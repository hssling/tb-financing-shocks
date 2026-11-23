"""Paper D, post hoc extension (analysis plan section 11).

Everything here is POST HOC: chosen after the letter was declined and after the
results of plan sections 9 and 10 were known. It describes the 2019-2024 fall
in spending per RR-TB patient in more detail, using the same WHO files, the
same balanced panels and the same deflator as src/d_regimen.py:

  (a) distribution of the per-country change, by WHO region and income group;
  (b) composition: drugs (exp_sld) against programme costs (exp_mdrmgt);
  (c) numbers started on treatment against total spending;
  (d) timing: share of the fall present by 2021 and by 2022.

Writes outputs/d_extend/results.json and outputs/d_extend/country_changes.csv.
Standard library only.
Usage: python -I src/d_extend.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d_regimen as d                    # noqa: E402

ROOT = d.ROOT
OUT = ROOT / "outputs" / "d_extend"
A, B = 2019, 2024
MIN_SUBGROUP = 5
PROC_RAW = "data/vintages/raw/gtbreport2026__finance__output__finance_imputed_constantus_included.rda"


# ---------------------------------------------------------------- inputs

def verify_inputs() -> None:
    """The public files (d_regimen) and the archive behind the processed file."""
    d.verify_inputs()
    with (d.PW / "data" / "vintages" / "vintage_manifest.csv").open(encoding="utf-8") as f:
        man = {r["local_path"]: r["sha256"] for r in csv.DictReader(f)}
    raw = d.PW / PROC_RAW
    assert man.get(PROC_RAW) == hashlib.sha256(raw.read_bytes()).hexdigest(), f"{PROC_RAW} differs from manifest"


@lru_cache(maxsize=None)
def income_groups() -> dict[str, str]:
    """World Bank income group for 2024 as assigned in WHO's processed finance file."""
    out = {}
    with d.PROC.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if int(r["year"]) == B and r.get("g_income") not in (None, "", "NA"):
                out[r["iso3"]] = r["g_income"]
    return out


@lru_cache(maxsize=None)
def regions() -> dict[str, str]:
    return {c: r["g_whoregion"] for (c, _), r in d.table(d.EXPEN).items() if r.get("g_whoregion")}


def amount(iso: str, y: int, col: str) -> float | None:
    """A reported amount; 0 is read as missing (the public file prints 0 for missing)."""
    v = d.num((d.table(d.EXPEN).get((iso, y)) or {}).get(col))
    return v if v and v > 0 else None


# ---------------------------------------------------------------- pure helpers

def summary(values: list[float]) -> dict:
    """n, median and inclusive quartiles of a list of changes (fractions)."""
    v = sorted(values)
    if not v:
        return {"n": 0, "median": None, "q1": None, "q3": None, "share_falling": None}
    q = statistics.quantiles(v, n=4, method="inclusive") if len(v) > 1 else [v[0]] * 3
    return {"n": len(v), "median": statistics.median(v), "q1": q[0], "q3": q[2],
            "share_falling": sum(1 for x in v if x < 0) / len(v)}


def by_group(rows: list[dict], key: str, value: str) -> dict:
    groups: dict[str, list[float]] = {}
    for r in rows:
        groups.setdefault(r.get(key) or "unclassified", []).append(r[value])
    return {g: {**summary(v), "interpreted": len(v) >= MIN_SUBGROUP} for g, v in sorted(groups.items())}


def quadrants(pairs: list[tuple[float, float]]) -> dict:
    """pairs of (change in spending per patient, change in patients started)."""
    return {"cost_down_patients_up": sum(1 for c, p in pairs if c < 0 and p > 0),
            "cost_down_patients_down": sum(1 for c, p in pairs if c < 0 and p <= 0),
            "cost_up_patients_up": sum(1 for c, p in pairs if c >= 0 and p > 0),
            "cost_up_patients_down": sum(1 for c, p in pairs if c >= 0 and p <= 0)}


def verdict(spend_change: float, patients_change: float) -> str:
    """Plan section 11(c): wording fixed before the result was seen."""
    if spend_change < 0 and patients_change <= 0:
        return "savings not visibly reinvested"
    if spend_change < 0:
        return "numbers treated rose while total spending fell"
    return "total spending rose"


def decomposition(drug: tuple[float, float], prog: tuple[float, float]) -> dict:
    """Pooled per-patient drug and programme spending in two years; the share of
    the change in their sum that comes from drugs."""
    dd, dp = drug[1] - drug[0], prog[1] - prog[0]
    tot = dd + dp
    return {"drug": drug, "programme": prog, "total": (drug[0] + prog[0], drug[1] + prog[1]),
            "change_drug": dd, "change_programme": dp, "change_total": tot,
            "relative_drug": drug[1] / drug[0] - 1, "relative_programme": prog[1] / prog[0] - 1,
            "relative_total": (drug[1] + prog[1]) / (drug[0] + prog[0]) - 1,
            "drug_share_of_change": dd / tot if tot else None,
            "mostly_drugs": bool(tot and dd / tot > 0.5)}


def log_change(a: float, b: float) -> float:
    return math.log(b) - math.log(a)


# ---------------------------------------------------------------- analyses

def real_factor(a: int = A, b: int = B) -> float:
    k = d.deflator()
    return k[b] / k[a]


def panel(which: str, a: int = A, b: int = B) -> dict[str, dict[int, float]]:
    """The balanced panel of plan section 9 (same construction as d_regimen.balanced)."""
    S = d.series(which)
    return {c: S[c] for c in S if not c.startswith("__") and a in S[c] and b in S[c]}


def distribution(which: str) -> tuple[dict, list[dict]]:
    P, f = panel(which), real_factor()
    rows = []
    for c, s in sorted(P.items()):
        rows.append({"iso3": c, "region": regions().get(c), "income": income_groups().get(c),
                     "change_real": s[B] / s[A] * f - 1, "change_current": s[B] / s[A] - 1})
    res = {"all_real": summary([r["change_real"] for r in rows]),
           "all_current": summary([r["change_current"] for r in rows]),
           "by_region": by_group(rows, "region", "change_real"),
           "by_income": by_group(rows, "income", "change_real"),
           "income_source": "g_income for 2024 in WHO's processed finance file (low- and middle-income only)",
           "check_median_matches_section_9": abs(statistics.median(r["change_real"] for r in rows) + 1
                                                 - d.balanced(which)["median_ratio_constant"]) < 1e-12}
    return res, rows


def programme_cut() -> float:
    """99th percentile of programme spending per patient started, pooled 2017-2024 (plan section 4 rule)."""
    v = []
    for (c, y) in d.table(d.EXPEN):
        if y in d.YEARS:
            s, m = d.started(c, y), amount(c, y, "exp_mdrmgt")
            if s and s >= d.MIN_STARTED and m:
                v.append(m / s)
    v.sort()
    return v[int(0.99 * (len(v) - 1))]


def composition() -> tuple[dict, list[dict]]:
    k, cut = d.deflator(), programme_cut()
    rows, excluded = [], []
    for c in sorted(panel("sld")):
        sld = {y: amount(c, y, "exp_sld") for y in (A, B)}
        mgt = {y: amount(c, y, "exp_mdrmgt") for y in (A, B)}
        st = {y: d.started(c, y) for y in (A, B)}
        if not all(mgt.values()):
            continue
        if any(mgt[y] / st[y] > cut for y in (A, B)):
            excluded.append(c)
            continue
        r = {"iso3": c, "started": st, "sld": sld, "mgt": mgt,
             "drug_share": {y: sld[y] / (sld[y] + mgt[y]) for y in (A, B)}}
        pp = lambda x, y: x[y] * k[y] / st[y]                       # real, per patient started
        r["change_drug"] = pp(sld, B) / pp(sld, A) - 1
        r["change_programme"] = pp(mgt, B) / pp(mgt, A) - 1
        r["change_total"] = (pp(sld, B) + pp(mgt, B)) / (pp(sld, A) + pp(mgt, A)) - 1
        rows.append(r)
    pooled = lambda col, y: sum(r[col][y] * k[y] for r in rows) / sum(r["started"][y] for r in rows)
    res = {"n": len(rows), "excluded_programme_p99": excluded, "programme_cut": cut,
           "drug_share_median": {y: statistics.median(r["drug_share"][y] for r in rows) for y in (A, B)},
           "change_drug": summary([r["change_drug"] for r in rows]),
           "change_programme": summary([r["change_programme"] for r in rows]),
           "change_total": summary([r["change_total"] for r in rows]),
           "pooled": decomposition((pooled("sld", A), pooled("sld", B)), (pooled("mgt", A), pooled("mgt", B)))}
    # consistency of the two drug measures, where a country is in both panels
    S, C, f = panel("sld"), panel("cpp"), real_factor()
    both = sorted(set(S) & set(C))
    xs = [log_change(S[c][A], S[c][B]) for c in both]
    ys = [log_change(C[c][A], C[c][B]) for c in both]
    res["two_drug_measures"] = {"n": len(both), "spearman": d.spearman(xs, ys) if len(both) > 3 else None,
                                "same_direction": sum(1 for x, y in zip(xs, ys) if (x < 0) == (y < 0)) / len(both)}
    return res, rows


def treated(which: str, a: int = A, b: int = B, comp_rows: list[dict] | None = None) -> dict:
    """Patients started and total spending in a panel, from year a to year b."""
    k, P = d.deflator(), panel(which, a, b)
    st = {y: sum(d.started(c, y) for c in P) for y in (a, b)}
    res = {"n": len(P), "started": st, "change_started": st[b] / st[a] - 1}
    pairs = []
    for c in P:
        pc = log_change(P[c][a] * k[a], P[c][b] * k[b])
        pairs.append((pc, log_change(d.started(c, a), d.started(c, b))))
    res["spearman_cost_vs_patients"] = d.spearman([x for x, _ in pairs], [y for _, y in pairs])
    res["quadrants"] = quadrants(pairs)
    res["patients_rose_share"] = sum(1 for _, y in pairs if y > 0) / len(pairs)
    if which == "sld":
        tot = {y: sum(P[c][y] * d.started(c, y) * k[y] for c in P) for y in (a, b)}
        res["total_real_sld"] = tot
        res["change_total_real_sld"] = tot[b] / tot[a] - 1
        res["change_pooled_per_patient"] = (tot[b] / st[b]) / (tot[a] / st[a]) - 1
        res["verdict"] = verdict(res["change_total_real_sld"], res["change_started"])
        # plan section 11, addendum: how far the totals rest on the two largest programmes
        top = sorted(P, key=lambda c: -d.started(c, a))[:2]
        rest = [c for c in P if c not in top]
        st_r = {y: sum(d.started(c, y) for c in rest) for y in (a, b)}
        tot_r = {y: sum(P[c][y] * d.started(c, y) * k[y] for c in rest) for y in (a, b)}
        res["largest_two"] = {"iso3": top, "share_started": 1 - st_r[a] / st[a],
                              "share_spending": 1 - tot_r[a] / tot[a],
                              "without": {"change_started": st_r[b] / st_r[a] - 1,
                                          "change_total_real_sld": tot_r[b] / tot_r[a] - 1,
                                          "verdict": verdict(tot_r[b] / tot_r[a] - 1, st_r[b] / st_r[a] - 1)}}
    if comp_rows is not None:
        tot = {y: sum((r["sld"][y] + r["mgt"][y]) * k[y] for r in comp_rows) for y in (a, b)}
        cst = {y: sum(r["started"][y] for r in comp_rows) for y in (a, b)}
        res["composition_panel"] = {"n": len(comp_rows), "total_real_drug_and_programme": tot,
                                    "change_total": tot[b] / tot[a] - 1, "started": cst,
                                    "change_started": cst[b] / cst[a] - 1,
                                    "verdict": verdict(tot[b] / tot[a] - 1, cst[b] / cst[a] - 1)}
    return res


def timing(which: str) -> dict:
    m = d.panel_medians(which)
    drops = {y: m[y - 1] - m[y] for y in range(A + 1, B + 1)}
    S = d.series(which, constant=True)
    keep = {c for c in S if not c.startswith("__") and A in S[c] and B in S[c]}
    return {"medians": m,
            "share_by_2021": (m[A] - m[2021]) / (m[A] - m[B]),
            "share_by_2022": (m[A] - m[2022]) / (m[A] - m[B]),
            "largest_single_year_fall": max(drops, key=drops.get),
            "figure_panel_equals_balanced_panel": keep == set(panel(which))}


def results() -> tuple[dict, list[dict]]:
    verify_inputs()
    R: dict = {"label": "POST HOC (analysis plan section 11)", "years": [A, B],
               "deflator_factor_2019_to_2024": real_factor()}
    rows_by: dict[str, list[dict]] = {}
    for which in ("sld", "cpp"):
        R[which] = {}
        R[which]["distribution"], rows_by[which] = distribution(which)
        R[which]["timing"] = timing(which)
    R["composition"], comp_rows = composition()
    R["sld"]["treated"] = treated("sld", comp_rows=comp_rows)
    R["cpp"]["treated"] = treated("cpp")
    R["sld"]["treated_2020"] = treated("sld", 2020, B)
    R["cpp"]["treated_2020"] = treated("cpp", 2020, B)
    # one row per country in either panel
    comp = {r["iso3"]: r for r in comp_rows}
    S, C = panel("sld"), panel("cpp")
    k = d.deflator()
    table_rows = []
    for c in sorted(set(S) | set(C)):
        s = next((r for r in rows_by["sld"] if r["iso3"] == c), None)
        p = next((r for r in rows_by["cpp"] if r["iso3"] == c), None)
        table_rows.append({
            "iso3": c, "who_region": regions().get(c, ""), "income_group": income_groups().get(c, ""),
            "started_2019": d.started(c, A), "started_2024": d.started(c, B),
            "sld_per_patient_2019_real": round(S[c][A] * k[A], 2) if c in S else "",
            "sld_per_patient_2024_real": round(S[c][B] * k[B], 2) if c in S else "",
            "sld_change_real": round(s["change_real"], 4) if s else "",
            "cpp_change_real": round(p["change_real"], 4) if p else "",
            "programme_change_real": round(comp[c]["change_programme"], 4) if c in comp else "",
            "drug_share_2019": round(comp[c]["drug_share"][A], 4) if c in comp else "",
            "drug_share_2024": round(comp[c]["drug_share"][B], 4) if c in comp else ""})
    return R, table_rows


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return x


def write(R: dict, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(jsonable(R), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    with (OUT / "country_changes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    R, rows = results()
    write(R, rows)
    pc = lambda x: f"{100 * x:+.1f}%"
    print("POST HOC (plan section 11)")
    for which in ("sld", "cpp"):
        D = R[which]["distribution"]
        a = D["all_real"]
        print(f"\n== {which}: n {a['n']}, median {pc(a['median'])} (IQR {pc(a['q1'])} to {pc(a['q3'])}), "
              f"falling {100 * a['share_falling']:.1f}% real / {100 * D['all_current']['share_falling']:.1f}% current")
        for g, s in list(D["by_region"].items()) + list(D["by_income"].items()):
            print(f"   {g:<13} n {s['n']:>2} median {pc(s['median'])} IQR {pc(s['q1'])} to {pc(s['q3'])} "
                  f"falling {100 * s['share_falling']:.0f}%")
        t = R[which]["timing"]
        print(f"   timing: by 2021 {100 * t['share_by_2021']:.1f}%, by 2022 {100 * t['share_by_2022']:.1f}%, "
              f"largest fall in {t['largest_single_year_fall']}; figure panel = balanced: "
              f"{t['figure_panel_equals_balanced_panel']}")
        for key in ("treated", "treated_2020"):
            T = R[which][key]
            extra = (f"; total real SLD {pc(T['change_total_real_sld'])}, pooled per patient "
                     f"{pc(T['change_pooled_per_patient'])}; {T['verdict']}") if which == "sld" else ""
            print(f"   {key}: n {T['n']}, started {T['started']} ({pc(T['change_started'])}); rose in "
                  f"{100 * T['patients_rose_share']:.0f}%; Spearman {T['spearman_cost_vs_patients']:+.2f}; "
                  f"{T['quadrants']}{extra}")
    C = R["composition"]
    print(f"\n== composition: n {C['n']} (excluded p99 {C['excluded_programme_p99']}); drug share median "
          f"{C['drug_share_median']}; drug {pc(C['change_drug']['median'])}, programme "
          f"{pc(C['change_programme']['median'])}, total {pc(C['change_total']['median'])}")
    print(f"   pooled {C['pooled']}")
    print(f"   two drug measures {C['two_drug_measures']}")
    print(f"   composition panel {R['sld']['treated']['composition_panel']}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

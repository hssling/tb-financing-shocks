"""Paper C: what replaced US government TB funding in 2025?

Implements docs/analysis_plan_C.md exactly. Standard library only.

Inputs are read from the companion provenance project, where they are archived
(public WHO file) or fetched at pinned commits (WHO's processed file); each is
checked against its recorded SHA-256 before use.

Usage: python -I src/c_usaid.py
"""
from __future__ import annotations

import csv
import hashlib
import statistics
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PW = ROOT.parent / "provenance_weighting"
PUBLIC = PW / "data" / "TB_expenditure_utilisation_2026-08-25.csv"
PUBLIC_SHA = "manifest"                       # read from the companion manifest
PROC_RDA = PW / "data" / "vintages" / "raw" / \
    "gtbreport2026__finance__output__finance_imputed_constantus_included.rda"
PROC_CSV = PW / "data" / "vintages" / "csv" / \
    "gtbreport2026__finance__output__finance_imputed_constantus_included__finance_merged.csv"
OUT = ROOT / "outputs"

SOURCES = ["domestic", "gf", "usaid", "grnt"]       # rcvd_tot_<source>
LABEL = {"domestic": "Domestic", "gf": "Global Fund", "usaid": "USAID", "grnt": "Other grants"}
IDENTITY_TOL = 0.01


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_inputs() -> None:
    man = {r["local_path"]: r["sha256"] for r in
           csv.DictReader((PW / "data" / "raw_file_manifest.csv").open(encoding="utf-8"))}
    want = man.get("data/TB_expenditure_utilisation_2026-08-25.csv")
    assert want and sha256(PUBLIC) == want, "public expenditure file differs from its manifest digest"
    vman = {r["local_path"]: r["sha256"] for r in
            csv.DictReader((PW / "data" / "vintages" / "vintage_manifest.csv").open(encoding="utf-8"))}
    rel = PROC_RDA.relative_to(PW).as_posix()
    assert vman.get(rel) and sha256(PROC_RDA) == vman[rel], "WHO processed file differs from its digest"


def num(s: str | None) -> float | None:
    if s is None or s.strip() in ("", "NA"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


@lru_cache(maxsize=None)
def public() -> dict[tuple[str, int], dict]:
    out = {}
    with PUBLIC.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rec = {s: num(r.get(f"rcvd_tot_{s}")) for s in SOURCES}
            rec["total"] = num(r.get("rcvd_tot"))
            rec["country"] = r["country"]
            out[(r["iso3"], int(r["year"]))] = rec
    return out


@lru_cache(maxsize=None)
def processed() -> dict[tuple[str, int], dict]:
    out = {}
    with PROC_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[(r["iso3"], int(r["year"]))] = r
    return out


def complete(rec: dict | None, blank_grants_ok: bool = False) -> bool:
    """All four sources and the total reported, and the sources sum to it.
    blank_grants_ok (post-hoc sensitivity, analysis plan section 8): a blank
    "other grants" counts as zero when the other three sources already sum to
    the total within tolerance, so the total itself confirms it."""
    if rec and blank_grants_ok and rec["grnt"] is None and rec["total"] is not None             and all(rec[s] is not None for s in ("domestic", "gf", "usaid")):
        rec = {**rec, "grnt": 0.0}
    if not rec or rec["total"] is None or any(rec[s] is None for s in SOURCES):
        return False
    if rec["total"] == 0:
        return sum(rec[s] for s in SOURCES) == 0
    return abs(sum(rec[s] for s in SOURCES) - rec["total"]) <= IDENTITY_TOL * rec["total"]


def reported(iso3: str, year: int) -> bool:
    lab = (processed().get((iso3, year)) or {}).get("rcvd_imputation", "")
    return lab == "Reported data"


def populations(require_reported: bool = True, blank_grants_ok: bool = False) -> dict[str, list[str]]:
    P = public()
    isos = sorted({c for c, _ in P})
    usaid, comparison, excluded = [], [], []
    for c in isos:
        r23, r24, r25 = P.get((c, 2023)), P.get((c, 2024)), P.get((c, 2025))
        had = r24 is not None and (r24["usaid"] or 0) > 0
        both = complete(r24, blank_grants_ok) and complete(r25, blank_grants_ok)
        prov = (reported(c, 2024) and reported(c, 2025)) if require_reported else True
        if had:
            (usaid if both and prov else excluded).append(c)
        elif both and prov and all((x is None or (x["usaid"] or 0) == 0) for x in (r23, r24, r25)):
            comparison.append(c)
    return {"usaid": usaid, "comparison": comparison, "excluded": excluded}


def country_rows(require_reported: bool = True, blank_grants_ok: bool = False) -> list[dict]:
    P = public()
    rows = []
    fill = lambda r: {**r, "grnt": 0.0} if blank_grants_ok and r["grnt"] is None else r
    for c in populations(require_reported, blank_grants_ok)["usaid"]:
        a, b = fill(P[(c, 2024)]), fill(P[(c, 2025)])
        d = {s: b[s] - a[s] for s in SOURCES}
        dt = b["total"] - a["total"]
        offset = (d["domestic"] + d["gf"] + d["grnt"]) / -d["usaid"] if d["usaid"] < 0 else None
        if d["usaid"] >= 0:
            cls = "USAID did not fall"
        elif dt >= 0:
            cls = "fully offset"
        elif dt > d["usaid"]:
            cls = "partly offset"
        else:
            cls = "not offset"
        r23 = P.get((c, 2023))
        trend = (b["domestic"] - a["domestic"]) - (a["domestic"] - r23["domestic"]) \
            if r23 and r23["domestic"] is not None else None
        rows.append({"iso3": c, "country": a["country"],
                     **{f"{s}_2024": a[s] for s in SOURCES}, **{f"{s}_2025": b[s] for s in SOURCES},
                     "total_2024": a["total"], "total_2025": b["total"],
                     **{f"d_{s}": d[s] for s in SOURCES}, "d_total": dt,
                     "offset_ratio": offset, "class": cls, "domestic_beyond_trend": trend})
    return rows


def pct_change(a: float | None, b: float | None) -> float | None:
    return (b - a) / a if a and b is not None else None


def difference_in_changes() -> dict:
    """Median proportional change in domestic funding, USAID vs comparison
    countries, 2024-2025 and (placebo) 2023-2024."""
    P = public()
    pops = populations()
    out = {}
    for label, (y0, y1) in (("2024-2025", (2024, 2025)), ("2023-2024 (placebo)", (2023, 2024))):
        res = {}
        for g in ("usaid", "comparison"):
            ch = [pct_change((P.get((c, y0)) or {}).get("domestic"), (P.get((c, y1)) or {}).get("domestic"))
                  for c in pops[g]]
            ch = [x for x in ch if x is not None]
            res[g] = {"n": len(ch), "median": statistics.median(ch) if ch else None}
        out[label] = res
    return out


def expected_2026(isos: list[str]) -> dict:
    Pp = processed()
    u = sum(num((Pp.get((c, 2026)) or {}).get("cf_tot_usaid")) or 0.0 for c in isos)
    d = sum(num((Pp.get((c, 2026)) or {}).get("cf_tot_domestic")) or 0.0 for c in isos)
    n = sum(1 for c in isos if (c, 2026) in Pp)
    return {"countries_in_file": n, "usaid_expected": u, "domestic_expected": d}


def summary(rows: list[dict], exclude: tuple[str, ...] = ()) -> dict:
    sel = [r for r in rows if r["iso3"] not in exclude]
    s = {k: sum(r[k] for r in sel) for k in
         ("usaid_2024", "usaid_2025", "domestic_2024", "domestic_2025", "gf_2024", "gf_2025",
          "grnt_2024", "grnt_2025", "total_2024", "total_2025")}
    s["n"] = len(sel)
    s["classes"] = {k: sum(1 for r in sel if r["class"] == k) for k in
                    ("fully offset", "partly offset", "not offset", "USAID did not fall")}
    ratios = [r["offset_ratio"] for r in sel if r["offset_ratio"] is not None]
    s["median_offset"] = statistics.median(ratios) if ratios else None
    s["usaid_fell_by_half"] = sum(1 for r in sel if r["usaid_2025"] < 0.5 * r["usaid_2024"])
    return s


def results() -> dict:
    verify_inputs()
    rows = country_rows()
    pops = populations()
    return {
        "populations": pops,
        "rows": rows,
        "all": summary(rows),
        "without_india": summary(rows, ("IND",)),
        "dic": difference_in_changes(),
        "expected_2026": expected_2026(pops["usaid"]),
        "sensitivity_any_label": summary(country_rows(require_reported=False)),
        "posthoc_blank_grants_rows": country_rows(blank_grants_ok=True),
        "posthoc_blank_grants": summary(country_rows(blank_grants_ok=True)),
        "posthoc_blank_grants_without_india": summary(country_rows(blank_grants_ok=True), ("IND",)),
    }


def main() -> int:
    R = results()
    m = lambda x: f"US$ {x / 1e6:,.1f} m"
    p = R["populations"]
    print(f"Population: {len(p['usaid'])} countries with USAID funding in 2024 and complete, reported "
          f"data for 2024 and 2025; {len(p['excluded'])} excluded ({', '.join(p['excluded'])}); "
          f"{len(p['comparison'])} comparison countries")
    for label in ("all", "without_india"):
        s = R[label]
        print(f"\n[{label}] n={s['n']}")
        for src in ("usaid", "domestic", "gf", "grnt", "total"):
            print(f"   {src:<9} {m(s[f'{src}_2024'])} -> {m(s[f'{src}_2025'])}")
        print(f"   classes: {s['classes']}; median offset ratio "
              f"{s['median_offset'] if s['median_offset'] is None else round(s['median_offset'], 2)}; "
              f"USAID fell by more than half in {s['usaid_fell_by_half']}")
    print("\nCountry rows (US$ m): USAID 24->25, domestic 24->25, total change, class")
    for r in sorted(R["rows"], key=lambda r: r["d_usaid"]):
        print(f"   {r['iso3']} {r['usaid_2024']/1e6:7.1f} -> {r['usaid_2025']/1e6:6.1f} | "
              f"{r['domestic_2024']/1e6:8.1f} -> {r['domestic_2025']/1e6:8.1f} | "
              f"{r['d_total']/1e6:+8.1f} | {r['class']}")
    print("\nDifference in changes (median proportional change in domestic):", R["dic"])
    print("Expected 2026:", {k: (round(v / 1e6, 1) if isinstance(v, float) else v)
                             for k, v in R["expected_2026"].items()})
    print("Sensitivity, any provenance label:", R["sensitivity_any_label"]["n"], "countries,",
          R["sensitivity_any_label"]["classes"])
    for label in ("posthoc_blank_grants", "posthoc_blank_grants_without_india"):
        s = R[label]
        print(f"\n[{label}] n={s['n']}: USAID {m(s['usaid_2024'])} -> {m(s['usaid_2025'])}; domestic "
              f"{m(s['domestic_2024'])} -> {m(s['domestic_2025'])}; GF {m(s['gf_2024'])} -> {m(s['gf_2025'])}; "
              f"total {m(s['total_2024'])} -> {m(s['total_2025'])}; classes {s['classes']}; median offset "
              f"{None if s['median_offset'] is None else round(s['median_offset'], 2)}")
    added = sorted({r["iso3"] for r in R["posthoc_blank_grants_rows"]} - {r["iso3"] for r in R["rows"]})
    for r in R["posthoc_blank_grants_rows"]:
        if r["iso3"] in added:
            print(f"   + {r['iso3']} USAID {r['usaid_2024']/1e6:.1f} -> {r['usaid_2025']/1e6:.1f}; domestic "
                  f"{r['domestic_2024']/1e6:.1f} -> {r['domestic_2025']/1e6:.1f}; total {r['d_total']/1e6:+.1f}; {r['class']}")
    OUT.mkdir(exist_ok=True)
    with (OUT / "c_country_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(R["rows"][0]))
        w.writeheader()
        w.writerows(R["rows"])
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

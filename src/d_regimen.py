"""Paper D: did shorter all-oral regimens lower spending per RR-TB patient?

Implements docs/analysis_plan_D.md exactly. Standard library only.
Usage: python -I src/d_regimen.py
"""
from __future__ import annotations

import csv
import hashlib
import math
import random
import statistics
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PW = ROOT.parent / "provenance_weighting"
NOTIF = PW / "data" / "TB_notifications_2026-08-25.csv"
EXPEN = PW / "data" / "TB_expenditure_utilisation_2026-08-25.csv"
PROC = PW / "data" / "vintages" / "csv" / \
    "gtbreport2026__finance__output__finance_imputed_constantus_included__finance_merged.csv"

BASELINE, ADOPTION, PLACEBO_PRE = (2019, 2020, 2021), (2023, 2024), (2017, 2018)
YEARS = range(2017, 2025)
MIN_STARTED = 20
HIGH = 0.25
NON_GDF = ("CHN", "IND", "RUS", "ZAF")
SEED, PERMS = 20261115, 10_000


def num(s):
    if s is None or str(s).strip() in ("", "NA"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def verify_inputs() -> None:
    man = {r["local_path"]: r["sha256"] for r in
           csv.DictReader((PW / "data" / "raw_file_manifest.csv").open(encoding="utf-8"))}
    for p in (NOTIF, EXPEN):
        rel = p.relative_to(PW).as_posix()
        assert man.get(rel) == hashlib.sha256(p.read_bytes()).hexdigest(), f"{rel} differs from manifest"


@lru_cache(maxsize=None)
def table(path: Path) -> dict[tuple[str, int], dict]:
    with path.open(encoding="utf-8-sig") as f:
        return {(r["iso3"], int(r["year"])): r for r in csv.DictReader(f)}


def started(iso: str, y: int) -> float | None:
    r = table(NOTIF).get((iso, y))
    if not r:
        return None
    cols = (("conf_rrmdr_tx", "unconf_rrmdr_tx") if y <= 2019
            else ("conf_rr_nfqr_tx", "unconf_rr_nfqr_tx", "conf_rr_fqr_tx"))
    vals = [num(r.get(c)) for c in cols]
    if vals[0] is None:                       # the confirmed count is required
        return None
    return sum(v for v in vals if v is not None)


def join_test() -> dict:
    """Section 3: the 2019 and 2020 definitions should give similar totals."""
    ratios = []
    for (iso, y) in table(NOTIF):
        if y == 2019:
            a, b = started(iso, 2019), started(iso, 2020)
            if a and b and a >= MIN_STARTED:
                ratios.append(b / a)
    return {"countries": len(ratios), "median_ratio_2020_to_2019": statistics.median(ratios)}


def outcome(iso: str, y: int, which: str) -> float | None:
    e = table(EXPEN).get((iso, y)) or {}
    s = started(iso, y)
    if s is None or s < MIN_STARTED:
        return None
    if which == "sld":
        v = num(e.get("exp_sld"))
        return v / s if v and v > 0 else None
    v = num(e.get("exp_cpp_mdr"))
    return v if v and v > 0 else None


def exposure(iso: str, key: str = "mdrxdr_bpalm_tx") -> float | None:
    shares = []
    for y in (2022, 2023):
        r = table(NOTIF).get((iso, y)) or {}
        s, b = started(iso, y), num(r.get(key))
        if b is not None and s:
            shares.append(min(b / s, 1.0))
        elif key == "mdrxdr_bpalm_tx" and num(r.get("mdrxdr_bpalm_used")) == 0 and s:
            shares.append(0.0)
    return statistics.mean(shares) if shares else None


def klass(x: float | None, high: float = HIGH) -> str | None:
    if x is None:
        return None
    return "high" if x >= high else "low" if x > 0 else "non"


def deflator() -> dict[int, float]:
    """US GDP deflator per year from WHO's processed file; restates in 2024 dollars."""
    vals = {}
    with PROC.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            d = num(r.get("imf_deflator_us"))
            if d:
                vals.setdefault(int(r["year"]), d)
    return {y: vals[2024] / vals[y] for y in YEARS}


def series(which: str, constant: bool = False, drop_restated: bool = False) -> dict[str, dict[int, float]]:
    k = deflator() if constant else {y: 1.0 for y in YEARS}
    out: dict[str, dict[int, float]] = {}
    isos = sorted({c for c, _ in table(EXPEN)})
    for iso in isos:
        for y in YEARS:
            v = outcome(iso, y, which)
            if v is None:
                continue
            if drop_restated:
                col = "exp_sld" if which == "sld" else "exp_cpp_mdr"
                a = num((table(EXPEN).get((iso, y)) or {}).get(col))
                b = num((table(EXPEN).get((iso, y - 1)) or {}).get(col))
                if a and b and a == b:
                    continue
            out.setdefault(iso, {})[y] = v * k[y]
    # implausible values: above the pooled 99th percentile
    pooled = sorted(v for d in out.values() for v in d.values())
    cut = pooled[int(0.99 * (len(pooled) - 1))]
    flagged = [(c, y) for c, d in out.items() for y, v in d.items() if v > cut]
    for c, y in flagged:
        del out[c][y]
    out["__flagged__"] = {i: 0.0 for i in range(len(flagged))}
    series.flagged = flagged          # type: ignore[attr-defined]
    return out


def change(d: dict[int, float], pre: tuple, post: tuple, min_pre: int = 2, min_post: int = 1) -> float | None:
    a = [d[y] for y in pre if y in d]
    b = [d[y] for y in post if y in d]
    if len(a) < min_pre or len(b) < min_post:
        return None
    return math.log(statistics.mean(b)) - math.log(statistics.mean(a))


def spearman(x: list[float], y: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num_ = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num_ / den if den else float("nan")


def compare(which: str, pre=BASELINE, post=ADOPTION, high=HIGH, exclude=(), constant=False,
            drop_restated=False, min_pre=2) -> dict:
    S = series(which, constant, drop_restated)
    rows = []
    for iso, d in S.items():
        if iso.startswith("__") or iso in exclude:
            continue
        x = exposure(iso)
        c = klass(x, high)
        ch = change(d, pre, post, min_pre=min_pre)
        if c is None or ch is None:
            continue
        rows.append({"iso3": iso, "exposure": x, "class": c, "dlog": ch})
    hi = [r["dlog"] for r in rows if r["class"] == "high"]
    no = [r["dlog"] for r in rows if r["class"] == "non"]
    res = {"n_high": len(hi), "n_low": sum(1 for r in rows if r["class"] == "low"), "n_non": len(no),
           "median_high": statistics.median(hi) if hi else None,
           "median_non": statistics.median(no) if no else None, "rows": rows}
    if hi and no:
        obs = statistics.median(hi) - statistics.median(no)
        rng = random.Random(SEED)
        pool, k, extreme = hi + no, len(hi), 0
        for _ in range(PERMS):
            rng.shuffle(pool)
            if abs(statistics.median(pool[:k]) - statistics.median(pool[k:])) >= abs(obs) - 1e-12:
                extreme += 1
        res.update({"diff": obs, "p": (extreme + 1) / (PERMS + 1)})
    xs = [r["exposure"] for r in rows]
    ys = [r["dlog"] for r in rows]
    res["spearman"] = spearman(xs, ys) if len(rows) > 3 else None
    return res


def descriptive(which: str) -> dict[int, dict]:
    S = series(which)
    out = {}
    for y in YEARS:
        by = {"all": [], "high": [], "low": [], "non": []}
        for iso, d in S.items():
            if iso.startswith("__") or y not in d:
                continue
            by["all"].append(d[y])
            c = klass(exposure(iso))
            if c:
                by[c].append(d[y])
        out[y] = {k: (len(v), statistics.median(v) if v else None) for k, v in by.items()}
    return out


def results() -> dict:
    verify_inputs()
    R = {"join": join_test()}
    for which in ("sld", "cpp"):
        R[which] = {
            "primary": compare(which),
            "placebo": compare(which, pre=PLACEBO_PRE, post=BASELINE),
            "non_gdf_excluded": compare(which, exclude=NON_GDF),
            "constant": compare(which, constant=True),
            "no_restated": compare(which, drop_restated=True),
            "threshold_10": compare(which, high=0.10),
            "threshold_50": compare(which, high=0.50),
            "descriptive": descriptive(which),
        }
        R[which]["flagged"] = list(series.flagged)      # type: ignore[attr-defined]
    return R


def fmt(r: dict) -> str:
    if r.get("diff") is None:
        return f"n high {r['n_high']}, non {r['n_non']}: not estimable"
    pc = lambda x: f"{100 * (math.exp(x) - 1):+.1f}%"
    return (f"high {r['n_high']} (median {pc(r['median_high'])}), low {r['n_low']}, non {r['n_non']} "
            f"(median {pc(r['median_non'])}); difference {r['diff']:+.3f} log points, permutation "
            f"p = {r['p']:.3f}; Spearman {r['spearman']:+.2f}")


def main() -> int:
    R = results()
    print("Join test 2019->2020:", R["join"])
    for which, label in (("sld", "Outcome 1: second-line drug expenditure per patient started"),
                         ("cpp", "Outcome 2: reported expenditure per MDR patient")):
        print(f"\n== {label}")
        for k in ("primary", "placebo", "non_gdf_excluded", "constant", "no_restated",
                  "threshold_10", "threshold_50"):
            print(f"   {k:<18} {fmt(R[which][k])}")
        print("   flagged >p99:", R[which]["flagged"])
        print("   median by year (n, median US$) all | high | non:")
        for y, d in R[which]["descriptive"].items():
            f = lambda t: f"{t[0]:>3} {t[1]:>9,.0f}" if t[1] else f"{t[0]:>3}       -"
            print(f"     {y}: {f(d['all'])} | {f(d['high'])} | {f(d['non'])}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

"""Render paper C's tables from src/c_usaid.py, never by hand.

Writes manuscript/tables_c.md; the manuscript carries the same blocks and
verification/check_c.py fails if they differ from a fresh rendering.
Usage: python -I manuscript/make_c_exhibits.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import c_usaid as c                                              # noqa: E402

OUT = ROOT / "manuscript" / "tables_c.md"


def m(x: float) -> str:
    return f"{x / 1e6:,.1f}"


def signed(x: float) -> str:
    return f"{x / 1e6:+,.1f}".replace("-", "−")


def table1(R: dict) -> str:
    primary = {r["iso3"] for r in R["rows"]}
    rows = sorted(R["posthoc_blank_grants_rows"], key=lambda r: r["d_usaid"])
    out = ["**Table 1. Change in national TB programme funding received, by source, 2024 to 2025, in "
           "countries that received USAID TB funding in 2024.** US$ million, current prices.", "",
           "| Country | USAID 2024 | USAID 2025 | Change: USAID | Domestic | Global Fund | Other grants | "
           "Total | Offset of USAID change |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        name = r["country"] + ("" if r["iso3"] in primary else "ᵃ")
        out.append(f"| {name} | {m(r['usaid_2024'])} | {m(r['usaid_2025'])} | {signed(r['d_usaid'])} | "
                   f"{signed(r['d_domestic'])} | {signed(r['d_gf'])} | {signed(r['d_grnt'])} | "
                   f"{signed(r['d_total'])} | {r['class']} |")
    out += ["", "*Change is the 2025 value minus the 2024 value. Fully offset: total funding did not fall. "
            "Partly offset: total fell by less than USAID. Not offset: total fell by at least as much as "
            "USAID. ᵃ Admitted in the post-hoc analysis only: \"other grants\" was blank in one year and the "
            "other three sources sum to the reported total, which confirms it was zero. Source: WHO Global "
            "TB Programme, funding received as reported by national programmes, release of 25 August 2026.*"]
    return "\n".join(out)


def table2(R: dict) -> str:
    def line(label: str, s: dict) -> str:
        cl = s["classes"]
        return (f"| {label} | {s['n']} | {m(s['usaid_2024'])} → {m(s['usaid_2025'])} | "
                f"{m(s['domestic_2024'])} → {m(s['domestic_2025'])} | {m(s['gf_2024'])} → {m(s['gf_2025'])} | "
                f"{m(s['total_2024'])} → {m(s['total_2025'])} | {cl['fully offset']} / {cl['partly offset']} / "
                f"{cl['not offset']} / {cl['USAID did not fall']} |")
    out = ["**Table 2. Totals and classification in the primary population and in sensitivity analyses.** "
           "US$ million.", "",
           "| Analysis | Countries | USAID 2024 → 2025 | Domestic 2024 → 2025 | Global Fund 2024 → 2025 | "
           "Total 2024 → 2025 | Fully / partly / not offset / USAID did not fall |",
           "|---|---:|---|---|---|---|---|",
           line("Primary: complete, reported data", R["all"]),
           line("Primary, excluding India", R["without_india"]),
           line("Constant 2025 US$", R["sensitivity_constant"]),
           line("Excluding possibly restated values", R["sensitivity_no_restated"]),
           line("Post hoc: blank other grants confirmed zero", R["posthoc_blank_grants"])]
    d = R["dic"]
    out += ["", f"*Difference in changes: the median proportional change in domestic funding was "
            f"{100 * d['2024-2025']['usaid']['median']:.1f}% in the {d['2024-2025']['usaid']['n']} USAID "
            f"countries and {100 * d['2024-2025']['comparison']['median']:.1f}% in "
            f"{d['2024-2025']['comparison']['n']} countries without USAID funding between 2024 and 2025, "
            f"against {100 * d['2023-2024 (placebo)']['usaid']['median']:.1f}% and "
            f"{100 * d['2023-2024 (placebo)']['comparison']['median']:.1f}% between 2023 and 2024. "
            f"Constant dollars: 2024 amounts restated with the US GDP deflator carried in WHO's processed "
            f"file (factor {R['deflator_factor']:.3f}).*"]
    return "\n".join(out)


def render() -> dict[str, str]:
    R = c.results()
    return {"Table 1": table1(R), "Table 2": table2(R)}


# --- sentences that name countries (RECORD item 13.1: exclusions and reasons) ---
NUMBER = "zero one two three four five six seven eight nine ten eleven twelve".split()
THE = ("Central African Republic", "Democratic Republic", "United Republic", "Republic of", "Syrian Arab",
       "Lao People", "Congo", "Philippines")


def the(name: str) -> str:
    return f"the {name}" if name.startswith(THE) else name


def series(names: list[str]) -> str:
    names = [the(n) for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def reason_phrase(reasons: list[tuple[int, str]], iso3: str) -> str:
    """Plain-language reason, built only from the failing conditions the code found.
    The 'reported data' label is mentioned only when nothing else failed."""
    core = [(y, r) for y, r in reasons if r != "label"] or reasons
    years = lambda code: sorted({y for y, r in core if r == code})
    yrs = lambda ys: " and ".join(str(y) for y in ys)
    parts = []
    if years("no record"):
        parts.append(f"had no record for {yrs(years('no record'))}")
    if years("nothing by source"):
        parts.append(f"reported no funding by source for {yrs(years('nothing by source'))}")
    for s in c.SOURCES:
        if years(f"blank:{s}"):
            label = "other grants" if s == "grnt" else f"{c.LABEL[s]} funding"
            parts.append(f"left {label} blank for {yrs(years(f'blank:{s}'))}")
    if years("total missing"):
        parts.append(f"left the total blank for {yrs(years('total missing'))}")
    if years("sum"):
        parts.append(f"reported sources that did not sum to the total for {yrs(years('sum'))}")
    if years("total printed as zero"):
        y = years("total printed as zero")[0]
        rec = c.public()[(iso3, y)]
        given = sum(rec[s] or 0 for s in c.SOURCES)
        parts.append(f"printed a {y} total of zero although its sources sum to US$ {given / 1e6:,.1f} million")
    if years("label"):
        parts.append(f"was not labelled by WHO as reported data for {yrs(years('label'))}")
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def sentences() -> dict[str, str]:
    R = c.results()
    P = c.public()
    name = lambda iso: P[(iso, 2024)]["country"]
    admitted = {r["iso3"] for r in R["posthoc_blank_grants_rows"]}
    others = [iso for iso in R["populations"]["excluded"] if iso not in admitted]
    groups: dict[str, list[str]] = {}
    for iso in sorted(others, key=name):
        groups.setdefault(reason_phrase(R["exclusion_reasons"][iso], iso), []).append(name(iso))
    clauses = [f"{series(n)} {p}" for p, n in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[1][0]))]
    excl = (f"Of the {NUMBER[len(others)]} excluded for other reasons, "
            + ("; ".join(clauses[:-1]) + "; and " + clauses[-1] if len(clauses) > 1 else clauses[0]) + ".")
    comp = "The comparison countries were " + series(sorted((name(i) for i in R["populations"]["comparison"]),
                                                             key=lambda n: n.removeprefix("the "))) + "."
    return {"exclusions": excl, "comparison": comp}


def main() -> int:
    b = render()
    OUT.write_text("\n\n".join(b.values()) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

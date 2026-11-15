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


def main() -> int:
    b = render()
    OUT.write_text("\n\n".join(b.values()) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

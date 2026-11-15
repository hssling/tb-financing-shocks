"""Paper C, Figure 1: change in funding by source, as a share of each country's
2024 total, so that India's scale does not flatten every other country.

matplotlib is used here only; the analysis (src/) is standard library.
Usage: python manuscript/make_c_figure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import c_usaid as c                       # noqa: E402

OUT = ROOT / "manuscript" / "figure_c1_change_by_source.png"
DPI = 400
SRC = [("usaid", "USAID", "#c05621", "//"), ("gf", "Global Fund", "#8c8c8c", "xx"),
       ("grnt", "Other grants", "#d9a441", ".."), ("domestic", "Domestic", "#2b6cb0", None)]


def main() -> int:
    R = c.results()
    primary = {r["iso3"] for r in R["rows"]}
    rows = sorted(R["posthoc_blank_grants_rows"], key=lambda r: r["d_usaid"], reverse=True)
    plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(12, 9), layout="constrained")
    for i, r in enumerate(rows):
        base = r["total_2024"]
        pos = neg = 0.0
        for key, lab, col, hatch in SRC:
            v = 100 * r[f"d_{key}"] / base
            left = pos if v >= 0 else neg + v
            ax.barh(i, v, left=pos if v >= 0 else neg, color="white" if hatch else col,
                    edgecolor=col, hatch=hatch, linewidth=1.3, height=0.7,
                    label=lab if i == 0 else None, zorder=2)
            if v >= 0:
                pos += v
            else:
                neg += v
        net = 100 * r["d_total"] / base
        ax.plot([net], [i], marker="D", color="black", markersize=7, zorder=4,
                label="Net change in total" if i == 0 else None)
    names = [r["country"].replace("Democratic Republic of the Congo", "DR Congo")
             .replace("United Republic of Tanzania", "Tanzania") + ("" if r["iso3"] in primary else " (a)")
             for r in rows]
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(names, fontsize=13)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Change 2024 to 2025, % of the country's 2024 TB programme funding", fontsize=13)
    ax.grid(axis="x", color="#e6e6e6", zorder=0)
    ax.legend(frameon=False, fontsize=12.5, loc="lower right")
    fig.savefig(OUT, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Paper D (letter), Figure 1: spending per RR-TB patient, 2017-2024, in the
balanced panel of countries reporting in both 2019 and 2024, constant 2024 US$.

matplotlib is used here only; the analysis (src/) is standard library.
Usage: python manuscript/make_d_figure.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import d_regimen as d                     # noqa: E402

OUT = ROOT / "manuscript" / "figure_d1_spending_per_patient.png"


def panel(which: str) -> tuple[list[int], list[float], int]:
    S = d.series(which, constant=True)
    keep = [c for c in S if not c.startswith("__") and 2019 in S[c] and 2024 in S[c]]
    ys, meds = [], []
    for y in d.YEARS:
        v = [S[c][y] for c in keep if y in S[c]]
        if v:
            ys.append(y); meds.append(statistics.median(v))
    return ys, meds, len(keep)


def main() -> int:
    plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(10, 5.8), layout="constrained")
    # shaded: the period after WHO recommended BPaLM (December 2022)
    ax.axvspan(2022.96, 2024.5, color="#eeeeee", zorder=0)
    ax.text(2024.1, 0.03, "after WHO's\nBPaLM\nguideline", transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", fontsize=11, color="#444444")
    for which, lab, col, mk in (("sld", "Second-line drug expenditure per patient started", "#2b6cb0", "o"),
                                ("cpp", "Reported expenditure per MDR-TB patient treated", "#c05621", "s")):
        ys, meds, n = panel(which)
        ax.plot(ys, meds, marker=mk, color=col, linewidth=2.2, markersize=7,
                label=f"{lab} (n = {n})", zorder=3)
    for x, txt, ha, dx, yy in ((2022.96, "pretomanid\nprice cut,\nDec 2022", "right", -0.05, 0.97),
                               (2023.66, "bedaquiline\nprice cut,\nAug 2023", "left", 0.05, 0.97)):
        ax.axvline(x, color="#666666", linestyle=":", linewidth=1.4, zorder=1)
        ax.text(x + dx, yy, txt, transform=ax.get_xaxis_transform(), ha=ha, va="top",
                fontsize=11, color="#444444")
    ax.set_xlim(2016.6, 2024.9)
    ax.set_xticks(list(d.YEARS))
    ax.set_ylabel("Median, constant 2024 US$ per patient")
    ax.set_ylim(0, None)
    ax.grid(axis="y", color="#e6e6e6", zorder=0)
    ax.legend(frameon=False, fontsize=11.5, loc="lower left", bbox_to_anchor=(0, 0.12))
    fig.savefig(OUT, dpi=400, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Paper D, version 3 exhibits (post hoc extension, analysis plan section 11).

Figure 1, two panels:
  A  median spending per patient, 2017-2024, constant 2024 US$, in the
     balanced panels (as the earlier figure);
  B  per country, 2019 to 2024: real change in second-line drug spending per
     patient started against the change in the number started.
Table 1: the per-country real change, 2019 to 2024, by WHO region and income group.

Reads outputs/d_extend/results.json and country_changes.csv (run src/d_extend.py
first). matplotlib is used here only.
Usage: python -I manuscript/make_d_extend_exhibits.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "outputs" / "d_extend"
FIG = ROOT / "manuscript" / "figure_d_v3_1.png"
TAB = ROOT / "manuscript" / "table_d3_1.md"
BLUE, ORANGE, INK, MUTED = "#2b6cb0", "#c05621", "#333333", "#666666"
REGIONS = (("AFR", "African Region"), ("AMR", "Region of the Americas"), ("EMR", "Eastern Mediterranean Region"),
           ("EUR", "European Region"), ("SEA", "South-East Asia Region"), ("WPR", "Western Pacific Region"))
INCOME = (("LIC", "Low income"), ("LMC", "Lower-middle income"), ("UMC", "Upper-middle income"))


def pct(x: float) -> str:
    return f"{100 * x:+.1f}".replace("-", "−")


def cell(s: dict) -> str:
    return f"{s['n']} | {pct(s['median'])} ({pct(s['q1'])} to {pct(s['q3'])})"


def table(R: dict) -> str:
    s, c = R["sld"]["distribution"], R["cpp"]["distribution"]
    lines = ["**Table 1.** Real change (%) in drug spending per patient, 2019 to 2024, by country group: "
             "median (interquartile range) across countries (post hoc).", "",
             "| Country group | n | Second-line drug spending per patient started | n | "
             "Reported drug cost per patient starting MDR-TB treatment |",
             "|---|---|---|---|---|",
             f"| All countries | {cell(s['all_real'])} | {cell(c['all_real'])} |"]
    for k, lab in REGIONS:
        lines.append(f"| WHO {lab} | {cell(s['by_region'][k])} | {cell(c['by_region'][k])} |")
    for k, lab in INCOME:
        lines.append(f"| {lab} | {cell(s['by_income'][k])} | {cell(c['by_income'][k])} |")
    n_unc = c["by_income"].get("unclassified", {}).get("n", 0) + s["by_income"].get("unclassified", {}).get("n", 0)
    lines += ["", f"Constant 2024 US dollars. Income groups as assigned in WHO's processed finance file, which "
                  f"holds no high-income countries; {("no", "one", "two")[n_unc]} country without a group is counted in all countries "
                  f"only. MDR-TB = multidrug-resistant tuberculosis."]
    return "\n".join(lines) + "\n"


def main() -> int:
    R = json.loads((RES / "results.json").read_text(encoding="utf-8"))
    with (RES / "country_changes.csv").open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["sld_change_real"]]
    plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), layout="constrained", width_ratios=(1.1, 1))

    # A: medians by year
    a.axvspan(2022.96, 2024.5, color="#eeeeee", zorder=0)
    a.text(2023.75, 0.03, "after WHO's\nBPaLM\nguideline", transform=a.get_xaxis_transform(),
           ha="center", va="bottom", fontsize=10, color=MUTED)
    for which, lab, col, mk in (("sld", "Second-line drug spending\nper patient started", BLUE, "o"),
                                ("cpp", "Reported drug cost per patient\nstarting MDR-TB treatment", ORANGE, "s")):
        m = {int(y): v for y, v in R[which]["timing"]["medians"].items()}
        ys = sorted(m)
        n = R[which]["distribution"]["all_real"]["n"]
        a.plot(ys, [m[y] for y in ys], marker=mk, color=col, linewidth=2, markersize=7,
               label=f"{lab} (n = {n})", zorder=3)
    a.set_xlim(2016.6, 2024.6)
    a.set_xticks(range(2017, 2025))
    a.tick_params(axis="x", labelsize=10)
    a.set_ylim(0, None)
    a.set_ylabel("Median, constant 2024 US$")
    a.grid(axis="y", color="#e6e6e6", zorder=0)
    a.legend(frameon=False, fontsize=10, loc="lower left")
    a.set_title("A  Median per patient, 2017–2024", loc="left", fontsize=12, color=INK)

    # B: per country, change in spending per patient against change in patients started
    x = [math.log2(1 + float(r["sld_change_real"])) for r in rows]
    y = [math.log2(float(r["started_2024"]) / float(r["started_2019"])) for r in rows]
    b.axvline(0, color=MUTED, linewidth=1, zorder=1)
    b.axhline(0, color=MUTED, linewidth=1, zorder=1)
    lo, hi = math.log2(1 / 128), math.log2(16)
    inside = [(v, w) for v, w in zip(x, y) if lo <= v <= hi]
    clipped = [(min(max(v, lo), hi), w) for v, w in zip(x, y) if not lo <= v <= hi]
    b.scatter([v for v, _ in inside], [w for _, w in inside], s=46, color=BLUE, edgecolor="white",
              linewidth=1.2, zorder=3)
    if clipped:
        b.scatter([v for v, _ in clipped], [w for _, w in clipped], s=60, marker="D", facecolor="white",
                  edgecolor=BLUE, linewidth=1.5, zorder=3)      # explained in the figure legend
    q = R["sld"]["treated"]["quadrants"]
    for (qx, qy, ha, va), k in (((0.02, 0.98, "left", "top"), "cost_down_patients_up"),
                                ((0.02, 0.02, "left", "bottom"), "cost_down_patients_down"),
                                ((0.98, 0.98, "right", "top"), "cost_up_patients_up"),
                                ((0.98, 0.02, "right", "bottom"), "cost_up_patients_down")):
        b.text(qx, qy, f"{q[k]} countries", transform=b.transAxes, ha=ha, va=va, fontsize=10, color=MUTED)
    xt = [1 / 64, 1 / 8, 1 / 2, 1, 4, 16]
    yt = [1 / 4, 1 / 2, 1, 2, 4]
    lab = lambda r: "0" if r == 1 else f"{100 * (r - 1):+.0f}%".replace("-", "−")
    b.set_xticks([math.log2(v) for v in xt], [lab(v) for v in xt], fontsize=10)
    b.set_yticks([math.log2(v) for v in yt], [lab(v) for v in yt], fontsize=10)
    b.set_xlim(lo - 0.3, hi + 0.3)
    b.set_ylim(math.log2(1 / 5), math.log2(5))
    b.set_xlabel("Real change in second-line drug spending per patient started")
    b.set_ylabel("Change in number started on treatment")
    b.set_title(f"B  Per country, 2019 to 2024 (n = {len(rows)})", loc="left", fontsize=12, color=INK)

    fig.savefig(FIG, dpi=400, facecolor="white")
    plt.close(fig)
    assert all(math.log2(1 / 5) <= w <= math.log2(5) for w in y), "a country outside the y axis"
    assert len(inside) + len(clipped) == len(rows)
    TAB.write_text(table(R), encoding="utf-8")
    print(f"wrote {FIG.relative_to(ROOT)} and {TAB.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

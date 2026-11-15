"""Verify paper D (IJTLD letter) against src/d_regimen.py.

1. Every derived number the letter states equals what the code computes now.
2. References numbered 1..n, all cited, in order of first citation; at most 15.
3. Letter text at most 1,100 words (IJTLD Letter).

Usage: python -I verification/check_d.py ; exit 1 on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import d_regimen as d                 # noqa: E402

PAPER = ROOT / "manuscript" / "paper_d_letter.md"
WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
         "fifteen sixteen seventeen eighteen nineteen twenty").split()


def main() -> int:
    t = PAPER.read_text(encoding="utf-8")
    errs: list[str] = []
    R = d.results()
    s, c, a = R["sld"]["balanced"], R["cpp"]["balanced"], R["adoption"]
    pc = lambda r: f"{100 * (1 - r):.1f}%"
    want = {
        "BPaL reporting": f"with {a['reporting'][2022]} and {a['reporting'][2023]} countries reporting",
        "2024 not counted": "and not for 2024" if a["reporting"][2024] == 0 else "(2024 now counted)",
        "lt12 2025": f"reported by {a['lt12_2025']} countries",
        "share >=25": f"{WORDS[a['share_ge_25']].capitalize()} countries reached a 25% share",
        "analysable": f"only {WORDS[min(R['sld']['primary']['n_high'], R['cpp']['primary']['n_high'])]} to "
                      f"{WORDS[max(R['sld']['primary']['n_high'], R['cpp']['primary']['n_high'])]} of them",
        "sld n": f"Among the {s['n']} countries reporting second-line drug expenditure",
        "sld fall": f"the median fell by {pc(s['median_ratio'])} ({pc(s['median_ratio_constant'])} in constant",
        "sld share falling": f"it fell in {100 * s['share_falling']:.1f}% of countries",
        "cpp n": f"Among the {c['n']} countries reporting expenditure per MDR-TB patient",
        "cpp fall": f"it fell by {pc(c['median_ratio'])} ({pc(c['median_ratio_constant'])})",
        "cpp share falling": f"in {100 * c['share_falling']:.1f}% of countries",
        "sld by 2021": f"{100 * R['sld']['fall_by_2021']:.1f}% of the 2019–2024 fall",
        "cpp by 2021": f"{100 * R['cpp']['fall_by_2021']:.1f}% of the fall in expenditure per patient treated",
        "join": f"was {R['join']['median_ratio_2020_to_2019']:.2f} across {R['join']['countries']} countries",
        "figure n": f"among the {s['n']} countries reporting each measure" if s["n"] == c["n"] else "(n differ)",
    }
    for label, w in want.items():
        if w not in t:
            errs.append(f"text: expected {label} as {w!r}")

    i = t.index("## References"); j = t.index("\n## ", i + 5)
    listed = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", t[i:j])]
    if listed != list(range(1, len(listed) + 1)) or len(listed) > 15:
        errs.append(f"reference list {listed} (IJTLD Letter: at most 15)")
    order: list[int] = []
    for m in re.finditer(r"\((\d+(?:\s*[,–-]\s*\d+)*)\)", t[t.index("## Letter"):i]):
        for part in m.group(1).split(","):
            rng = [int(x) for x in re.split(r"[–-]", part)]
            for n in range(rng[0], rng[-1] + 1):
                if n <= len(listed) and n not in order:
                    order.append(n)
    if sorted(order) != listed:
        errs.append(f"cited {sorted(order)} vs listed {listed}")
    if order != sorted(order):
        errs.append(f"references not in order of first citation: {order}")

    letter = t[t.index("Dear Editor"):t.index("**Funding.**")]
    nwords = len(re.sub(r"\*\*|`|#", "", letter).split())
    if nwords > 1100:
        errs.append(f"letter {nwords} words > 1,100")

    if errs:
        print(f"FAILED: {len(errs)} problem(s)\n  " + "\n  ".join(errs))
        return 1
    print(f"PASSED: {len(want)} derived numbers match the code; {len(listed)} references cited in "
          f"order; letter {nwords} words")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

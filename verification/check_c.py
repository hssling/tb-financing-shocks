"""Verify paper C against the code that produced it.

1. Tables 1-2 in the manuscript equal a fresh rendering (make_c_exhibits.py).
2. Every derived number the text states equals what src/c_usaid.py computes now.
3. References are numbered 1..n, all cited, in order of first citation.
4. Abstract <= 250 words, main text <= 3,000 (Bulletin of the WHO, Research).

Usage: python -I verification/check_c.py ; exit 1 on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "manuscript"))
import c_usaid as c                   # noqa: E402
import make_c_exhibits as mx          # noqa: E402

PAPER = ROOT / "manuscript" / "manuscript_c.md"
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def money(x: float) -> str:
    return f"US$ {x / 1e6:,.1f} million"


def main() -> int:
    t = PAPER.read_text(encoding="utf-8")
    errs: list[str] = []
    R = c.results()

    # 1. tables
    for name, block in mx.render().items():
        if block not in t:
            errs.append(f"{name}: differs from a fresh rendering; rerun make_c_exhibits.py and paste it")

    # 2. prose numbers
    a, w, ph = R["all"], R["without_india"], R["posthoc_blank_grants"]
    pops = R["populations"]
    n_had = len(pops["usaid"]) + len(pops["excluded"])
    rows = {r["iso3"]: r for r in R["rows"]}
    ng = rows["NGA"]
    P = c.processed(); Q = c.public()
    blank_only = sum(1 for iso in pops["excluded"]
                     if iso in {r["iso3"] for r in R["posthoc_blank_grants_rows"]})
    fell = sum(1 for r in R["rows"] if r["d_usaid"] < 0)
    d = R["dic"]
    exp = lambda iso: money(c.num(P[(iso, 2026)]["cf_tot_usaid"]))
    want = {
        "population": f"{WORDS[len(pops['usaid'])].capitalize()} of {n_had} countries met",
        "USAID": f"from {money(a['usaid_2024'])} to {money(a['usaid_2025'])}",
        "Global Fund": f"from {money(a['gf_2024'])} to {money(a['gf_2025'])}",
        "domestic": f"from {money(a['domestic_2024'])} to {money(a['domestic_2025'])}",
        "total": f"from {money(a['total_2024'])} to {money(a['total_2025'])}",
        "without India": f"from {money(w['domestic_2024'])} to {money(w['domestic_2025'])}",
        "fell by half": f"by more than half in {WORDS[a['usaid_fell_by_half']]}",
        "fully offset": f"{WORDS[a['classes']['fully offset']].capitalize()} countries fully offset",
        "rose": f"in {WORDS[a['classes']['USAID did not fall']]} countries USAID funding rose",
        "median USAID": f"{100 * d['2024-2025']['usaid']['median']:.1f}% in the USAID countries",
        "median comparison": f"{100 * d['2024-2025']['comparison']['median']:.1f}% in countries without",
        "placebo": f"it was {100 * d['2023-2024 (placebo)']['usaid']['median']:.1f}% and "
                   f"{100 * d['2023-2024 (placebo)']['comparison']['median']:.1f}%",
        "Nigeria USAID": f"lost {money(-ng['d_usaid'])} from USAID and {money(-ng['d_gf'])} from the Global Fund",
        "Nigeria domestic": f"domestic funding rose by {money(ng['d_domestic'])}",
        "Nigeria total": f"total funding fell by {money(-ng['d_total'])}",
        "blank-only exclusions": f"{WORDS[blank_only]} of the twelve excluded failed only because",
        "post hoc": f"gave {ph['n']} countries, of which {WORDS[ph['classes']['fully offset']]} fully offset, "
                    f"{WORDS[ph['classes']['partly offset']]} partly offset and "
                    f"{WORDS[ph['classes']['not offset']]} did not",
        "nine whose USAID fell": f"in {WORDS[a['classes']['fully offset']]} of the {WORDS[fell]} whose USAID funding fell",
        "Kyrgyzstan zero total": f"sources sum to {money(sum(Q[('KGZ', 2025)][s] or 0 for s in c.SOURCES))}"
                                 if (Q[('KGZ', 2025)]['total'] == 0) else "(Kyrgyzstan total no longer zero)",
        "Indonesia 2026":f"Indonesia expected {exp('IDN')} after receiving {money(Q[('IDN', 2025)]['usaid'])}",
        "Nigeria 2026": f"Nigeria {exp('NGA')} after {money(Q[('NGA', 2025)]['usaid'])}",
        "comparison size": f"{WORDS[len(pops['comparison'])].capitalize() if len(pops['comparison']) < 13 else 'Twenty-three'} countries met the conditions for the comparison group, "
                           f"{d['2024-2025']['comparison']['n']} of them",
    }
    for label, s in want.items():
        if s.replace("US$ ", "US$ ") not in t:
            errs.append(f"text: expected {label} as {s!r}")

    # 2a. the public README quotes the same headline numbers; they must match too.
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for label in ("USAID", "Global Fund", "domestic"):
        s = want[label].replace(" million to ", " million to ")
        # README wraps lines; compare with whitespace collapsed
        if " ".join(s.split()) not in " ".join(readme.split()):
            errs.append(f"README: expected {label} as {s!r}")

    # 2b. every number in the abstract must be supported by the body or tables.
    # A mutation test changed 40.3% in the abstract alone and the checks above
    # passed, because they look at body sentences.
    ab_text = t[t.index("## Abstract"):t.index("**Keywords")]
    body_text = t[t.index("## Introduction"):t.index("## References")]
    for num_ in re.findall(r"(?<![\w.])\d[\d,]*\.\d+|(?<![\w.])\d{2,}(?![\w.,])", ab_text):
        if num_ not in body_text:
            errs.append(f"abstract states {num_}, which the body and tables do not")

    # 3. references
    i = t.index("## References"); j = t.index("\n## ", i + 5)
    listed = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", t[i:j])]
    if listed != list(range(1, len(listed) + 1)):
        errs.append(f"reference list numbered {listed}")
    order: list[int] = []
    for m in re.finditer(r"\((\d+(?:\s*[,–-]\s*\d+)*)\)", t[:i] + t[j:]):
        for part in m.group(1).split(","):
            if "–" in part or "-" in part:
                lo, hi = (int(x) for x in re.split(r"[–-]", part))
                nums = range(lo, hi + 1)
            else:
                nums = [int(part)]
            for n in nums:
                if n not in order:
                    order.append(n)
    order = [n for n in order if n <= len(listed)]
    if sorted(set(order)) != listed:
        errs.append(f"cited {sorted(set(order))} vs listed 1..{len(listed)}")
    if order != sorted(order):
        errs.append(f"references not in order of first citation: {order}")

    # 4. limits
    def count(x: str) -> int:
        x = re.sub(r"(?m)^\|.*$|^\*\*Table \d+\..*$|^\*[^*].*\*$", "", x)
        return len(re.sub(r"\*\*|`|#", "", x).split())
    ab = count(t[t.index("## Abstract") + 11:t.index("**Keywords")])
    body = count(t[t.index("## Introduction"):t.index("## Acknowledgements")])
    if ab > 250:
        errs.append(f"abstract {ab} words > 250")
    if body > 3000:
        errs.append(f"main text {body} words > 3000")

    if errs:
        print(f"FAILED: {len(errs)} problem(s)\n  " + "\n  ".join(errs))
        return 1
    print(f"PASSED: tables match the code; {len(want)} derived numbers in the text match; "
          f"{len(listed)} references cited in order; abstract {ab} words, main text {body} words")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

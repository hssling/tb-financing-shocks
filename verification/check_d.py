"""Verify paper D (IJTLD letter) against src/d_regimen.py.

1. Every derived number the letter states equals what the code computes now.
2. References numbered 1..n, all cited, in order of first citation; at most 15.
3. Letter text at most 1,100 words (IJTLD Letter).
4. IJTLD form: superscript citations; title <= 110 characters without
   abbreviations; running head <= 45 characters; 3-5 keywords, none in the
   title; first author and "et al." when there are more than three authors;
   an ethics statement; the built Word file embeds the figure and carries
   line numbers.

Usage: python -I verification/check_d.py ; exit 1 on any failure.
"""
from __future__ import annotations

import math
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
    pct = lambda dlog: f"{100 * (math.exp(dlog) - 1):+.1f}%".replace("-", "−").replace("+", "+")
    want = {
        "BPaL reporting": f"with {a['reporting'][2022]} and {a['reporting'][2023]} countries reporting",
        "six-month reporting": f"reported by {a['six_reporting'][2024]} countries for 2024 and "
                               f"{a['six_reporting'][2025]} for 2025",
        "six-month >=25": f"{a['six_ge_25_2024']} of the {a['six_with_share_2024']} countries with a share reached 25%",
        "six sld": (lambda r: f"changed by {pct(r['median_high'])} in {r['n_high']} high adopters and "
                              f"{pct(r['median_non'])} in {r['n_non']} non-adopters (permutation p = {r['p']:.2f})")
                   (R["sld"]["six_2024"]),
        "six cpp": (lambda r: f"by {pct(r['median_high'])} in {r['n_high']} high adopters and "
                              f"{pct(r['median_non'])} in {r['n_non']} non-adopters (p = {r['p']:.2f})")
                   (R["cpp"]["six_2024"]),
        "placebo direction": "adopters' spending had risen relative to non-adopters'"
                             if R["sld"]["six_2024_placebo"]["diff"] > 0 and R["cpp"]["six_2024_placebo"]["diff"] > 0
                             else "(placebo direction changed)",
        "share >=25": f"{WORDS[a['share_ge_25']]} countries reached a 25% share",
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
    if re.search(r"\((\d+(?:\s*[,–-]\s*\d+)*)\)", t[t.index("Dear Editor"):i]):
        errs.append("bracketed citation found; IJTLD uses superscript numbers")
    for m in re.finditer(r"\^(\d+(?:[,–-]\d+)*)\^", t[t.index("Dear Editor"):i]):
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
    nwords = len(re.sub(r"\*\*|`|#|\^[\d,–-]+\^", "", letter).split())
    if nwords > 1100:
        errs.append(f"letter {nwords} words > 1,100")

    # 4. IJTLD form
    title = t.splitlines()[0].lstrip("# ").strip()
    if len(title) > 110:
        errs.append(f"title {len(title)} characters > 110")
    if re.search(r"\b[A-Z]{2,}\b|\b[A-Z][a-z]*[A-Z]", title):
        errs.append(f"title contains an abbreviation: {title!r}")
    head = re.search(r"(?m)^\*\*Running head:\*\* (.*)$", t).group(1).strip()
    if len(head) > 45:
        errs.append(f"running head {len(head)} characters > 45")
    kws = [k.strip() for k in re.search(r"(?m)^\*\*Keywords:\*\* (.*)$", t).group(1).split(";")]
    if not 3 <= len(kws) <= 5:
        errs.append(f"{len(kws)} keywords; IJTLD asks for 3-5")
    for k in kws:
        if k.lower() in title.lower():
            errs.append(f"keyword {k!r} appears in the title")
    for n_, e in re.findall(r"(?m)^(\d+)\. (.*)$", t[i:j]):
        names = re.match(r"^((?:[A-Z][\w'-]+(?: [A-Z][\w'-]+)* [A-Z]{1,3}, )*[A-Z][\w'-]+(?: [A-Z][\w'-]+)* [A-Z]{1,3})[.,]", e)
        if names and names.group(1).count(",") + 1 > 3:
            errs.append(f"reference {n_}: more than three authors listed; use the first and et al.")
        if re.search(r"\bdoi:", e):
            errs.append(f"reference {n_}: IJTLD article references carry no DOI")
    if not re.search(r"Ethical approval was not required", t):
        errs.append("no ethics statement")
    docx = ROOT / "submission" / "paper_d" / "03_letter.docx"
    if docx.exists():
        import zipfile
        with zipfile.ZipFile(docx) as z:
            names_ = z.namelist(); doc = z.read("word/document.xml").decode("utf-8")
        if not any(x.startswith("word/media/") for x in names_):
            errs.append("built letter does not embed the figure")
        if "lnNumType" not in doc:
            errs.append("built letter has no line numbering")
        if not re.search(r'<w:vertAlign w:val="superscript"\s*/>', doc):
            errs.append("built letter has no superscript citations")
        if docx.stat().st_mtime < PAPER.stat().st_mtime:
            errs.append("built letter is older than the source; rerun submission/build_d.py")
    else:
        errs.append("submission/paper_d/03_letter.docx not built")
    cover = ROOT / "submission" / "paper_d" / "02_cover_letter.md"
    if cover.exists():
        cl = cover.read_text(encoding="utf-8")
        if f'"{title}"' not in cl:
            errs.append("cover letter does not carry the manuscript title")
        if f"({nwords:,} words, {len(listed)} references, one figure)" not in cl:
            errs.append(f"cover letter counts differ from the letter ({nwords} words, {len(listed)} references)")

    if errs:
        print(f"FAILED: {len(errs)} problem(s)\n  " + "\n  ".join(errs))
        return 1
    print(f"PASSED: {len(want)} derived numbers match the code; {len(listed)} references cited in "
          f"order; letter {nwords} words; title {len(title)} characters; running head {len(head)}; "
          f"{len(kws)} keywords; IJTLD form checked in the source and the built Word file")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

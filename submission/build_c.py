"""Build paper C's upload set for the Bulletin of the WHO.

From manuscript/manuscript_c.md, writes into submission/paper_c/:
  03_manuscript_blinded.md   author block and self-citation names removed
  04_manuscript.md           with author details; the Bulletin does not state
                             its review model, so both are provided
  06_Figure_1.png            from manuscript/figure_c1_change_by_source.png
and stamps derived counts into 01_title_page.md. Every .md becomes .docx via
pandoc, with tables given journal rules by the companion project's styler.

Rules carried over from the companion project, each learned the hard way:
counts are derived, never typed; author-only text never reaches an upload;
reference numbers are literal text (Word once renumbered a list-numbered
reference list from 1 on the third entry).

Usage: python -I submission/build_c.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "manuscript" / "manuscript_c.md"
OUT = ROOT / "submission" / "paper_c"
FIG = ROOT / "manuscript" / "figure_c1_change_by_source.png"
sys.path.insert(0, str(ROOT.parent / "provenance_weighting" / "manuscript"))
import style_docx_tables as styler           # noqa: E402

AUTHOR_ONLY = [r"\*\*Target journal:\*\*", r"Notes for the author", r"not for submission"]
LEAKS = ["Siddalingaiah", "hssling", "ORCID", "Shridevi", "0000-0002", "zenodo.", "HSS "]


def count_words(text: str) -> int:
    text = re.sub(r"(?m)^\|.*$|^\*\*Table \d+\..*$|^\[Table \d+ about here\]$", "", text)
    text = re.sub(r"(?m)^\*[^*].*\*$", "", text)            # table notes
    return len(re.sub(r"\*\*|`|#", "", text).split())


def for_submission(t: str) -> str:
    t = re.sub(r"(?m)^\*\*Target journal:\*\*.*\n?", "", t)
    i = t.find("## Notes for the author")
    if i != -1:
        t = t[:i].rstrip().rstrip("-").rstrip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", t)


def blind(t: str) -> str:
    for pat in (r"(?m)^\*\*Author:\*\*.*\n", r"(?m)^Department of Community Medicine.*\n",
                r"(?m)^Correspondence:.*\n"):
        t, n = re.subn(pat, "", t)
        assert n == 1, f"blinding pattern did not match exactly once: {pat}"
    t = t.replace("Siddalingaiah HS.", "[Author].")
    # the contributions statement names the author by initials
    t, n = re.subn(r"(## Author contributions\n\n).*\n", r"\1[Withheld for blind review.]\n", t)
    assert n == 1, "author contributions section not found exactly once"
    # The archive DOI resolves to a record naming the author, and the
    # repository URL carries the author's username: both withheld when blind.
    t = re.sub(r"doi:10\.5281/zenodo\.\d+", "[archive DOI withheld for blind review]", t)
    t = re.sub(r"https://github\.com/hssling/[A-Za-z0-9_.-]+", "[repository withheld for blind review]", t)
    for leak in LEAKS:
        assert leak not in t, f"blinded copy still contains {leak!r}"
    return t


def tables_to_end(t: str) -> tuple[str, int]:
    """Lift each table (caption, rows, italic note) to a Tables section after
    the reference list, leaving a placement marker."""
    lines, out, blocks, i = t.split("\n"), [], [], 0
    while i < len(lines):
        m = re.match(r"^\*\*Table (\d+)\.", lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        block = [lines[i]]; i += 1; seen = False
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("|"):
                seen = True
            elif ln.strip() == "" or (seen and ln.startswith("*") and not ln.startswith("**")):
                pass
            else:
                break
            block.append(ln); i += 1
        while block and not block[-1].strip():
            block.pop()
        blocks.append("\n".join(block))
        out += [f"[Table {m.group(1)} about here]", ""]
    text = "\n".join(out)
    k = text.index("## Figure captions")
    return text[:k] + "## Tables\n\n" + "\n\n".join(blocks) + "\n\n" + text[k:], len(blocks)


def literal_refs(t: str) -> str:
    i = t.index("## References"); j = t.index("\n## ", i + 5)
    out = []
    for ln in t[i:j].split("\n"):
        m = re.match(r"^(\d+)\. (.*)$", ln)
        out += ([f"{m.group(1)}\\. {m.group(2)}", ""] if m else ([ln, ""] if ln.strip() else []))
    return t[:i] + "\n".join(out).rstrip() + "\n" + t[j:]


def add_word_count(t: str, body: int) -> str:
    m = re.search(r"(?m)^\*\*Running title:\*\*.*$", t)
    return t[:m.end()] + f"\n\n**Word count:** {body:,} words (main text, Introduction to Discussion, " \
        "excluding abstract, tables, figure captions and references)" + t[m.end():]


def stamp(page: Path, counts: dict) -> None:
    s = page.read_text(encoding="utf-8")
    rows = [(r"(\| Abstract \(structured\) \| )[\d,]+( words \|)", counts["abstract"]),
            (r"(\| Main text,[^|]*\| )[\d,]+( words \|)", counts["body"]),
            (r"(\| Tables \| )\d+( \|)", counts["tables"]),
            (r"(\| Figures \| )\d+( \|)", counts["figures"]),
            (r"(\| References \| )\d+( \|)", counts["refs"])]
    for pat, v in rows:
        s, n = re.subn(pat, lambda m: f"{m.group(1)}{v:,}{m.group(2)}", s)
        assert n == 1, f"title page row not found: {pat}"
    page.write_text(s, encoding="utf-8")


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    counts = {
        "abstract": count_words(src[src.index("## Abstract") + 11:src.index("**Keywords")]),
        "body": count_words(src[src.index("## Introduction"):src.index("## Acknowledgements")]),
        "tables": len(re.findall(r"(?m)^\*\*Table \d+\.", src)),
        "figures": len(re.findall(r"(?m)^\*\*Fig\. \d+\.", src)),
        "refs": len(re.findall(r"(?m)^\d+\. ", src[src.index("## References"):src.index("## Figure captions")])),
    }
    sub = for_submission(src)
    sub, n_tab = tables_to_end(add_word_count(sub, counts["body"]))
    assert n_tab == counts["tables"]
    sub = literal_refs(sub)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "04_manuscript.md").write_text(sub, encoding="utf-8")
    (OUT / "03_manuscript_blinded.md").write_text(blind(sub), encoding="utf-8")
    stamp(OUT / "01_title_page.md", counts)
    assert counts["figures"] == 1 and FIG.exists()
    shutil.copyfile(FIG, OUT / "06_Figure_1.png")
    for f in sorted(OUT.glob("0[1-5]_*.md")):
        txt = f.read_text(encoding="utf-8")
        for pat in AUTHOR_ONLY:
            assert not re.search(pat, txt), f"{f.name}: author-only content {pat}"
    pandoc = shutil.which("pandoc")
    made = []
    if pandoc:
        for md in sorted(OUT.glob("*.md")):
            docx = md.with_suffix(".docx")
            r = subprocess.run([pandoc, str(md), "-f", "markdown+pipe_tables", "-o", str(docx),
                                "--standalone", "--wrap=none"], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            styler.process(docx)
            made.append(docx.name)
    print(f"counts {counts}; wrote {len(made)} .docx in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

"""Build the paper D letter's upload set for IJTLD.

IJTLD asks for a single Word document holding the title page, the text, the
references and the figure with its legend, at 1.5 or double spacing with
continuous line numbering. This script writes, into submission/paper_d/:

  03_letter.md / .docx   title page (with derived counts), page break, letter,
                         references, figure legend and the embedded figure;
                         1.5 line spacing and continuous line numbers
  04_Figure_1.png / .tif the figure again as image files (600 dpi TIFF), for
                         the portal's figure slot and for typesetting

The title page carries what IJTLD lists: title (<= 110 characters, no
abbreviations), author and affiliation, running head (<= 45 characters), word
count of the text, numbers of references, tables and figures, 3-5 keywords
that do not appear in the title, and the corresponding author's address and
contact details. Every count is derived here, never typed.

Usage: python -I submission/build_d.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "submission"))
import build_c as b                                   # noqa: E402

SRC = ROOT / "manuscript" / "paper_d_letter.md"
FIG = ROOT / "manuscript" / "figure_d1_spending_per_patient.png"
OUT = ROOT / "submission" / "paper_d"
PAGE_BREAK = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'


def field(t: str, name: str) -> str:
    m = re.search(rf"(?m)^\*\*{name}:\*\* (.*)$", t)
    assert m, f"{name} missing from the source"
    return m.group(1).strip()


def counts(t: str) -> dict:
    letter = t[t.index("Dear Editor"):t.index("**Funding.**")]
    i = t.index("## References"); j = t.index("\n## ", i + 5)
    return {"words": len(re.sub(r"\*\*|`|#|\^[\d,–-]+\^", "", letter).split()),
            "refs": len(re.findall(r"(?m)^\d+\. ", t[i:j])),
            "figures": len(re.findall(r"(?m)^\*\*Figure\.", t)),
            "tables": len(re.findall(r"(?m)^\*\*Table \d+\.", t))}


def title_page(t: str, n: dict) -> str:
    title = t.splitlines()[0].lstrip("# ").strip()
    author = re.search(r"(?m)^\*\*Author:\*\* (.*)\n(.*)$", t)
    return "\n".join([
        f"# {title}", "",
        f"**Article type:** Letter", "",
        f"**Author:** {author.group(1)}  ",
        author.group(2), "",
        f"**Running head:** {field(t, 'Running head')}", "",
        f"**Word count:** summary, none (Letters have no summary); text, {n['words']:,} words "
        "(excluding references and figure legend)", "",
        f"**References:** {n['refs']}; **Tables:** {n['tables']}; **Figures:** {n['figures']}", "",
        f"**Keywords:** {field(t, 'Keywords')}", "",
        f"**Corresponding author:** {field(t, 'Corresponding author')}", ""])


def line_numbers_and_spacing(docx: Path) -> None:
    """1.5 line spacing as the document default, and continuous line numbers."""
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                s = data.decode("utf-8")
                s, k = re.subn(r"<w:sectPr([^>]*)>",
                               r'<w:sectPr\1><w:lnNumType w:countBy="1" w:restart="continuous"/>', s)
                assert k >= 1, "no section properties found"
                data = s.encode("utf-8")
            elif item.filename == "word/styles.xml":
                s = data.decode("utf-8")
                # 1.5 lines (line="360" in 240ths) for the defaults and every paragraph style
                s, k = re.subn(r"(<w:pPrDefault>\s*<w:pPr>\s*)<w:spacing ([^>]*?)\s*/>",
                               r'\1<w:spacing \2 w:line="360" w:lineRule="auto"/>', s, count=1)
                assert k == 1, "could not set default spacing"
                s = re.sub(r'w:line="\d+" w:lineRule="auto"', 'w:line="360" w:lineRule="auto"', s)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(docx)


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    n = counts(src)
    sub = b.for_submission(src)
    # the letter itself: no section heading (IJTLD Letters have none) and no author block
    body = sub[sub.index("Dear Editor"):]
    body = b.literal_refs(body.replace("## Figure caption", "## Figure captions"))
    body = body.replace("## Figure captions", "## Figure legend")
    body = body.rstrip() + "\n\n![](04_Figure_1.png){width=6.3in}\n"
    t = title_page(src, n) + "\n" + PAGE_BREAK + "\n\n" + body
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "03_letter.md").write_text(t, encoding="utf-8")
    for f in sorted(OUT.glob("0*.md")):
        txt = f.read_text(encoding="utf-8")
        assert "Target journal" not in txt, f"{f.name}: author-only"
        assert "Notes for the author" not in txt and "not for submission" not in txt, f.name
    shutil.copyfile(FIG, OUT / "04_Figure_1.png")
    from PIL import Image
    with Image.open(FIG) as im:
        im.convert("RGB").save(OUT / "04_Figure_1.tif", dpi=(600, 600), compression="tiff_lzw")
    pandoc = shutil.which("pandoc")
    made = []
    if pandoc:
        for md in sorted(OUT.glob("*.md")):
            docx = md.with_suffix(".docx")
            r = subprocess.run([pandoc, str(md), "-f", "markdown+pipe_tables+superscript",
                                "-o", str(docx), "--standalone", "--wrap=none",
                                f"--resource-path={OUT}"], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            b.styler.process(docx)
            if md.name == "03_letter.md":
                line_numbers_and_spacing(docx)
            made.append(docx.name)
    print(f"counts {n}; wrote {made} and the figure in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

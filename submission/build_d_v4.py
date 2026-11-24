"""Build paper D's Short Communication upload set for The International Journal
of Health Planning and Management (Wiley; single-blind review, anonymised main
document).

Reads manuscript/paper_d_shortcomm_v4.md (the source, holding the title-page
fields, the text, the declarations, references, table and figure legend) and
manuscript/paper_d_shortcomm_v4_cover.md (the cover letter, with {title},
{main_words}, {abstract_words}, {keywords} and {refs} filled in here), and
writes into submission/paper_d_v4/:

  01_title_page.docx                       title, running title, author, affiliation,
                                           contact details, word counts, keywords,
                                           acknowledgements, funding, conflicts, author
                                           contributions, data availability, and the
                                           blinded reference in full
  02_main_document.docx                    anonymised: title, abstract and keywords,
                                           main text, data availability, references,
                                           table, figure legend; self-citations read
                                           "[reference blinded for review]" and links
                                           to the author's archive "[link blinded for
                                           review]"
  03_manuscript_with_author_details.docx   the same with the title-page fields and the
                                           declarations, not blinded
  04_Figure_1.tif                          600 dpi
  05_cover_letter.docx

The Markdown each Word file is made from is kept in submission/paper_d_v4/_md/.
Every count is derived here, never typed.

Usage: python -I submission/build_d_v4.py
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
import build_d as bd                                  # noqa: E402

SRC = ROOT / "manuscript" / "paper_d_shortcomm_v4.md"
COVER = ROOT / "manuscript" / "paper_d_shortcomm_v4_cover.md"
FIG = ROOT / "manuscript" / "figure_d_v3_1.png"
OUT = ROOT / "submission" / "paper_d_v4"
MD = OUT / "_md"
MAIN = ("Introduction", "Methods", "Results", "Discussion")
DECLARATIONS = ("Acknowledgements", "Funding", "Conflict of interest statement", "Author contributions")
SELF = "Siddalingaiah"
BLIND_REF = "[reference blinded for review]"
BLIND_LINK = "[link blinded for review]"
LINK = re.compile(r"https?://github\.com/hssling/[A-Za-z0-9_.-]*[A-Za-z0-9_-]"
                  r"|https?://doi\.org/10\.5281/zenodo\.\d+|doi:10\.5281/zenodo\.\d+")
# anything that identifies the author; none may remain in the main document
LEAKS = ("Siddalingaiah", "hssling", "Shridevi", "Tumkur", "ORCID", "0000-0002", "zenodo", "github",
         "8941087719", "Author contributions", "Acknowledgements")
PAGE_BREAK = bd.PAGE_BREAK


def field(t: str, name: str) -> str:
    return bd.field(t, name)


def title(t: str) -> str:
    return t.splitlines()[0].lstrip("# ").strip()


def sections(t: str) -> dict[str, str]:
    """Level-2 sections by heading, each with its subsections."""
    parts = re.split(r"(?m)^## (.+)$", t)
    return {parts[k].strip(): parts[k + 1].strip("\n") for k in range(1, len(parts), 2)}


def plain_words(s: str) -> int:
    s = "\n".join(ln for ln in s.splitlines() if not ln.lstrip().startswith("#"))
    s = re.sub(r"\^[\d,–-]+\^|\*\*|`", "", s)
    s = re.sub(r"(?m)^- ", "", s)
    return len(s.split())


def main_text(t: str) -> str:
    S = sections(t)
    return "\n\n".join(f"## {h}\n\n{S[h]}" for h in MAIN)


def counts(t: str) -> dict:
    S = sections(t)
    return {"abstract_words": plain_words(S["Abstract"]),
            "main_words": plain_words(main_text(t)),
            "refs": len(re.findall(r"(?m)^\d+\. ", S["References"])),
            "keywords": len(field(t, "Keywords").split(";")),
            "tables": len(re.findall(r"(?m)^\*\*Table \d+\.", t)),
            "figures": len(re.findall(r"(?m)^\*\*Figure \d+\.", t)),
            "title_chars": len(title(t)),
            "running_title_chars": len(field(t, "Running title"))}


def self_citations(t: str) -> dict[int, str]:
    refs = sections(t)["References"]
    return {int(n): e for n, e in re.findall(r"(?m)^(\d+)\. (.*)$", refs) if SELF in e}


def blind(md: str) -> str:
    """Self-citations and links to the author's archive withheld."""
    md = re.sub(rf"(?m)^(\d+)(\\?\.) .*{SELF}.*$", rf"\1\2 {BLIND_REF}", md)
    md = LINK.sub(BLIND_LINK, md)
    for leak in LEAKS:
        assert leak.lower() not in md.lower(), f"blinded document still contains {leak!r}"
    return md


def number_word(k: int) -> str:
    """Numbers under ten spelt out, as the journal asks."""
    return ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")[k] if k < 10 else str(k)


def word_counts_line(n: dict) -> str:
    return (f"**Word counts:** abstract {n['abstract_words']} words; main text (Introduction to Discussion, "
            f"headings excluded) {n['main_words']:,} words; {n['refs']} references; "
            f"{number_word(n['tables'])} table and {number_word(n['figures'])} figure; "
            f"{number_word(n['keywords'])} keywords")


def title_block(t: str, n: dict) -> str:
    return "\n".join([
        f"# {title(t)}", "",
        f"**Running title:** {field(t, 'Running title')}", "",
        f"**Article type:** {field(t, 'Article type')}", "",
        f"**Author:** {field(t, 'Author')}", "",
        f"**Affiliation:** {field(t, 'Affiliation')}", "",
        f"**Corresponding author:** {field(t, 'Corresponding author')}", "",
        word_counts_line(n), "",
        f"**Keywords:** {field(t, 'Keywords')}", ""])


def declarations(t: str) -> str:
    S = sections(t)
    return "\n".join(f"## {h}\n\n{S[h]}\n" for h in DECLARATIONS)


def body(t: str) -> str:
    """Abstract to figure legend, in the journal's order."""
    S = sections(t)
    return "\n".join([
        "## Abstract", "", S["Abstract"], "",
        f"**Keywords:** {field(t, 'Keywords')}", "",
        main_text(t), "",
        "## Data availability statement", "", S["Data availability statement"], "",
        "## References", "", S["References"], "",
        "## Table", "", S["Table"], "",
        "## Figure legend", "", S["Figure legend"], ""])


def title_page(t: str, n: dict) -> str:
    S = sections(t)
    blinded = self_citations(t)
    lines = [title_block(t, n), declarations(t),
             "## Data availability statement", "", S["Data availability statement"], "",
             "## Blinded reference", "",
             "The main document is anonymised: the reference below is cited there as "
             f"\"{BLIND_REF}\", with the same number.", ""]
    lines += [f"{k}\\. {e}" for k, e in sorted(blinded.items())]
    return "\n".join(lines) + "\n"


def cover_letter(t: str, n: dict) -> str:
    c = COVER.read_text(encoding="utf-8")
    for k, v in {"title": title(t), "main_words": f"{n['main_words']:,}",
                 "abstract_words": str(n["abstract_words"]), "keywords": number_word(n["keywords"]),
                 "refs": str(n["refs"])}.items():
        c = c.replace("{" + k + "}", v)
    assert "{" not in c, "unfilled field in the cover letter"
    return c


def scrub_properties(docx: Path) -> None:
    """No author or editor names in the document properties."""
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                s = data.decode("utf-8")
                for tag in ("dc:creator", "cp:lastModifiedBy", "dc:title"):
                    s = re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}></{tag}>", s, flags=re.S)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(docx)


def render(md: Path, docx: Path, numbered: bool) -> None:
    pandoc = shutil.which("pandoc")
    assert pandoc, "pandoc not found"
    r = subprocess.run([pandoc, str(md), "-f", "markdown+pipe_tables+superscript", "-o", str(docx),
                        "--standalone", "--wrap=none"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    b.styler.process(docx)
    if numbered:
        bd.line_numbers_and_spacing(docx)
    scrub_properties(docx)


def main() -> int:
    t = SRC.read_text(encoding="utf-8")
    n = counts(t)
    MD.mkdir(parents=True, exist_ok=True)
    docs = {
        "01_title_page": (title_page(t, n), False),
        "02_main_document": (blind(f"# {title(t)}\n\n" + b.literal_refs(body(t))), True),
        "03_manuscript_with_author_details": (title_block(t, n) + "\n" + declarations(t) + "\n" + PAGE_BREAK
                                              + "\n\n" + b.literal_refs(body(t)), True),
        "05_cover_letter": (cover_letter(t, n), False),
    }
    for name, (text, numbered) in docs.items():
        md = MD / f"{name}.md"
        md.write_text(text, encoding="utf-8")
        render(md, OUT / f"{name}.docx", numbered)
    from PIL import Image
    with Image.open(FIG) as im:
        im.convert("RGB").save(OUT / "04_Figure_1.tif", dpi=(600, 600), compression="tiff_lzw")
    print(f"counts {n}; wrote {sorted(p.name for p in OUT.glob('0*'))} in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

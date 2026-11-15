"""Build the paper D letter's upload set for IJTLD.

Writes submission/paper_d/03_letter.md (author-only text removed, literal
reference numbers), copies the figure as PNG and 600 dpi TIFF, and converts
the Markdown to Word. Reuses the cleaning functions of build_c.py.

Usage: python -I submission/build_d.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "submission"))
import build_c as b                                   # noqa: E402

SRC = ROOT / "manuscript" / "paper_d_letter.md"
FIG = ROOT / "manuscript" / "figure_d1_spending_per_patient.png"
OUT = ROOT / "submission" / "paper_d"


def main() -> int:
    t = b.for_submission(SRC.read_text(encoding="utf-8"))
    t = b.literal_refs(t.replace("## Figure caption", "## Figure captions"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "03_letter.md").write_text(t, encoding="utf-8")
    for f in sorted(OUT.glob("0*.md")):
        txt = f.read_text(encoding="utf-8")
        for pat in b.AUTHOR_ONLY:
            assert pat.strip("\\*:") not in txt or "Target journal" not in txt, f"{f.name}: author-only"
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
            r = subprocess.run([pandoc, str(md), "-f", "markdown+pipe_tables", "-o", str(docx),
                                "--standalone", "--wrap=none"], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            b.styler.process(docx)
            made.append(docx.name)
    print(f"wrote {made} and the figure in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

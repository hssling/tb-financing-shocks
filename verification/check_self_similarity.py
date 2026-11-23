"""Screen papers C and D for text overlap with the author's other manuscripts.

Reuses the shingle method of the companion project's screen
(../provenance_weighting/verification/check_self_similarity.py) by import, so
both projects measure overlap identically. Fails on any verbatim run of 40 or
more words outside reference lists; reports the share of 8-word shingles shared.
Also fails if a cover letter's "no shared passage longer than N words" is not
the longest run this screen finds for that paper. A cover letter already sent
passes if its stated bound still holds (the screen finds no longer run), and
the bound is reported when it is no longer tight. Version 3 of paper D is also
compared with the author's later manuscripts, but not with its own earlier,
unpublished versions.

Usage: python -I verification/check_self_similarity.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PW = ROOT.parent / "provenance_weighting"
sys.path.insert(0, str(PW / "verification"))
import check_self_similarity as ss       # noqa: E402

OUTER = ROOT.parent
D_V3 = ROOT / "manuscript" / "paper_d_letter_v3.md"
TARGETS = [("Paper C (USAID 2025)", ROOT / "manuscript" / "manuscript_c.md"),
           ("Paper D letter (RR-TB spending)", ROOT / "manuscript" / "paper_d_letter.md"),
           ("Paper D letter v3 (Journal of Infection)", D_V3)]
# manuscripts submitted after papers C and D, compared with version 3 only
LATER = [("TB-diabetes cascade, IJTLD-11-26-0796", OUTER / "tb_diabetes_gap/manuscript/v2/submission/02_manuscript.docx"),
         ("ACF yield, IJTB (number pending)", OUTER / "tb_acf_campaign/manuscript/ext_v2/submission/03_Manuscript.docx"),
         ("Private-sector gap, HPM-26-01517", OUTER / "tb_private_gap/manuscript/submission/main_document.docx"),
         ("Nutrition payment, TRSTMH-D-26-00643", OUTER / "tb_nutrition_support/manuscript/submission/manuscript.docx"),
         ("Priority tool, EPP-D-26-01579", OUTER / "tb_priority_tool/manuscript/submission/02_manuscript_anonymised.docx"),
         ("State TB Score, JPH-26-1883", OUTER / "tb_state_score/manuscript/jph_v2/submission/01_manuscript.docx")]
SOURCES = [("Paper A, IJTB-D-26-00779", ss.PAPER_A), ("Paper B, TMI-26-01346", ss.PAPER_B)] + ss.PRIOR \
    + [(name, path) for name, path in TARGETS[:2]]      # C and D against each other
EARLIER_D = {ROOT / "manuscript" / "paper_d_letter.md", ROOT / "manuscript" / "paper_d_letter_v2.md"}


def longest_run(a: list[str], b_shingles: set) -> int:
    """Longest run of consecutive target words whose 8-grams all occur in b."""
    best = cur = 0
    for i in range(len(a) - ss.N + 1):
        if tuple(a[i:i + ss.N]) in b_shingles:
            cur = cur + 1 if cur else ss.N
            best = max(best, cur)
        else:
            cur = 0
    return best


LETTERS = {ROOT / "manuscript" / "manuscript_c.md": ROOT / "submission" / "paper_c" / "02_cover_letter.md",
           ROOT / "manuscript" / "paper_d_letter.md": ROOT / "submission" / "paper_d" / "02_cover_letter.md",
           D_V3: ROOT / "submission" / "paper_d_v3" / "02_cover_letter.md"}
FROZEN = {ROOT / "manuscript" / "manuscript_c.md", ROOT / "manuscript" / "paper_d_letter.md"}


def main() -> int:
    fail = False
    for tname, tpath in TARGETS:
        if not tpath.exists():
            continue
        longest = 0
        words = ss.normalise(ss.body_only(ss.read_any(tpath)))
        tsh = ss.shingles(words)
        print(f"{tname}: {len(words):,} words, {len(tsh):,} distinct 8-grams")
        union = set()
        sources = SOURCES + LATER if tpath == D_V3 else SOURCES
        for sname, spath in sources:
            if Path(spath) == tpath or (tpath == D_V3 and Path(spath) in EARLIER_D):
                continue                                  # a paper against itself or its earlier versions
            if not Path(spath).exists():
                print(f"   {sname:<44} (not on this machine)")
                continue
            ssh = ss.shingles(ss.normalise(ss.body_only(ss.read_any(Path(spath)))))
            shared = tsh & ssh
            union |= shared
            run = longest_run(words, ssh)
            print(f"   {sname:<44} {len(shared):>5} shared  {100 * len(shared) / len(tsh):5.1f}%  "
                  f"longest run {run} words")
            fail |= run >= ss.LONG_RUN
            longest = max(longest, run)
        print(f"   {'COMBINED':<44} {len(union):>5} shared  {100 * len(union) / len(tsh):5.1f}%")
        # the cover letter quotes the longest shared run; it must be this run
        letter = LETTERS.get(tpath)
        if letter and letter.exists():
            import re
            m = re.search(r"no shared passage longer than (\d+) words", letter.read_text(encoding="utf-8"))
            if m and tpath in FROZEN and int(m.group(1)) > longest:
                print(f"   cover letter {letter.parent.name} (as sent) states {m.group(1)} words; the screen now "
                      f"finds {longest}: the stated bound holds")
            elif not m or int(m.group(1)) != longest:
                print(f"   COVER LETTER {letter.parent.name}: states "
                      f"{m.group(1) + ' words' if m else 'no figure'}, the screen finds {longest}")
                fail = True
    print("FAILED: a verbatim run of 40+ words, or a cover letter misstating the longest run" if fail else
          "PASSED: no verbatim run of 40+ words outside reference lists; cover letters state the longest run")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

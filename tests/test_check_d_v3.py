"""Mutation tests for the version 3 check in verification/check_d.py.

Each mutation alters the letter, the cover letter or the outputs in memory;
the check must report a problem for every one, and none for the unaltered
files. Needs the WHO files and the (unpublished) letter; skipped otherwise.
Usage: python -I -m pytest tests/test_check_d_v3.py -q
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verification"))
sys.path.insert(0, str(ROOT / "src"))
import check_d as c                       # noqa: E402
import d_regimen as d                     # noqa: E402

READY = c.V3.exists() and c.V3_COVER.exists() and d.NOTIF.exists()
pytestmark = pytest.mark.skipif(not READY, reason="letter or WHO files not on this machine")

if READY:
    TEXT = c.V3.read_text(encoding="utf-8")
    COVER = c.V3_COVER.read_text(encoding="utf-8")
    R = d.results()
    E = c.extension_outputs()


def run(text=None, cover=None, E_=None):
    return c.check_v3(text if text is not None else TEXT, cover if cover is not None else COVER,
                      None, R, E_ if E_ is not None else E)[0]


def sub(old, new, s=None, count=1):
    s = TEXT if s is None else s
    assert old in s, old
    return s.replace(old, new, count)


def test_unaltered_passes():
    assert run() == []


LETTER_MUTATIONS = {
    "headline median": ("the median fell by 45.9%", "the median fell by 45.8%"),
    "panel size": ("Among the 66 countries", "Among the 67 countries"),
    "share falling": ("in 84.8% of countries", "in 85.8% of countries"),
    "timing": ("64.7% and 71.7%", "64.7% and 61.7%"),
    "region name": ("in the Region of the Americas", "in the European Region"),
    "pooled drugs": ("accounted for 92.4%", "accounted for 82.4%"),
    "total spending": ("from US$296.2 million", "from US$286.2 million"),
    "started": ("from 145,106 to 131,909", "from 145,106 to 141,909"),
    "rho": ("Spearman's rho −0.03", "Spearman's rho −0.30"),
    "untraced number": ("Ethical approval was not required", "In 12 countries ethical approval was not required"),
    "superscript": ("linezolid [1].", "linezolid.^1^"),
    "subheading": ("The fall was mostly in drugs.", "## Results\n\nThe fall was mostly in drugs."),
    "post hoc removed": ("reported below are post hoc,", "reported below were added,"),
    "causal wording": ("the savings were not visibly reinvested", "the savings were not reinvested because of BPaLM"),
    "citation order": ("cost-saving for health systems [6]", "cost-saving for health systems [7]"),
    "AI declaration": ("**Declaration of generative AI and AI-assisted technologies in the manuscript preparation "
                       "process.**", "**Use of AI.**"),
    "anchor DOI": ("https://doi.org/10.1016/j.jinf.2025.106509", "https://doi.org/10.1016/j.jinf.2025.106510"),
    "seven authors": ("Sweeney S, Laurence YV, Berry C, Singh MP, Dodd M, Fielding K, et al.",
                      "Sweeney S, Laurence YV, Berry C, Singh MP, Dodd M, Fielding K, Kazounis E."),
    "table cell": ("| 29 | −46.3 (−72.5 to −12.8) |", "| 29 | −46.3 (−72.5 to −12.9) |"),
    "legend": ("open diamonds mark two countries", "open diamonds mark three countries"),
    "earlier submission": ("Ethical approval was not required", "The letter was declined elsewhere. Ethical approval "
                           "was not required"),
}


@pytest.mark.parametrize("name", sorted(LETTER_MUTATIONS))
def test_letter_mutation_is_caught(name):
    old, new = LETTER_MUTATIONS[name]
    assert run(text=sub(old, new)), name


def test_word_limit():
    padding = " ".join(["word"] * 200)
    assert any("words > 1,000" in e for e in run(text=sub("Three implications follow", padding + " Three implications follow")))


def test_third_exhibit():
    extra = "\n**Table 2.** Another table.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
    assert any("at most two" in e for e in run(text=TEXT.rstrip() + "\n" + extra))


def test_cover_letter_counts_and_disclosure():
    assert run(cover=COVER.replace("840 words", "841 words", 1) if "840 words" in COVER
               else COVER.replace(" words,", "0 words,", 1))
    assert run(cover=COVER.replace("BLT/2026/298045", "BLT/2026/298045; IJTLD-11-26-0773"))
    assert run(cover=COVER.replace("106509", "106510"))


@pytest.mark.parametrize("path,value", [
    (("sld", "treated", "verdict"), "numbers treated rose while total spending fell"),
    (("composition", "pooled", "mostly_drugs"), False),
    (("cpp", "timing", "share_by_2022"), 0.45),
])
def test_wording_conditions_follow_the_outputs(path, value):
    E2 = copy.deepcopy(E)
    node = E2
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    assert run(E_=E2)

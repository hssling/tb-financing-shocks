"""Mutation tests for the version 4 check in verification/check_d.py.

Each mutation alters the Short Communication, its cover letter, the outputs or
the text of the built main document in memory; the check must report a problem
for every one, and none for the unaltered files. Needs the WHO files, the
(unpublished) manuscript and its built set; skipped otherwise.
Usage: python -I -m pytest tests/test_check_d_v4.py -q
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verification"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "submission"))
import check_d as c                       # noqa: E402
import d_regimen as d                     # noqa: E402

COVER_MD = c.V4_DIR / "_md" / "05_cover_letter.md"
MAIN_DOCX = c.V4_DIR / "02_main_document.docx"
READY = c.V4.exists() and COVER_MD.exists() and MAIN_DOCX.exists() and d.NOTIF.exists()
pytestmark = pytest.mark.skipif(not READY, reason="manuscript, built set or WHO files not on this machine")

if READY:
    import build_d_v4 as bv               # noqa: E402
    TEXT = c.V4.read_text(encoding="utf-8")
    COVER = COVER_MD.read_text(encoding="utf-8")
    R = d.results()
    E = c.extension_outputs()
    MAIN_TEXT, CORE = c.docx_text(MAIN_DOCX)
    N_SELF = len(bv.self_citations(TEXT))


def run(text=None, cover=None, E_=None, built=None):
    return c.check_v4(text if text is not None else TEXT, cover if cover is not None else COVER,
                      built, R, E_ if E_ is not None else E)[0]


def sub(old, new, s=None, count=1):
    s = TEXT if s is None else s
    assert old in s, old
    return s.replace(old, new, count)


def test_unaltered_passes():
    assert run() == []


def test_unaltered_built_set_passes():
    assert run(built=c.V4_DIR) == []


MUTATIONS = {
    "abstract headline": ("fell by 45.9% in real terms, and the reported", "fell by 44.9% in real terms, and the reported"),
    "panel size": ("Among the 66 countries", "Among the 67 countries"),
    "share falling": ("in 84.8% of countries", "in 85.8% of countries"),
    "timing": ("Most of the fall (64.7% and 71.7%)", "Most of the fall (64.7% and 61.7%)"),
    "region name": ("in the Region of the Americas", "in the European Region"),
    "pooled drugs": ("accounted for 92.4% of that fall", "accounted for 82.4% of that fall"),
    "total spending": ("from US$296.2 million", "from US$286.2 million"),
    "started": ("from 145,106 to 131,909", "from 145,106 to 141,909"),
    "rho": ("Spearman's rho −0.03", "Spearman's rho −0.30"),
    "deflator": ("prices rose by 20.6%", "prices rose by 21.6%"),
    "join": ("the median ratio of the 2020 to the 2019 count was 0.88", "the median ratio of the 2020 to the 2019 "
             "count was 0.87"),
    "cpp adopters": ("−43.3% in 30 high adopters", "−43.3% in 31 high adopters"),
    "panel medians": ("from US$2,390 in 2019", "from US$2,391 in 2019"),
    "composition totals": ("to US$276.6 million", "to US$267.6 million"),
    "from 2020 without two": ("numbers rose by 20.5%", "numbers rose by 25.0%"),
    "untraced number": ("The data are aggregated and public,", "The data for 12 countries are aggregated and public,"),
    "untraced number in the abstract": ("Both measures are drug costs.", "Both measures are drug costs in 12 countries."),
    "bracketed citation": ("tracked by source and function.^1^", "tracked by source and function [1]."),
    "citation in the abstract": ("Both measures are drug costs.", "Both measures are drug costs.^13^"),
    "citation order": ("dependent on the price of bedaquiline.^10^", "dependent on the price of bedaquiline.^11^"),
    "uncited reference": ("modelled.^3^", "modelled."),
    "table before figure": ("in 84.8% of countries (Figure 1A; Table 1)", "in 84.8% of countries (Table 1; Figure 1A)"),
    "missing figure": ("(Figure 1A; Table 1)", "(Table 1)"),
    "causal wording": ("the savings were not visibly reinvested", "the savings were not reinvested because of BPaLM"),
    "impact": ("such as those in economic and budgetary evaluations", "such as the impact of the regimens"),
    "US spelling": ("ethical approval was not required", "ethical approval was not required by the program"),
    "post hoc removed": ("the further analyses were post hoc.", "the further analyses followed."),
    "AI removed": ("Claude (Anthropic), a large language model, was used", "Software was used"),
    "abbreviated title": ("# Drug spending per patient treated for drug-resistant tuberculosis",
                          "# Drug spending per patient treated for RR-TB"),
    "keyword count": ("resource allocation; bedaquiline", "resource allocation; bedaquiline; pretomanid"),
    "running title": ("**Running title:** Drug spending per patient with drug-resistant tuberculosis",
                      "**Running title:** Drug spending per patient with drug-resistant tuberculosis, 2019 to 2024, "
                      "by country"),
    "AMA authors": ("Su Y, Garcia Baena I, Harle AC, et al.", "Su Y, Garcia Baena I, et al."),
    "seven authors": ("Wells WA, Scheening S, Waseem S, Schulhofer A, Wolde Y, Stallworthy G.",
                      "Wells WA, Scheening S, Waseem S, Schulhofer A, Wolde Y, Stallworthy G, Other A."),
    "article without DOI": (" doi:10.1136/bmjgh-2021-007182", ""),
    "journal-response opening": ("Treating rifampicin-resistant tuberculosis (RR-TB), which",
                                 "Dear Editor, treating rifampicin-resistant tuberculosis (RR-TB), which"),
    "table cell": ("| 29 | −46.3 (−72.5 to −12.8) |", "| 29 | −46.3 (−72.5 to −12.9) |"),
    "legend": ("open diamonds mark two countries", "open diamonds mark three countries"),
    "earlier submission named": ("The data are aggregated and public,", "An earlier version was declined. The data are aggregated and public,"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_manuscript_mutation_is_caught(name):
    old, new = MUTATIONS[name]
    assert run(text=sub(old, new)), name


def test_main_text_word_limit():
    padding = " ".join(["word"] * 120)
    assert any("> 2,000" in e for e in run(text=sub("### Limitations\n\n", "### Limitations\n\n" + padding + " ")))


def test_abstract_word_limit():
    padding = " ".join(["word"] * 20)
    assert any("abstract" in e and "> 250" in e for e in run(text=sub("Both measures are drug costs.",
                                                                      "Both measures are drug costs. " + padding)))


def test_reference_limit():
    i = TEXT.index("## Table")
    extra = "".join(f"{k}. Extra reference {k}. 2026.\n" for k in range(15, 22))
    text = TEXT[:i] + extra + "\n" + TEXT[i:]
    cited = sub("archived openly.^14^", "archived openly.^14-21^", text)
    assert any("> 20" in e for e in run(text=cited))


COVER_MUTATIONS = {
    "theme": ('Theme 1, "Health financing and economics"', 'Theme 3, "Global health, health planning and interventions"'),
    "counts": ("words of main text", "words of text"),
    "related missing": ("JPH-26-1883", "JPH-26-0000"),
    "same-journal line": ("HPM-26-01517, this journal", "HPM-26-01517, another journal"),
    "earlier submission": ("BLT/2026/298045", "BLT/2026/298045; IJTLD-11-26-0773"),
    "abandoned journal": ("for transparency", "for transparency (also sent to the Journal of Infection)"),
    "declined manuscript as under review": ("in preparation for resubmission", "TMI-26-01346, under review"),
}


@pytest.mark.parametrize("name", sorted(COVER_MUTATIONS))
def test_cover_letter_mutation_is_caught(name):
    old, new = COVER_MUTATIONS[name]
    assert old in COVER, old
    assert run(cover=COVER.replace(old, new, 1)), name


def test_anonymised_main_document_passes():
    assert c.anonymisation_errors(MAIN_TEXT, CORE, N_SELF) == []


@pytest.mark.parametrize("leak", ["Siddalingaiah HS. TB financing shocks", "Shridevi Institute",
                                  "https://github.com/hssling/tb-financing-shocks", "doi:10.5281/zenodo.24478545",
                                  "ORCID 0000-0002-4771-8285"])
def test_leak_in_main_document_is_caught(leak):
    assert c.anonymisation_errors(MAIN_TEXT + " " + leak, CORE, N_SELF)


def test_unblinded_self_citation_is_caught():
    assert c.anonymisation_errors(MAIN_TEXT.replace(bv.BLIND_REF, "Author. Code archive.", 1), CORE, N_SELF)


def test_author_in_document_properties_is_caught():
    assert c.anonymisation_errors(MAIN_TEXT, CORE.replace("<dc:creator></dc:creator>",
                                                          "<dc:creator>Siddalingaiah</dc:creator>"), N_SELF)


@pytest.mark.parametrize("path,value", [
    (("sld", "treated", "verdict"), "numbers treated rose while total spending fell"),
    (("composition", "pooled", "mostly_drugs"), False),
    (("cpp", "timing", "share_by_2022"), 0.45),
    (("sld", "treated", "composition_panel", "verdict"), "total spending rose"),
])
def test_wording_conditions_follow_the_outputs(path, value):
    E2 = copy.deepcopy(E)
    node = E2
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    assert run(E_=E2)


def test_blinding_withholds_the_archive_and_the_self_citation():
    md = bv.blind(bv.body(TEXT))
    assert bv.BLIND_REF in md and bv.BLIND_LINK in md
    assert "zenodo" not in md.lower() and "hssling" not in md


def test_blinding_refuses_a_leak():
    with pytest.raises(AssertionError):
        bv.blind(bv.body(TEXT) + "\nShridevi Institute\n")

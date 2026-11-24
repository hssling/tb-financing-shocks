"""Verify paper D (IJTLD letter) against src/d_regimen.py.

1. Every derived number the letter states equals what the code computes now.
2. References numbered 1..n, all cited, in order of first citation; at most 15.
3. Letter text at most 1,100 words (IJTLD Letter).
4. IJTLD form: superscript citations; title <= 110 characters without
   abbreviations; running head <= 45 characters; 3-5 keywords, none in the
   title; first author and "et al." when there are more than three authors;
   an ethics statement; the built Word file embeds the figure and carries
   line numbers.

Version 3 (Journal of Infection Letter, with the post hoc analyses of plan
section 11), when manuscript/paper_d_letter_v3.md is present:

5. The saved outputs (outputs/d_extend) equal a fresh run of src/d_extend.py.
6. Every derived number in the letter text and figure legend equals the
   outputs, and every number in them is either derived or on a short list of
   stated constants (years, the release date, source-stated prices); the table
   equals the one rendered from the outputs; conditional wording ("about half",
   "mostly", "not visibly reinvested") holds in the outputs.
7. Journal of Infection form: at most 1,000 words, 10 references and two
   figures or tables; no subheadings in the letter; citations "[n]" in order;
   at most six authors then "et al."; DOIs as URLs; reference 1 is the Journal
   article the letter answers; the AI declaration precedes the references; the
   added analyses are called post hoc; no causal wording; the built Word file
   and the cover letter agree with the source; the cover letter does not name
   the earlier, declined submission.

Version 4 (Short Communication for The International Journal of Health
Planning and Management), when manuscript/paper_d_shortcomm_v4.md is present:

8. Every derived number in the abstract, main text and figure legend equals the
   outputs (version 3 passages and the added ones), every other number is a
   stated constant, the table equals the one rendered from the outputs, and the
   wording conditions of version 3 hold.
9. Journal limits: main text at most 2,000 words, abstract at most 250 words
   without citations, at most 20 references and seven keywords, running title
   under 70 characters, title without abbreviations.
10. References, Figure 1 and Table 1 cited in order of first citation; AMA
    reference form; no causal wording; British spelling; post hoc analyses and
    the use of AI described in the Methods; no opening in response to a journal
    article.
11. The built set: all five files present and newer than the source; the main
    document anonymised (no name, affiliation, contact, archive link or
    self-citation, empty document properties); the title page carries the
    derived word counts; the cover letter states Theme 1, carries the derived
    counts, discloses the related manuscripts by their current numbers and does
    not name the earlier submissions of this work.

Usage: python -I verification/check_d.py ; exit 1 on any failure.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "submission"))
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
    if V3.exists():
        R3, E = R, extension_outputs()
        e3, info = check_v3(V3.read_text(encoding="utf-8"), V3_COVER.read_text(encoding="utf-8")
                            if V3_COVER.exists() else None, V3_DOCX, R3, E)
        if e3:
            print(f"FAILED (version 3): {len(e3)} problem(s)\n  " + "\n  ".join(e3))
            return 1
        print(f"PASSED (version 3): outputs equal a fresh run; {info}")
    if V4.exists():
        E = extension_outputs()
        cover = V4_DIR / "_md" / "05_cover_letter.md"
        e4, info = check_v4(V4.read_text(encoding="utf-8"), cover.read_text(encoding="utf-8")
                            if cover.exists() else None, V4_DIR, R, E)
        if e4:
            print(f"FAILED (version 4): {len(e4)} problem(s)\n  " + "\n  ".join(e4))
            return 1
        print(f"PASSED (version 4): {info}")
    return 0


# ------------------------------------------------------------------ version 3

V3 = ROOT / "manuscript" / "paper_d_letter_v3.md"
V3_COVER = ROOT / "submission" / "paper_d_v3" / "02_cover_letter.md"
V3_DOCX = ROOT / "submission" / "paper_d_v3" / "03_letter.docx"
ANCHOR_DOI = "10.1016/j.jinf.2025.106509"
NAMES = {"AFR": "African Region", "AMR": "Region of the Americas", "EMR": "Eastern Mediterranean Region",
         "EUR": "European Region", "SEA": "South-East Asia Region", "WPR": "Western Pacific Region",
         "IND": "India", "RUS": "the Russian Federation"}
# numbers that are not derived from the data: years, the release date, figure
# number, the 6-month regimen, and prices as stated by the cited sources [3-5]
CONSTANTS = {str(y) for y in range(2017, 2027)} | {"1", "6", "25", "34", "289", "130", "310", "588"}
CAUSAL = (r"\bcaus\w*", r"\bled to\b", r"\bdue to\b", r"\bbecause of\b", r"\beffect of\b", r"\bresult(ed|ing)? in\b",
          r"\bdr(o|i)ve[ns]?\b", r"\bdriven\b", r"\bimpact\w*", r"\battributable\b", r"\bthanks to\b")


def extension_outputs() -> dict:
    """The saved outputs, after checking that they equal a fresh run."""
    import json
    import d_extend as x
    saved = json.loads((x.OUT / "results.json").read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(x.jsonable(x.results()[0]), sort_keys=True))
    if saved != fresh:
        raise SystemExit("FAILED: outputs/d_extend/results.json differs from a fresh run; rerun src/d_extend.py")
    return saved


def v3_wants(R: dict, E: dict) -> tuple[dict, list[str]]:
    """Derived strings the letter must contain, and conditions the wording relies on."""
    m = lambda v: f"{v:.1f}".replace("-", "−")                    # signed, unicode minus
    f = lambda v: f"{abs(100 * v):.1f}"                           # magnitude of a fall, %
    p = lambda v: f"{100 * v:.1f}"
    usd = lambda v: f"US${v:,.0f}"
    word = lambda n: ("no", "one", "two", "three", "four", "five")[n] if n < 6 else str(n)
    s, c, C = E["sld"], E["cpp"], E["composition"]
    sd, cd = s["distribution"]["all_real"], c["distribution"]["all_real"]
    T, T20 = s["treated"], s["treated_2020"]
    six = R["sld"]["six_2024"]
    pct = lambda dlog: m(100 * (math.exp(dlog) - 1))
    regs = {k: v for k, v in s["distribution"]["by_region"].items() if v["interpreted"]}
    lo, hi = max(regs, key=lambda k: regs[k]["median"]), min(regs, key=lambda k: regs[k]["median"])
    L2 = T["largest_two"]
    pooled = C["pooled"]
    direction = lambda v: "rose" if v > 0 else "fell"
    rows = []
    import csv
    with (ROOT / "outputs" / "d_extend" / "country_changes.csv").open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["sld_change_real"]]
    beyond = sum(1 for r in rows if not 1 / 128 <= 1 + float(r["sld_change_real"]) <= 16)
    want = {
        "minimum started": f"each with at least {d.MIN_STARTED} people started",
        "adopters": f"by a median of {pct(six['median_non'])}% in {six['n_non']} non-adopters and "
                    f"{pct(six['median_high'])}% in {six['n_high']} high adopters",
        "adopters p": f"permutation p = {six['p']:.2f})",
        "sld distribution": f"Among the {sd['n']} countries reporting second-line drug expenditure per patient started "
                            f"in both years, the median fell by {f(sd['median'])}% in real terms (interquartile range "
                            f"{m(100 * sd['q1'])}% to {m(100 * sd['q3'])}%), and it fell in {p(sd['share_falling'])}% "
                            f"of countries",
        "cpp distribution": f"among the {cd['n']} reporting the drug cost per person starting MDR-TB treatment, it fell "
                            f"by {f(cd['median'])}% ({m(100 * cd['q1'])}% to {m(100 * cd['q3'])}%), in "
                            f"{p(cd['share_falling'])}% of countries",
        "region range": f"from {f(regs[lo]['median'])}% in the {NAMES[lo]} to {f(regs[hi]['median'])}% in the "
                        f"{NAMES[hi]}",
        "low income": f"by {f(s['distribution']['by_income']['LIC']['median'])}% in low-income countries",
        "two measures": f"same direction in {p(C['two_drug_measures']['same_direction'])}% of the "
                        f"{C['two_drug_measures']['n']} countries with both",
        "timing": f"{p(s['timing']['share_by_2022'])}% and {p(c['timing']['share_by_2022'])}% of the 2019–2024 fall "
                  f"in the two medians had occurred by 2022",
        "composition n": f"In {C['n']} countries that also reported other programme expenditure",
        "drug share": f"a median {p(C['drug_share_median']['2019'])}% of that spending in 2019 and "
                      f"{p(C['drug_share_median']['2024'])}% in 2024",
        "pooled total": f"fell from {usd(pooled['total'][0])} to {usd(pooled['total'][1])} "
                        f"({m(100 * pooled['relative_total'])}%)",
        "pooled drugs": f"drugs, from {usd(pooled['drug'][0])} to {usd(pooled['drug'][1])}, accounted for "
                        f"{p(pooled['drug_share_of_change'])}% of that fall",
        "pooled programme": f"other programme costs fell from {usd(pooled['programme'][0])} to "
                            f"{usd(pooled['programme'][1])} ({m(100 * pooled['relative_programme'])}%), although by "
                            f"{f(C['change_programme']['median'])}% in the median country",
        "totals": f"In the {T['n']} countries, total second-line drug spending {direction(T['change_total_real_sld'])} "
                  f"by {f(T['change_total_real_sld'])}% in real terms, from US${T['total_real_sld']['2019'] / 1e6:.1f} "
                  f"million to US${T['total_real_sld']['2024'] / 1e6:.1f} million, while the number started on "
                  f"treatment {direction(T['change_started'])} by {f(T['change_started'])}%, from "
                  f"{T['started']['2019']:,.0f} to {T['started']['2024']:,.0f}",
        "per country": f"(Spearman's rho {T['spearman_cost_vs_patients']:+.2f}".replace("-", "−").replace("+", "") +
                       f"; Figure 1B); numbers rose in {T['quadrants']['cost_down_patients_up']} of the "
                       f"{T['quadrants']['cost_down_patients_up'] + T['quadrants']['cost_down_patients_down']} "
                       f"countries where spending per patient fell",
        "largest two": f"{NAMES[L2['iso3'][0]]} and {NAMES[L2['iso3'][1]]}, accounted for {p(L2['share_started'])}% "
                       f"of people started in 2019 and {p(L2['share_spending'])}% of spending; without them, numbers "
                       f"{direction(L2['without']['change_started'])} by {f(L2['without']['change_started'])}% while "
                       f"spending {direction(L2['without']['change_total_real_sld'])} by "
                       f"{f(L2['without']['change_total_real_sld'])}%",
        "from 2020": f"numbers {direction(T20['change_started'])} by {f(T20['change_started'])}% while spending "
                     f"{direction(T20['change_total_real_sld'])} by {f(T20['change_total_real_sld'])}%",
        "legend n": f"among the {sd['n']} countries reporting each measure in both 2019 and 2024"
                    if sd["n"] == cd["n"] else "(n differ)",
        "legend beyond": f"open diamonds mark {word(beyond)} countries beyond the horizontal axis",
    }
    conditions = []
    for which, a in (("sld", sd), ("cpp", cd)):
        if not 0.4 <= 1 + a["median"] <= 0.6:
            conditions.append(f"'about half': {which} real median ratio {1 + a['median']:.2f}")
        if not E[which]["timing"]["share_by_2022"] > 0.5:
            conditions.append(f"'mostly before BPaLM': {which} share by 2022 {E[which]['timing']['share_by_2022']:.2f}")
        groups = list(E[which]["distribution"]["by_region"].values()) + [
            g for k, g in E[which]["distribution"]["by_income"].items() if k != "unclassified"]
        if any(g["median"] >= 0 for g in groups):
            conditions.append(f"'fell in every WHO region and income group': not so for {which}")
    if not pooled["mostly_drugs"]:
        conditions.append("'mostly in drugs': drugs are not more than half of the pooled fall")
    if T["verdict"] != "savings not visibly reinvested":
        conditions.append(f"'not visibly reinvested': the pre-stated verdict is {T['verdict']!r}")
    if abs(T["spearman_cost_vs_patients"]) >= 0.2:
        conditions.append(f"'unrelated': Spearman {T['spearman_cost_vs_patients']:+.2f}")
    return want, conditions


def check_v3(t: str, cover: str | None, docx: Path | None, R: dict, E: dict) -> tuple[list[str], str]:
    errs: list[str] = []
    want, conditions = v3_wants(R, E)
    errs += [f"wording not supported by the outputs: {c}" for c in conditions]
    for label, w in want.items():
        if w not in t:
            errs.append(f"text: expected {label} as {w!r}")
    start, fund = t.index("Dear Editor"), t.index("**Funding.**")
    i = t.index("## References"); j = t.index("\n## ", i + 5)
    letter = t[start:fund]
    legend = t[t.index("## Figure legend"):t.index("\n## ", t.index("## Figure legend") + 5)] \
        if "\n## Table" in t else t[t.index("## Figure legend"):]
    # 6. every number in the letter text and the figure legend is derived or a stated constant
    traced = set()
    for w in want.values():
        traced |= {x.replace(",", "") for x in re.findall(r"\d[\d,]*(?:\.\d+)?", w)}
    body = re.sub(r"\[\d+(?:[,–-]\d+)*\]|COVID-19", "", letter + legend)
    for x in re.findall(r"\d[\d,]*(?:\.\d+)?", body):
        x = x.replace(",", "").rstrip(".")
        if x not in traced and x not in CONSTANTS:
            errs.append(f"untraced number in the letter or legend: {x}")
    # the table equals the one rendered from the outputs
    sys.path.insert(0, str(ROOT / "manuscript"))
    import make_d_extend_exhibits as mx
    if mx.table(E).strip() not in t:
        errs.append("Table 1 differs from the table rendered from the outputs")
    # 7. Journal of Infection form
    nwords = len(re.sub(r"\*\*|`|#|\[\d+(?:[,–-]\d+)*\]", "", letter).split())
    if nwords > 1000:
        errs.append(f"letter {nwords} words > 1,000")
    nfig = len(re.findall(r"(?m)^\*\*Figure(?: \d+)?\.", t))
    ntab = len(re.findall(r"(?m)^\*\*Table \d+\.", t))
    if nfig + ntab > 2:
        errs.append(f"{nfig} figures and {ntab} tables: at most two in total")
    if re.search(r"(?m)^#", letter):
        errs.append("a subheading inside the letter")
    if re.search(r"\^\d", letter):
        errs.append("superscript citation; the Journal uses [n]")
    listed = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", t[i:j])]
    if listed != list(range(1, len(listed) + 1)) or len(listed) > 10:
        errs.append(f"reference list {listed} (at most 10)")
    order: list[int] = []
    for mm in re.finditer(r"\[(\d+(?:[,–-]\d+)*)\]", t[start:i]):
        for part in mm.group(1).split(","):
            rng = [int(x) for x in re.split(r"[–-]", part)]
            for n in range(rng[0], rng[-1] + 1):
                if n not in order:
                    order.append(n)
    if sorted(order) != listed:
        errs.append(f"cited {sorted(order)} vs listed {listed}")
    if order != sorted(order):
        errs.append(f"references not in order of first citation: {order}")
    entries = dict((int(n), e) for n, e in re.findall(r"(?m)^(\d+)\. (.*)$", t[i:j]))
    if ANCHOR_DOI not in entries.get(1, "") or "J Infect" not in entries.get(1, ""):
        errs.append("reference 1 is not the Journal of Infection article the letter answers")
    if not re.match(r"Daniel and colleagues", letter[len("Dear Editor,"):].strip()):
        errs.append("the letter does not open by answering the Journal article")
    for n, e in entries.items():
        authors = e.split(". ")[0]
        if "et al" not in authors and authors.count(",") + 1 > 6:
            errs.append(f"reference {n}: more than six authors without et al.")
        if "et al" in authors and authors.split(", et al")[0].count(",") + 1 != 6:
            errs.append(f"reference {n}: et al. after other than six authors")
        if re.search(r"\bdoi:", e) or (re.search(r"\d{4};\d+", e) and "https://doi.org/10." not in e):
            errs.append(f"reference {n}: journal references carry the DOI as a URL")
    ai = "**Declaration of generative AI and AI-assisted technologies in the manuscript preparation process.**"
    if ai not in t or t.index(ai) > i:
        errs.append("Elsevier AI declaration missing or not before the references")
    if "post hoc" not in letter:
        errs.append("the added analyses are not called post hoc")
    for pat in CAUSAL:
        hit = re.search(pat, letter + legend, flags=re.I)
        if hit:
            errs.append(f"causal wording: {hit.group(0)!r}")
    title = t.splitlines()[0].lstrip("# ").strip()
    rt = re.search(r"(?m)^\*\*Running title:\*\* (.*)$", t).group(1).strip()
    if sum(ch.isalpha() for ch in rt) > 50:
        errs.append("running title over 50 letters")
    kws = re.search(r"(?m)^\*\*Keywords:\*\* (.*)$", t).group(1).split(";")
    if not 1 <= len(kws) <= 7:
        errs.append(f"{len(kws)} keywords; the Journal asks for 1-7")
    if re.search(r"IJTLD-11-26-0773|declined|previously submitted", t + (cover or ""), flags=re.I):
        errs.append("the letter or cover letter names the earlier submission")
    if docx is not None:
        if not docx.exists():
            errs.append(f"{docx.name} not built")
        else:
            import zipfile
            with zipfile.ZipFile(docx) as z:
                names_ = z.namelist(); doc = z.read("word/document.xml").decode("utf-8")
            if not any(x.startswith("word/media/") for x in names_):
                errs.append("built letter does not embed the figure")
            if "<w:tbl>" not in doc:
                errs.append("built letter has no table")
            if not re.search(r">\[1\] Daniel", doc):
                errs.append("built letter's references are not numbered [n]")
            if docx.stat().st_mtime < V3.stat().st_mtime:
                errs.append("built letter is older than the source; rerun submission/build_d.py")
            if f"{nwords:,} words" not in doc:
                errs.append("built title page word count differs from the source")
    if cover is not None:
        if f'"{title}"' not in cover:
            errs.append("cover letter does not carry the manuscript title")
        counts = (f"({nwords:,} words, {len(listed)} references, {('no', 'one', 'two')[nfig]} figure"
                  f"{'s' if nfig > 1 else ''} and {('no', 'one', 'two')[ntab]} table")
        if counts not in cover:
            errs.append(f"cover letter counts differ from the letter: expected {counts!r}")
        if "Journal of Infection" not in cover or "106509" not in cover:
            errs.append("cover letter does not name the Journal article answered")
    info = (f"{len(want)} derived passages and every number traced; Table 1 matches; letter {nwords} words; "
            f"{len(listed)} references in order; {nfig} figure and {ntab} table; Journal of Infection form, "
            f"Word file and cover letter checked")
    return errs, info


# ------------------------------------------------------------------ version 4

V4 = ROOT / "manuscript" / "paper_d_shortcomm_v4.md"
V4_DIR = ROOT / "submission" / "paper_d_v4"
V4_FILES = ("01_title_page.docx", "02_main_document.docx", "03_manuscript_with_author_details.docx",
            "04_Figure_1.tif", "05_cover_letter.docx")
# related manuscripts under review, by their current numbers
V4_RELATED = ("BLT/2026/298045", "HPM-26-01517", "IJTB-D-26-00779", "IJTB-D-26-00777", "IJTLD-11-26-0796",
              "TRSTMH-D-26-00643", "EPP-D-26-01579", "JPH-26-1883")
# earlier submissions of this work, and a manuscript no longer under review
V4_FORBIDDEN = ("IJTLD-11-26-0773", "Journal of Infection", "Tropical Medicine & International Health",
                "Tropical Medicine and International Health", "TMIH", "TMI-26-01346",
                "Lancet Infectious", "declined", "previously submitted")
# stated constants beyond those of version 3: the outlier percentile and software versions
CONSTANTS_V4 = CONSTANTS | {"99", "3.14", "3.10"}
CAUSAL_V4 = CAUSAL + (r"\bbecause\b", r"\bowing to\b", r"\bcontribut\w*", r"\bexplained by\b", r"\bas a result\b")
US_SPELLING = (r"\bprograms?\b", r"\banalyz\w*", r"\bcolor\w*",r"\bfavor\w*", r"\bcenter\b",
               r"\bmodel(ed|ing)\b", r"\borganization\b", r"\brandomiz\w*", r"\butiliz\w*", r"\bprioritiz\w*",
               r"\bbehavior\w*", r"\blabeled\b")
CITE = r"\^(\d+(?:[,–-]\d+)*)\^"


def v4_wants(R: dict, E: dict) -> tuple[dict, list[str]]:
    """Version 3 passages plus those added in version 4, and the wording conditions."""
    want, conditions = v3_wants(R, E)
    m = lambda v: f"{v:.1f}".replace("-", "−")
    f = lambda v: f"{abs(100 * v):.1f}"
    p = lambda v: f"{100 * v:.1f}"
    usd = lambda v: f"US${v:,.0f}"
    word = lambda n: ("no", "one", "two", "three", "four", "five")[n] if n < 6 else str(n)
    direction = lambda v: "rose" if v > 0 else "fell"
    pct = lambda dlog: m(100 * (math.exp(dlog) - 1))
    s, c, C, a = E["sld"], E["cpp"], E["composition"], R["adoption"]
    sd, cd = s["distribution"]["all_real"], c["distribution"]["all_real"]
    T, T20 = s["treated"], s["treated_2020"]
    six_c = R["cpp"]["six_2024"]
    prim = (R["sld"]["primary"]["n_high"], R["cpp"]["primary"]["n_high"])
    sm, cm = s["timing"]["medians"], c["timing"]["medians"]
    CP = T["composition_panel"]
    W20 = T20["largest_two"]["without"]
    want.update({
        "abstract n": f"analysed for the {sd['n']} countries reporting each measure in both 2019 and 2024"
                      if sd["n"] == cd["n"] else "(n differ)",
        "abstract headline": f"fell by {f(sd['median'])}% in real terms, and the reported drug cost per patient "
                             f"starting treatment for multidrug-resistant tuberculosis by {f(cd['median'])}%",
        "abstract share": f"Spending fell in {p(sd['share_falling'])}% and {p(cd['share_falling'])}% of countries",
        "abstract timing": f"Most of the fall ({p(s['timing']['share_by_2022'])}% and "
                           f"{p(c['timing']['share_by_2022'])}%) had occurred by 2022",
        "abstract drugs": f"Drugs accounted for {p(C['pooled']['drug_share_of_change'])}% of the pooled fall",
        "abstract totals": f"Total second-line drug spending {direction(T['change_total_real_sld'])} by "
                           f"{f(T['change_total_real_sld'])}%, while the number of people started on treatment "
                           f"{direction(T['change_started'])} by {f(T['change_started'])}%; without India and the "
                           f"Russian Federation, numbers {direction(T['largest_two']['without']['change_started'])} by "
                           f"{f(T['largest_two']['without']['change_started'])}%",
        "join": f"across {R['join']['countries']} countries, the median ratio of the 2020 to the 2019 count was "
                f"{R['join']['median_ratio_2020_to_2019']:.2f}",
        "deflator": f"prices rose by {p(1 / E['deflator_factor_2019_to_2024'] - 1)}% from 2019 to 2024",
        "permutations": f"({d.PERMS:,} permutations)",
        "BPaL reporting": f"with {a['reporting'][2022]} and {a['reporting'][2023]} countries reporting",
        "analysable": f"only {WORDS[min(prim)]} to {WORDS[max(prim)]} of the countries with spending data were "
                      f"high adopters",
        "six-month reporting": f"reported by {a['six_reporting'][2024]} countries for 2024; {a['six_ge_25_2024']} of "
                               f"the {a['six_with_share_2024']} countries with a share reached 25%",
        "cpp adopters": f"by {pct(six_c['median_high'])}% in {six_c['n_high']} high adopters and "
                        f"{pct(six_c['median_non'])}% in {six_c['n_non']} non-adopters (p = {six_c['p']:.2f})",
        "placebo": "adopters' spending had risen relative to non-adopters'"
                   if R["sld"]["six_2024_placebo"]["diff"] > 0 and R["cpp"]["six_2024_placebo"]["diff"] > 0
                   else "(placebo direction changed)",
        "current dollars": f"In current dollars the medians fell by {f(s['distribution']['all_current']['median'])}% "
                           f"and {f(c['distribution']['all_current']['median'])}%",
        "panel medians": f"from {usd(sm['2019'])} in 2019 to {usd(sm['2024'])} in 2024 for drug spending per patient "
                         f"started, and from {usd(cm['2019'])} to {usd(cm['2024'])} for the reported drug cost",
        "largest year": f"The largest single-year falls came in {s['timing']['largest_single_year_fall']} and "
                        f"{c['timing']['largest_single_year_fall']}",
        "excluded": f"({word(len(C['excluded_programme_p99']))} more was excluded by the 99th-percentile rule)",
        "composition totals": f"fell by {f(CP['change_total'])}%, from "
                              f"US${CP['total_real_drug_and_programme']['2019'] / 1e6:.1f} million to "
                              f"US${CP['total_real_drug_and_programme']['2024'] / 1e6:.1f} million, while the number "
                              f"started {direction(CP['change_started'])} by {f(CP['change_started'])}%",
        "from 2020 without two": f"without India and the Russian Federation, numbers {direction(W20['change_started'])} "
                                 f"by {f(W20['change_started'])}% while spending "
                                 f"{direction(W20['change_total_real_sld'])} by {f(W20['change_total_real_sld'])}%",
    })
    if not (CP["change_total"] < 0 and CP["verdict"] == "savings not visibly reinvested"):
        conditions.append(f"composition panel: total {CP['change_total']:+.3f}, verdict {CP['verdict']!r}")
    if T20["largest_two"]["iso3"] != T["largest_two"]["iso3"]:
        conditions.append("the two largest programmes differ between the 2019 and 2020 bases")
    return want, conditions


def docx_text(path: Path) -> tuple[str, str]:
    """Visible text and the core properties of a Word file."""
    import zipfile
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode("utf-8")
        core = z.read("docProps/core.xml").decode("utf-8") if "docProps/core.xml" in z.namelist() else ""
    return "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", doc)), core


def anonymisation_errors(text: str, core: str, n_self: int) -> list[str]:
    """The main document must identify neither the author nor the author's archive."""
    import build_d_v4 as bv
    errs = [f"main document contains {leak!r}" for leak in bv.LEAKS if leak.lower() in text.lower()]
    if text.count(bv.BLIND_REF) != n_self:
        errs.append(f"main document blinds {text.count(bv.BLIND_REF)} reference(s); the source has {n_self} "
                    f"self-citation(s)")
    if bv.BLIND_LINK not in text:
        errs.append("main document does not blind the archive links")
    for tag in ("dc:creator", "cp:lastModifiedBy"):
        hit = re.search(rf"<{tag}>([^<]+)</{tag}>", core)
        if hit:
            errs.append(f"main document properties name {hit.group(1)!r} ({tag})")
    return errs


def check_v4(t: str, cover: str | None, built: Path | None, R: dict, E: dict) -> tuple[list[str], str]:
    import build_d_v4 as bv
    errs: list[str] = []
    S = bv.sections(t)
    n = bv.counts(t)
    want, conditions = v4_wants(R, E)
    errs += [f"wording not supported by the outputs: {x}" for x in conditions]
    abstract, main, legend = S["Abstract"], bv.main_text(t), S["Figure legend"]
    scanned = abstract + "\n" + main + "\n" + legend
    for label, w in want.items():
        if w not in scanned:
            errs.append(f"text: expected {label} as {w!r}")
    # every number is derived or a stated constant
    traced = set()
    for w in want.values():
        traced |= {x.replace(",", "") for x in re.findall(r"\d[\d,]*(?:\.\d+)?", w)}
    body = re.sub(CITE + r"|COVID-19", "", scanned)
    for x in re.findall(r"\d[\d,]*(?:\.\d+)?", body):
        x = x.replace(",", "").rstrip(".")
        if x not in traced and x not in CONSTANTS_V4:
            errs.append(f"untraced number: {x}")
    sys.path.insert(0, str(ROOT / "manuscript"))
    import make_d_extend_exhibits as mx
    if mx.table(E).strip() not in t:
        errs.append("Table 1 differs from the table rendered from the outputs")
    # journal limits
    title = bv.title(t)
    if n["main_words"] > 2000:
        errs.append(f"main text {n['main_words']} words > 2,000")
    if n["abstract_words"] > 250:
        errs.append(f"abstract {n['abstract_words']} words > 250")
    if n["refs"] > 20:
        errs.append(f"{n['refs']} references > 20")
    if not 1 <= n["keywords"] <= 7:
        errs.append(f"{n['keywords']} keywords; at most seven")
    if n["running_title_chars"] >= 70:
        errs.append(f"running title {n['running_title_chars']} characters; fewer than 70 allowed")
    if re.search(r"\b[A-Z]{2,}\b|\b[A-Z][a-z]*[A-Z]", title):
        errs.append(f"title contains an abbreviation: {title!r}")
    if re.search(CITE + r"|\[\d+\]", abstract):
        errs.append("citation in the abstract")
    if n["figures"] + n["tables"] > 3:
        errs.append(f"{n['figures']} figures and {n['tables']} tables: more than three display items")
    # references: numbered, cited in order of first citation, AMA form
    listed = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", S["References"])]
    if listed != list(range(1, len(listed) + 1)):
        errs.append(f"reference list numbered {listed}")
    before_refs = t[t.index("## Abstract"):t.index("## References")]
    if re.search(r"(?<![\w\]])\[\d+(?:[,–-]\d+)*\]", before_refs):
        errs.append("bracketed citation; the journal uses superscript numbers")
    order: list[int] = []
    for mm in re.finditer(CITE, before_refs):
        for part in mm.group(1).split(","):
            rng = [int(x) for x in re.split(r"[–-]", part)]
            for k in range(rng[0], rng[-1] + 1):
                if k not in order:
                    order.append(k)
    if sorted(order) != listed:
        errs.append(f"cited {sorted(order)} vs listed {listed}")
    if order != sorted(order):
        errs.append(f"references not in order of first citation: {order}")
    for k, e in re.findall(r"(?m)^(\d+)\. (.*)$", S["References"]):
        authors = e.split(". ")[0]
        if "et al" in authors and authors.split(", et al")[0].count(",") + 1 != 3:
            errs.append(f"reference {k}: AMA lists three authors before et al.")
        if "et al" not in authors and authors.count(",") + 1 > 6:
            errs.append(f"reference {k}: more than six authors without et al.")
        if re.search(r"\d{4};\d+", e) and "doi:10." not in e:
            errs.append(f"reference {k}: journal article without its DOI")
    if ANCHOR_DOI in S["References"] or re.search(r"Dear Editor|recently reported", t):
        errs.append("the manuscript opens by responding to a journal article")
    # figure and table: cited, in order of first citation
    fig, tab = re.search(r"Figure 1", main), re.search(r"Table 1", main)
    if not fig or not tab:
        errs.append("Figure 1 or Table 1 not cited in the main text")
    elif fig.start() > tab.start():
        errs.append("Table 1 cited before Figure 1")
    if re.search(r"Figure [2-9]|Table [2-9]", main):
        errs.append("a figure or table cited that does not exist")
    # wording
    for pat in CAUSAL_V4:
        hit = re.search(pat, scanned, flags=re.I)
        if hit:
            errs.append(f"causal wording: {hit.group(0)!r}")
    british = scanned.replace("World Health Organization", "")
    for pat in US_SPELLING:
        hit = re.search(pat, british, flags=re.I)
        if hit:
            errs.append(f"US spelling: {hit.group(0)!r}")
    methods = S["Methods"]
    methods_body = "\n".join(ln for ln in methods.splitlines() if not ln.startswith("#"))
    if "post hoc" not in methods_body or "post hoc" not in abstract:
        errs.append("the added analyses are not called post hoc in the abstract and Methods")
    if not all(x in methods for x in ("Claude (Anthropic)", "large language model", "full responsibility")):
        errs.append("the use of AI is not described in the Methods")
    # cover letter
    if cover is not None:
        if 'Theme 1, "Health financing and economics"' not in cover:
            errs.append("cover letter does not state Theme 1")
        if f'"{title}"' not in cover:
            errs.append("cover letter does not carry the manuscript title")
        counts = (f"{n['main_words']:,} words of main text, an abstract of {n['abstract_words']} words, "
                  f"{bv.number_word(n['keywords'])} keywords, {n['refs']} references")
        if counts not in cover:
            errs.append(f"cover letter counts differ: expected {counts!r}")
        for rid in V4_RELATED:
            if rid not in cover:
                errs.append(f"cover letter does not disclose {rid}")
        line = next((ln for ln in cover.splitlines() if "HPM-26-01517" in ln), "")
        if "this journal" not in line or "different topic" not in line:
            errs.append("cover letter does not say HPM-26-01517 is at this journal and differs in topic")
        for bad in V4_FORBIDDEN:
            if bad.lower() in cover.lower():
                errs.append(f"cover letter names {bad!r}")
    for bad in V4_FORBIDDEN:
        if bad.lower() in t.lower():
            errs.append(f"manuscript names {bad!r}")
    # the built set
    if built is not None:
        for name in V4_FILES:
            f_ = built / name
            if not f_.exists():
                errs.append(f"{name} not built")
            elif f_.stat().st_mtime < V4.stat().st_mtime:
                errs.append(f"{name} is older than the source; rerun submission/build_d_v4.py")
        if all((built / x).exists() for x in V4_FILES):
            main_doc, core = docx_text(built / "02_main_document.docx")
            errs += anonymisation_errors(main_doc, core, len(bv.self_citations(t)))
            if "Abstract" not in main_doc or "Figure legend" not in main_doc or "Table 1." not in main_doc:
                errs.append("main document lacks the abstract, table or figure legend")
            page, _ = docx_text(built / "01_title_page.docx")
            plain = re.sub(r"\*\*", "", bv.word_counts_line(n))
            for need in (bv.field(t, "Running title"), "0000-0002-4771-8285", plain, "Acknowledgements", "Funding",
                         "Conflict of interest"):
                if need not in page:
                    errs.append(f"title page lacks {need[:60]!r}")
            full, _ = docx_text(built / "03_manuscript_with_author_details.docx")
            if "Siddalingaiah" not in full or "10.5281/zenodo.24478545" not in full:
                errs.append("manuscript with author details lacks the author or the archive DOI")
            from PIL import Image
            with Image.open(built / "04_Figure_1.tif") as im:
                if round(im.info.get("dpi", (0, 0))[0]) < 300:
                    errs.append("Figure 1 below 300 dpi")
            letter, _ = docx_text(built / "05_cover_letter.docx")
            if "Theme 1" not in letter:
                errs.append("built cover letter does not state Theme 1")
    info = (f"{len(want)} derived passages and every number traced; Table 1 matches; main text {n['main_words']:,} "
            f"words (limit 2,000); abstract {n['abstract_words']} (250); {n['refs']} references (20) in order; "
            f"{n['keywords']} keywords (7); running title {n['running_title_chars']} characters (<70); Figure 1 "
            f"before Table 1; no causal wording; main document anonymised; title page and cover letter checked")
    return errs, info


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

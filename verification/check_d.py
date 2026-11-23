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
    if V3.exists():
        R3, E = R, extension_outputs()
        e3, info = check_v3(V3.read_text(encoding="utf-8"), V3_COVER.read_text(encoding="utf-8")
                            if V3_COVER.exists() else None, V3_DOCX, R3, E)
        if e3:
            print(f"FAILED (version 3): {len(e3)} problem(s)\n  " + "\n  ".join(e3))
            return 1
        print(f"PASSED (version 3): outputs equal a fresh run; {info}")
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


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

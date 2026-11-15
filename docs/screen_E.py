"""Title screen for paper E's novelty search (docs/novelty_search_E.md).

A title is screened in if it concerns tuberculosis (or a multi-disease
assessment of the 2025 cuts) AND the 2025 US reductions or funding cuts in
general. Screened-in titles are written to docs/screen_titles_E.txt and are
then read by hand; the rule only decides what is read, not what is concluded.
Usage: python -I docs/screen_E.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

D = Path(__file__).parent
TB = re.compile(r"tubercul|\bTB\b|\bMDR\b", re.I)
CUT = re.compile(r"USAID|PEPFAR|foreign (aid|assistance)|funding (cut|freeze|reduction|withdraw|loss|shock|halt)|"
                 r"aid (cut|freeze|withdraw)|stop.work|donor (funding|withdraw|transition|exit)|"
                 r"\b2025\b.*(cut|freeze|suspen)|(cut|freeze|suspen).*\b2025\b|US (government )?(funding|aid)|"
                 r"global health (funding|financing)", re.I)
MULTI = re.compile(r"(impact|effect|consequence|disruption)s? of .*(cut|freeze|withdraw|suspen)", re.I)


def main() -> int:
    hits = json.loads((D / "novelty_hits_E.json").read_text(encoding="utf-8"))
    c1 = json.loads((D / "novelty_hits.json").read_text(encoding="utf-8"))["C1"]
    pools = {k: v["records"] for k, v in hits.items()} | {"C1 (re-screened)": c1["records"]}
    seen, lines, n_in = set(), [], {}
    for k, recs in pools.items():
        n_in[k] = 0
        for r in recs:
            t = r["title"]
            key = t.lower().strip(" .")
            if (TB.search(t) and CUT.search(t)) or MULTI.search(t):
                n_in[k] += 1
                if key in seen:
                    continue
                seen.add(key)
                lines.append(f"[{k} {r['source'][:2]} {r['id']}] {r['year']} | {t} | {r.get('journal', '')}")
    (D / "screen_titles_E.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("screened in:", n_in, "| unique titles:", len(lines))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

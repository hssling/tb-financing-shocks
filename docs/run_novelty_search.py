"""Run the pre-registered novelty searches (docs/novelty_search.md, Section 1.3).

PubMed (E-utilities) and Europe PMC; results written to docs/novelty_hits.json
with title, journal, year and identifiers. Standard library only.
Usage: python -I docs/run_novelty_search.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).with_name("novelty_hits.json")
UA = {"User-Agent": "novelty-search/1.0"}

QUERIES = {
    "C1": ('tuberculosis AND (USAID OR "foreign aid" OR "foreign assistance" OR "donor funding" OR '
           '"development assistance" OR PEPFAR) AND (cut* OR reduction* OR withdraw* OR suspension OR '
           'freeze OR termination)', 2025),
    "C2": ('tuberculosis AND ("domestic financing" OR "domestic funding" OR "domestic resource*") AND '
           '(donor OR USAID OR "Global Fund") AND (replace* OR substitut* OR transition OR fill*)', 2020),
    "D1": ('(multidrug-resistant tuberculosis OR rifampicin-resistant OR MDR-TB OR RR-TB) AND (BPaL OR BPaLM '
           'OR pretomanid OR "short regimen" OR "shorter regimen" OR "all-oral") AND (cost* OR expenditure* '
           'OR budget* OR "cost per patient")', 2019),
    "D2": ('(MDR-TB OR RR-TB) AND ("expenditure per patient" OR "cost per patient treated" OR "unit cost*") '
           'AND (country OR countries OR WHO OR "national programme")', 2015),
}


def get(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def pubmed(q: str, since: int) -> list[dict]:
    term = f"({q}) AND ({since}:3000[dp])"
    ids = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmax": 300, "retmode": "json"}))["esearchresult"]["idlist"]
    out = []
    for i in range(0, len(ids), 150):
        time.sleep(0.4)
        s = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(ids[i:i + 150]), "retmode": "json"}))["result"]
        for pid in ids[i:i + 150]:
            r = s.get(pid, {})
            out.append({"source": "pubmed", "id": pid, "title": r.get("title", ""),
                        "journal": r.get("fulljournalname", ""), "year": r.get("pubdate", "")[:4]})
    return out


def europepmc(q: str, since: int) -> list[dict]:
    query = f"({q}) AND PUB_YEAR:[{since} TO 3000]"
    d = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": query, "format": "json", "pageSize": 300, "resultType": "lite"}))
    return [{"source": "europepmc", "id": r.get("id"), "title": r.get("title", ""),
             "journal": r.get("journalTitle", r.get("bookOrReportDetails", {}).get("publisher", "")),
             "year": r.get("pubYear", ""), "src": r.get("source")}
            for r in d.get("resultList", {}).get("result", [])]


def main() -> int:
    results = {}
    for k, (q, since) in QUERIES.items():
        pm, ep = pubmed(q, since), europepmc(q, since)
        seen, merged = set(), []
        for r in pm + ep:
            key = r["title"].lower().strip(" .")
            if key and key not in seen:
                seen.add(key)
                merged.append(r)
        results[k] = {"query": q, "since": since, "pubmed": len(pm), "europepmc": len(ep),
                      "unique": len(merged), "records": merged}
        print(f"{k}: PubMed {len(pm)}, Europe PMC {len(ep)}, unique {len(merged)}")
    OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

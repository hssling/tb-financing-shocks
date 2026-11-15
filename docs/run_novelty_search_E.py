"""Run the pre-registered novelty searches for paper E (docs/novelty_search_E.md, Section 1.3).

Reuses the PubMed and Europe PMC functions of run_novelty_search.py. Europe PMC
is paged with its cursor up to 1,000 records per query, because the single
300-record page used for papers C and D bound for three of their four queries.
Results: docs/novelty_hits_E.json. Standard library only.
Usage: python -I docs/run_novelty_search_E.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run_novelty_search as base                     # noqa: E402

OUT = Path(__file__).with_name("novelty_hits_E.json")
QUERIES = {
    "E1": ('tuberculosis AND (USAID OR PEPFAR OR "foreign aid" OR "foreign assistance" OR "US funding" OR '
           '"funding cut*" OR "aid cut*" OR "donor funding") AND (notification* OR "case finding" OR '
           '"case detection" OR "case notification*" OR testing OR diagnos* OR "treatment initiation" OR '
           '"service delivery" OR "service disruption*" OR disruption*)', 2025),
    "E2": ('tuberculosis AND (surveillance OR "health information system*" OR "data quality" OR '
           '"data system*" OR reporting OR DHIS2) AND (USAID OR PEPFAR OR "foreign assistance" OR '
           '"foreign aid" OR "funding cut*" OR "aid cut*")', 2025),
}
CAP = 1000


def europepmc_all(q: str, since: int) -> tuple[list[dict], int]:
    query = f"({q}) AND PUB_YEAR:[{since} TO 3000]"
    out, cursor, hit = [], "*", 0
    while len(out) < CAP:
        d = base.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": query, "format": "json", "pageSize": 200, "resultType": "lite", "cursorMark": cursor}))
        hit = d.get("hitCount", 0)
        rows = d.get("resultList", {}).get("result", [])
        out += [{"source": "europepmc", "id": r.get("id"), "title": r.get("title", ""),
                 "journal": r.get("journalTitle", ""), "year": r.get("pubYear", ""), "src": r.get("source")}
                for r in rows]
        nxt = d.get("nextCursorMark")
        if not rows or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.3)
    return out, hit


def main() -> int:
    results = {}
    for k, (q, since) in QUERIES.items():
        pm = base.pubmed(q, since)
        ep, hits = europepmc_all(q, since)
        seen, merged = set(), []
        for r in pm + ep:
            key = r["title"].lower().strip(" .")
            if key and key not in seen:
                seen.add(key)
                merged.append(r)
        results[k] = {"query": q, "since": since, "pubmed": len(pm), "europepmc": len(ep),
                      "europepmc_hitcount": hits, "unique": len(merged), "records": merged}
        print(f"{k}: PubMed {len(pm)}, Europe PMC {len(ep)} of {hits}, unique {len(merged)}")
    OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

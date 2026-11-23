"""Audit every reference in papers C and D against Crossref and the live web.

For each reference with a DOI: fetch Crossref metadata and compare the first
author's surname, the year, volume, issue, first page or article number, and
title words; report any mismatch. For each URL: report the HTTP status.
Network use: Crossref API, doi.org and the cited URLs only.

Usage: python -I verification/audit_references.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = {"C": ROOT / "manuscript" / "manuscript_c.md", "D": ROOT / "manuscript" / "paper_d_letter.md",
          "D version 3": ROOT / "manuscript" / "paper_d_letter_v3.md"}
PAPERS = {k: v for k, v in PAPERS.items() if v.exists()}
UA = {"User-Agent": "reference-audit/1.0 (mailto withheld)"}
# Crossref is known to be wrong for some records; PubMed-verified exceptions go here.
KNOWN = {}


def refs(path: Path) -> list[tuple[int, str]]:
    t = path.read_text(encoding="utf-8")
    i = t.index("## References"); j = t.index("\n## ", i + 5)
    return [(int(n), e) for n, e in re.findall(r"(?m)^(\d+)\. (.*)$", t[i:j])]


def crossref(doi: str) -> dict | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://api.crossref.org/works/{doi}", headers=UA), timeout=40) as r:
            return json.load(r)["message"]
    except Exception:
        return None


def datacite(doi: str) -> dict | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://api.datacite.org/dois/{doi}", headers=UA), timeout=40) as r:
            a = json.load(r)["data"]["attributes"]
    except Exception:
        return None
    return {"creator": a["creators"][0]["name"], "year": str(a["publicationYear"]),
            "version": a.get("version") or "", "title": a["titles"][0]["title"]}


def bibliographic(entry: str) -> str | None:
    """DOI of Crossref's best match for a reference string, if its title agrees."""
    q = urllib.parse.quote(entry[:300])
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://api.crossref.org/works?query.bibliographic={q}&rows=1", headers=UA), timeout=40) as r:
            item = json.load(r)["message"]["items"][0]
    except Exception:
        return None
    title = norm((item.get("title") or [""])[0]).split()
    return item["DOI"] if title and sum(w in norm(entry) for w in title) / len(title) > 0.8 else None


def status(url: str) -> str:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return str(r.status)
        except urllib.error.HTTPError as e:
            if method == "GET":
                return str(e.code)
        except Exception as e:                                   # noqa: BLE001
            if method == "GET":
                return f"error {type(e).__name__}"
    return "?"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def main() -> int:
    problems = 0
    for key, path in PAPERS.items():
        print(f"===== Paper {key}")
        for n, e in refs(path):
            doi = re.search(r"(?:doi:\s?|https://doi\.org/)(10\.\S+?)\.?$", e)
            urls = re.findall(r"https?://\S+?(?=\s|\)|$)", e)
            notes = []
            if not doi and re.search(r"\b(19|20)\d\d; \d+", e):
                # IJTLD style: journal articles carry no DOI. Find the record by
                # bibliographic search, then audit it as if the DOI were given.
                found = bibliographic(e)
                if found:
                    print(f"        [{n}] no DOI in the entry; Crossref match {found}")
                    doi = re.match(r"(.*)", found)
                else:
                    notes.append("no Crossref match for an article without DOI")
            if doi:
                d = doi.group(1).rstrip(".")
                m = crossref(d)
                time.sleep(0.3)
                if m is None and d.startswith("10.5281/"):
                    # Zenodo DOIs are registered with DataCite, not Crossref
                    dc = datacite(d)
                    if dc is None:
                        notes.append("DOI NOT FOUND in DataCite")
                    else:
                        if dc["creator"].split(",")[0].lower() not in e.lower():
                            notes.append(f"creator DataCite '{dc['creator']}'")
                        if dc["year"] not in e:
                            notes.append(f"year DataCite {dc['year']}")
                        if dc["version"] and dc["version"].lstrip("v") not in e:
                            notes.append(f"version DataCite {dc['version']}")
                        tw = [w for w in norm(dc["title"]).split() if len(w) > 4][:6]
                        if sum(w not in norm(e) for w in tw) > 1:
                            notes.append(f"title DataCite: {dc['title'][:70]}")
                elif m is None:
                    notes.append("DOI NOT FOUND in Crossref")
                else:
                    fam = (m.get("author") or [{}])[0].get("family", "")
                    yr = str((m.get("issued", {}).get("date-parts") or [[None]])[0][0])
                    vol, iss = m.get("volume"), m.get("issue")
                    page = (m.get("page") or m.get("article-number") or "").split("-")[0]
                    title = (m.get("title") or [""])[0]
                    if fam and fam.split()[0].lower() not in e.lower() and d not in KNOWN:
                        notes.append(f"first author Crossref '{fam}'")
                    if yr not in e:
                        notes.append(f"year Crossref {yr}")
                    if vol and not re.search(rf"\b{re.escape(vol)}\b", e):
                        notes.append(f"volume Crossref {vol}")
                    if iss and f"({iss})" not in e and f" {iss}" not in e:
                        notes.append(f"issue Crossref {iss}")
                    if page and page not in e:
                        notes.append(f"first page/article Crossref {page}")
                    tw = [w for w in norm(title).split() if len(w) > 4][:6]
                    miss = [w for w in tw if w not in norm(e)]
                    if len(miss) > 1 and d not in KNOWN:
                        notes.append(f"title words missing {miss} (Crossref: {title[:70]})")
                st = status(f"https://doi.org/{d}")
                if not st.startswith(("2", "3")):
                    notes.append(f"doi.org status {st}")
            for u in urls:
                if "doi.org" in u:
                    continue
                st = status(u.rstrip(".,;"))
                if not st.startswith(("2", "3")):
                    notes.append(f"URL {u[:60]} status {st}")
            if not doi and not urls:
                notes.append("no DOI or URL")
            problems += bool(notes)
            print(f"  [{n:>2}] {'OK' if not notes else '; '.join(notes)}  | {e[:70]}")
    print(f"\n{problems} reference(s) with notes")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

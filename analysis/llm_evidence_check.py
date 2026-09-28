#!/usr/bin/env python3
"""Do LLMs invent languages? Check the evidence of the LLM-curated list (slide "Do LLMs invent languages?").

Inputs (sibling repos):
  ../../PL-ultimate-llm/web/dist/data/index.json          site index (14,242 pages, sources per page)
  ../../hopl-scrapping/exports/pl-graph/nodes.csv         HOPL names (8,509)
  ../../PL-ultimate-llm/swh-syntax-identification/syntaxes/syntaxes.json   Synid syntaxes (1,114)

Steps (network: Wikipedia API, GitHub API via `gh`, plain HTTP for other links):
  1. split the site pages into union-only / both / LLM-only;
  2. Wikipedia evidence: page exists? disambiguation? short description (batched API, 50 titles per call);
  3. GitHub evidence: does the repository exist (`gh api repos/<owner>/<repo>`);
  4. other evidence: HTTP status after redirects;
  5. exact (normalised) name match against HOPL and Synid;
  6. draw a random sample (seed 7) of 40 "unverified" LLM-only names for a manual / web-search check.

Outputs go to ./out/. Run from this directory:  python3 llm_evidence_check.py
"""
import collections
import concurrent.futures
import csv
import json
import random
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SANDBOX = HERE.parents[1]
INDEX = SANDBOX / "PL-ultimate-llm/web/dist/data/index.json"
HOPL = SANDBOX / "hopl-scrapping/exports/pl-graph/nodes.csv"
SYNID = SANDBOX / "PL-ultimate-llm/swh-syntax-identification/syntaxes/syntaxes.json"
OUT = HERE / "out"
UPSTREAM_EXCLUDED = {"llm", "repo", "manual_add"}
LANG_WORDS = ["language", "programming", "dialect", "notation", "dsl", "assembler", "compiler", "lisp",
              "basic", "fortran", "cobol", "algol", "calculus", "interpreter", "syntax", "shell",
              "scripting", "query", "markup", "prolog", "pascal", "smalltalk", "forth"]
BROWSER_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/124 Safari/537.36"}
WIKI_UA = {"User-Agent": "PLCatalogEvidenceCheck/1.0 (https://github.com/acherm/PL-ultimate-llm; batched API check)",
           "Content-Type": "application/x-www-form-urlencoded"}


def norm(name):
    return re.sub(r"[^a-z0-9+#]", "", name.lower())


def wiki_title(url):
    p = urllib.parse.urlparse(url)
    if not p.netloc.lower().endswith("en.wikipedia.org") or not p.path.startswith("/wiki/"):
        return None
    return urllib.parse.unquote(p.path[len("/wiki/"):]).replace("_", " ").split("#")[0]


def check_wikipedia(titles):
    res = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        data = urllib.parse.urlencode({"action": "query", "titles": "|".join(batch), "redirects": 1,
                                       "prop": "pageprops|description", "ppprop": "disambiguation",
                                       "format": "json", "formatversion": 2, "maxlag": 5}).encode()
        for attempt in range(6):
            try:
                req = urllib.request.Request("https://en.wikipedia.org/w/api.php", data=data, headers=WIKI_UA)
                q = json.load(urllib.request.urlopen(req, timeout=30))["query"]
                break
            except urllib.error.HTTPError as e:
                time.sleep(int(e.headers.get("Retry-After") or 5 * (attempt + 1)))
        norm_map = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {r["from"]: r["to"] for r in q.get("redirects", [])}
        pages = {p["title"]: p for p in q["pages"]}
        for t in batch:
            t2 = norm_map.get(t, t)
            t3 = redir.get(t2, t2)
            p = pages.get(t3)
            if p is None or p.get("missing") or p.get("invalid"):
                res[t] = {"status": "missing"}
            else:
                res[t] = {"status": "disambiguation" if "disambiguation" in (p.get("pageprops") or {}) else "ok",
                          "desc": p.get("description", ""), "final": t3}
        time.sleep(1.0)
    return res


def check_github(repo):
    ok = subprocess.run(["gh", "api", f"repos/{repo}", "--silent"], capture_output=True).returncode == 0
    return repo, "200" if ok else "404"


def check_http(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=BROWSER_UA), timeout=20)
        return url, str(r.status)
    except urllib.error.HTTPError as e:
        return url, str(e.code)
    except Exception as e:  # noqa: BLE001 - we record the failure kind
        return url, "ERR:" + type(e).__name__


def main():
    OUT.mkdir(exist_ok=True)
    pages = json.load(open(INDEX))["languages"]
    upstream = lambda x: set(x["in_sources"]) - UPSTREAM_EXCLUDED  # noqa: E731
    llm = [x for x in pages if not x["taxonomy_only"]]
    both = [x for x in llm if upstream(x)]
    print(f"pages {len(pages)} = union-only {len(pages) - len(llm)} + both {len(both)} + LLM-only {len(llm) - len(both)}")

    titles = sorted({t for x in llm if (t := wiki_title(x["evidence_url"] or ""))})
    wiki = check_wikipedia(titles)
    gh_repos = {}
    for x in llm:
        p = urllib.parse.urlparse(x["evidence_url"] or "")
        parts = [s for s in p.path.split("/") if s]
        if p.netloc.lower().removeprefix("www.") == "github.com" and len(parts) >= 2:
            gh_repos[x["slug"]] = f"{parts[0]}/{parts[1]}"
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        gh = dict(ex.map(check_github, sorted(set(gh_repos.values()))))
    others = sorted({x["evidence_url"] for x in llm if x["evidence_url"] and not wiki_title(x["evidence_url"])
                     and x["slug"] not in gh_repos and x["evidence_url"].startswith("http")})
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        http = dict(ex.map(check_http, others))

    hopl = {norm(r["name"]) for r in csv.DictReader(open(HOPL))}
    syn = json.load(open(SYNID))["syntaxes"]
    synid = {norm(s["name"]) for s in syn} | {norm(a) for s in syn for a in s.get("aliases", [])}

    def evidence(x):
        u = x["evidence_url"] or ""
        t = wiki_title(u)
        if t:
            r = wiki[t]
            if r["status"] == "missing":
                return "broken"
            if r["status"] == "disambiguation":
                return "off-topic"
            if not r["desc"]:
                return "ok"
            return "ok-language" if any(k in r["desc"].lower() for k in LANG_WORDS) else "off-topic"
        if x["slug"] in gh_repos:
            return "ok" if gh.get(gh_repos[x["slug"]]) == "200" else "broken"
        c = http.get(u)
        if c is None or c in ("404", "410", "500", "522", "526") or c.startswith("ERR"):
            return "broken"
        return "ok" if c == "200" else "indeterminate"

    rows = [{"name": x["name"], "slug": x["slug"], "evidence_url": x["evidence_url"], "model": x["model"],
             "llm_only": not upstream(x), "evidence": evidence(x),
             "in_hopl": norm(x["name"]) in hopl, "in_synid": norm(x["name"]) in synid} for x in llm]
    json.dump(rows, open(OUT / "llm_verdicts.json", "w"), indent=1)

    wiki_rows = [(r, wiki_title(r["evidence_url"] or "")) for r in rows]
    wiki_rows = [(r, t) for r, t in wiki_rows if t]
    for label, keep in [("all", lambda r: True), ("LLM-only", lambda r: r["llm_only"])]:
        sub = [(r, t) for r, t in wiki_rows if keep(r)]
        c = collections.Counter(wiki[t]["status"] for _, t in sub)
        print(f"Wikipedia evidence ({label}): {len(sub)} links, {dict(c)}, missing {100 * c['missing'] / len(sub):.0f}%")
    print("GitHub repos:", collections.Counter(gh.values()), "| other links:", collections.Counter(http.values()).most_common(6))
    lo = [r for r in rows if r["llm_only"]]
    print("LLM-only", len(lo), "in HOPL", sum(r["in_hopl"] for r in lo), "in HOPL or Synid",
          sum(r["in_hopl"] or r["in_synid"] for r in lo))
    unverified = [r for r in lo if not (r["in_hopl"] or r["in_synid"]) and r["evidence"] in ("broken", "off-topic")]
    print("unverified (broken or off-topic evidence, no HOPL/Synid match):", len(unverified))
    random.seed(7)
    json.dump(random.sample(unverified, 40), open(OUT / "unverified_sample.json", "w"), indent=1)


if __name__ == "__main__":
    main()

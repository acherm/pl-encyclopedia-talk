# Towards an Encyclopedia of Programming Languages Anchored in Software Heritage & CodeCommons

*Every Programming Language, with Its Real Programs*. Slogan: *Every language with its programs, every program with its language.*

**Online: https://blog.mathieuacher.com/pl-encyclopedia-talk/** · PDF: https://blog.mathieuacher.com/pl-encyclopedia-talk/talk.pdf

CodeCommons plenary meeting, Inria Paris, 28 September 2026. Talk by Mathieu Acher. 20 minutes, reveal.js slides written in Markdown (same setup as
`../PLs-AI-talk`), with a **Beamer-like theme** (Madrid/whale flavour): frame-title band, three-part
footline with frame numbers, blue/red/green blocks, triangle bullets, booktabs tables, Latin Modern fonts.

## Run it

```bash
cd PL-catalog-talk
python3 serve.py            # http://localhost:8000
```

reveal.js is vendored in `reveal/`, so everything works offline.

- `S`: speaker view (notes + timer). Every slide has notes with `⏱ T+` markers
- `F`: fullscreen, `O`: overview (for the backup slides), `B`: black screen
- Serve it over HTTP (not `file://`): the SVG diagrams are fetched and inlined at load time so that
  they use the Latin Modern font; opened as a file they still display, in the fallback font

## PDF

`talk.pdf` (44 pages: 34 + 10 backup, 1280×720) is built from the slides with reveal's print mode:

```bash
npm install        # once: puppeteer-core (drives your local Google Chrome)
npm run pdf        # → talk.pdf
```

`build-pdf.mjs` starts `serve.py`, opens `index.html?print-pdf`, waits for reveal, the fonts and the
inlined SVGs, then prints. Set `CHROME=/path/to/chrome` if Chrome is not in `/Applications`.
Rebuild it after every change to `slides.md`, then commit and push: GitHub Pages serves `main` as is
(`.nojekyll`), slides and PDF included.

## Plan and timing: 34 slides + 10 backup

| T+ | Section | Slides |
|----|---------|--------|
| 0 | Title · **the prototype today** (live-site screenshots) · **features** (tools & agents: find languages, label programs, find programs) · the dream + slogan · **why now, why it matters** · reality check: *where are all the Icon programs?* (`.icn` vs `.icon`) | 1–6 |
| 4:45 | **1. Four mirrors, no code**: HOPL · PL-ultimate · PL-ultimate-llm (the Icon commit) · do LLMs invent languages? · SWH extensions · diagnosis matrix | 7–13 |
| 9 | **2. The vision, made concrete**: ontology · UML cardinalities · two gaps in numbers · **PLI, formally** (*f* : *P* × *E* → 2<sup>*L*</sup>, learnt iteratively, labels as regression tests) · PLI funnel (Tree-sitter, team byline) | 14–19 |
| 14:45 | **3. Zoom in** (MSR-style): pipeline, three stories (`.fsf` = embedded DSL), COBOL, `.rpgle`, the LLM judge, method | 20–27 |
| 19:30 | **4. Making it real**: contributions (trace everything; the workflow will be redesigned) · challenges (PLI first; CodeCommons extractors) · how to help · **catch them all!** (1.5% caught: a pipeline gap) · **roadmap** (0 · register a domain name + official initiative?, 1 · start small, 2 · grow, 3 · scale; one reproducible pipeline throughout) | 28–33 |
| 24 | Closing + slogan + thanks | 34 |
| — | Backup: polysemy (`.m`), central idea, architecture, sources table, a cited SWHID, LLM protocol, `.fsf`, review app, review schema | B1–B9 |

As written this runs about **23–24 minutes**. To get back to 20, in this order: show slide 3 (features)
without reading it; say slide 8 (PL-ultimate) in one sentence; skip slide 12 (SWH extensions table: the
"two gaps" slide carries the numbers); skip slide 24 (COBOL "how you count": the `.rpgle` slide and note 5
of the UML slide make the same point); shorten slide 5 to the two arguments; on slide 18 (PLI, formally)
show the loop and skip reading the definitions.

## Numbers behind "Do LLMs invent languages?" (slide 11)

`analysis/llm_evidence_check.py` (outputs in `analysis/out/`, run of 2026-09-27):

- The 14,242 site pages = 10,400 union-only + 2,439 in both the union and the LLM list + 1,403 LLM-only.
  The LLM list started from one entry (Kotlin, 2025-10-22) and was never seeded from the union.
- Wikipedia evidence (2,473 links, 2,112 titles, checked with the Wikipedia API): 696 point to a page that
  does not exist (28%; 40% for LLM-only names), 21 to disambiguation pages.
- GitHub evidence: 503 of 554 repositories exist. Other links: 644 of 797 resolve; 53 × 404, 50 dead domains,
  ~45 undetermined (403/429).
- LLM-only names also found in HOPL (254) or Synid (27): 277. Unverified (broken or off-topic evidence and no
  corroboration): 465.
- Random sample of 40 unverified names, checked by web search (`out/unverified_sample_verdicts.json`, one URL
  per verdict): 27 exist, 9 exist under another name, 2 are not languages (NATJ, Brython), 2 not found
  (BASIC-D, Oxymoron). 2/40 = 5%, Wilson 95% CI 1.4–16.5% → ≈ 23 invented names (6–77) of 3,842, i.e. 0.6%
  (at most 2%), assuming corroborated names or names with working evidence are real.

## Files

- `slides.md`: all content (slide separator `---`, speaker notes after `Note:`)
- `index.html`: reveal.js config (1280×720, no transition, no progress bar) plus two small scripts:
  the Beamer footline (author · title · venue · frame number; backup frames are numbered B1, B2…),
  edited via the `FOOT_A/B/C` constants, and the inlining of `img[data-inline]` SVGs
- `talk.css`: the Beamer-like theme. A frame's first `##` becomes the frame-title band; add a frame
  subtitle with `## Title <span class="sub">Subtitle</span>`. Blocks: `.card` / `.findings` (the `h3`
  is the block title; `.red` = alertblock, `.green` = exampleblock). Slide classes: `titlepage`,
  `section-slide`, `closing`, `backup-start` (numbering of backup frames). Also `.cols`, `.cards`
  (`.three`, `.four`), `.pill`, `.evcard`, `.umlnotes`, `img.shot`, `table.tight`
- `analysis/`: the evidence check of the LLM list (script + outputs), see above
- `assets/fonts/`: Latin Modern Sans and Mono (the Beamer/LaTeX default typeface), copied from TeX Live;
  GUST Font License, free to redistribute
- `assets/img/uml-cardinalities.svg`: UML class diagram of ProgrammingLanguage, FileExtension, Content
  (`swh:1:cnt`), Occurrence (qualified SWHID) and the Attribution association class, with multiplicities;
  numbered badges refer to the six notes next to it on slide 13
- `assets/img/ontology.svg`: the ontology (Language, Source, Extension, Attribution = evidence, PLI method,
  Review, Program, Occurrence, Evidence of absence, Paper). Hand-written SVG, dark theme
- `assets/img/pli-loop.svg`: the iterative loop of the formalization slide (pick programs → synthesize *f* →
  validate & review → grow *D*)
- `assets/img/pli-funnel.svg`: the multi-level PL-identification funnel (graph → content → classifiers → LLM → humans)
- `assets/img/cobol-per-year.svg`: files per year with a COBOL extension (`.cbl .CBL .cob .COB .cpy .CPY`,
  2002–2023), summed from `../PL-roberto/nb_extensions_alphanum.csv`; the red 2021 bar (121K) is ≈ the
  110K-file synthetic test fixture found in the COBOL study
- `assets/img/architecture.svg`: the "how the pieces fit" diagram (now in backup)
- `assets/live/`: screenshots of the live PL Catalog (build of 2026-06-12: home, review queue, samples…) and of
  the Icon commit on GitHub (`commit-icon-parts.png`: header + `pl_list.txt` diff + `meta.json`)
- `assets/shots/`: screenshots of the PL Catalog (local build, `web/dist/`) and of the HOPL graph viewer
- `assets/figs/`: figures and review-app screenshots from the three extension studies
- `assets/img/logos/`: copied from PLs-AI-talk

## Where the material comes from

| What | Where |
|------|-------|
| PL-ultimate-llm + PL Catalog site + SWH evidence prototype | `../PL-ultimate-llm` (branch `swh-evidence-v1`); live at https://blog.mathieuacher.com/PL-ultimate-llm/ |
| **Extension studies** (COBOL, fsf, RPG) | also in `../PL-ultimate-llm`: `docs/{cobol,fsf,rpgle}_swh_study.{md,pdf}`, toolkits in `tools/{cobol,fsf,rpgle}/`, playbook in `docs/swh_extension_study_playbook.md` |
| Design notes (vision, gaps) | `../PL-ultimate-llm/docs/SOURCES_AND_SWH_EVIDENCE.md`, `SWH_EXTENSIONS_DECISIONS.md`, `PHASE2_OVERNIGHT.md` |
| Contribution flows | `../PL-ultimate-llm/docs/{add_pl,labelling_persistence,sample_requests,reviews,cli_roadmap}.md` |
| HOPL scrape + graph viewer | `../hopl-scrapping` (`exports/pl-graph/`, `viewer/pl-graph/`) |
| PL-ultimate (~12K languages, 7 sources) | `../PL-ultimate` (github.com/acherm/PL-ultimate) |
| Roberto's SWH extension CSV | `../PL-roberto/nb_extensions_alphanum.csv` (SWH-MSR-ARV: Desmazières, Di Cosmo, Lorentz, MSR 2025) |
| The vision video, transcribed | `../PL-vision-codecommons/transcript.txt` |
| SWH's Synid (syntax identification, CodeCommons) | `../PL-ultimate-llm/swh-syntax-identification/` (8 strategies, `syntaxes/syntaxes.json`: 1,114 syntaxes) |

Numbers were checked against those sources on 2026-09-27: `data/pl_list.txt` (3,862 languages),
`git log` trailers (3,846 `turn: add` commits, by model), `hopl-scrapping/exports/pl-graph/summary.json`
and `nodes.csv`, `data/derived/swh_extensions_popularity.csv`, `data/derived/pl_taxonomy/ext_claim.csv`,
`data/derived/pli_missing_from_master.csv` (151 Synid syntaxes in none of our catalogs), HOPL's
edges for Icon and COBOL, and the three study reports. Site-level counts (14,242 pages, ~190 languages with SWH samples)
come from the live PL Catalog home page.

## Before the talk

- [ ] Slide 6 (Icon): the `.icn` / `.icon` breakdown comes from GitHub code search (default branches), not
      from SWH; confirm on an SWH sample before quoting it as an SWH fact
- [ ] Slides 19 and 34: check the spelling "Axel Amour N'cho" (given as "Axel Amour N cho")
- [ ] Slide 31 ("How you can help"): decide whether to name the people already on each case study
      (COBOL, `.fsf`/neuro, `.m`, RPG). They are only mentioned in the speaker notes for now
- [ ] Slide 33: the roadmap (no dates yet) and the three "decisions for today" are a proposal; adjust to what
      has already been discussed with SWH / CodeCommons
- [ ] Optional live demo: PL Catalog (`/l/icon-…`, `/ext/m/`, a Perl page with SWH samples) and the
      HOPL viewer (`cd ../hopl-scrapping && python3 -m http.server`, then `/viewer/pl-graph/`)

# DevEval projects: what is there and how to pick one

> Written 2026-10-14. Sources, each opened for this note:
> - **Upstream:** `open-compass/DevEval` on GitHub, `README.md` and `benchmark_data/README.md`
>   ("Dataset Overview" table), and the folder listing of `benchmark_data/<language>/`, fetched with
>   `curl` on 2026-10-14 (default branch; the commit was not recorded).
> - **Harbor copy:** `download/deveval/` (Harbor dataset `deveval@1.0`, downloaded 2026-10-12): each
>   task's `task.toml` and its `deveval_source_repo/repo_config.json`.
> - **Here:** `clean-tasks-check.json` (round 6) and the spec word counts from `repo_config.json` paths.

## 1. How many projects

- **Upstream DevEval (originally named DevBench) has 22 projects** ("22 curated repositories across 4
  programming languages", upstream `README.md` line 23). The folder listing agrees: Python 10, C/C++ 5,
  Java 5, JavaScript 2.
- **Harbor's copy has 21.** `TextCNN` (Python, deep learning) is missing. Why Harbor left it out is
  not checked.
- Harbor makes **3 tasks per project** (implementation, unit testing, acceptance testing): 63 tasks.
  Only the *implementation* task fits our study. Upstream's software-design and environment-setup
  tasks are not in Harbor.

## 2. Are projects tagged for selection?

- **Harbor: in practice, no.** All 63 `task.toml` files carry `difficulty = "hard"` and
  `category = "software-development"`. The only tags that differ are the language, the phase and the
  repository name (for example `["deveval", "phase:implementation", "python", "repo:lice"]`). They
  narrow by language and nothing else.
- **Upstream: one useful label, in a README table, not as machine tags.** `benchmark_data/README.md`
  gives each project a **Domain** (ALGO, SE, NLP, API, DB, CV, DL, Web) plus code files, code lines,
  code tokens, acceptance and unit test counts, and unit-test coverage. That table is the closest thing
  to selection criteria. It is copied into §3.
- Nothing in either source marks the trait we care about: how much the tests rely on details the
  specification does not state. We measured that ourselves for three projects
  (`test-classification.json`: on `lice` only 3 of 31 tests are fully stated in the spec).

## 3. All 22 projects

Domain, code size and test counts: upstream table. Spec words: the four documents (PRD, UML class,
UML sequence, architecture design), counted here. "Usable here" is round 6: the reference passes every
hidden test and doing nothing passes none, after repackaging (`clean-tasks-check.json`).

| Project (Harbor name) | Language | Domain | Code files | Code lines | Unit / acceptance tests | Spec words | Usable here |
|---|---|---|---|---|---|---|---|
| arxiv-digest | Python | SE, API | 1 | 198 | 38 / 4 | 1 198 | yes; **used** (rounds 7, 9, 11) |
| chakin | Python | NLP | 1 | 162 | 1 / 1 | 982 | yes |
| geotext | Python | NLP | 2 | 470 | 4 / 5 | 895 | yes |
| hone | Python | SE | 4 | 274 | 7 / 5 | 1 699 | yes; **used** (pilot) |
| hybrid-images | Python | ALGO, CV | 1 | 144 | 19 / 1 | 760 | **kept for round 12 (owner, 2026-10-14)**: reference passes 12 of 20 (20 tests: the acceptance test is named `test`, which the first count missed) |
| lice | Python | SE | 2 | 376 | 25 / 6 | 1 376 | yes; **used** (rounds 7, 11) |
| particle-swarm-optimization | Python | ALGO | 2 | 168 | 5 / 1 | 524 | yes |
| readtime | Python | ALGO | 3 | 284 | 8 / 4 | 827 | yes |
| stocktrends | Python | ALGO | 1 | 384 | 7 / 2 | 1 556 | yes; **used** (rounds 7, 8, 11) |
| *TextCNN* | Python | DL, NLP | 5 | 403 | 10 / 1 | — | not in Harbor |
| area-calculation | C/C++ | SE | 7 | 162 | 3 / 3 | 797 | not repackaged |
| graph-cpp | C/C++ | ALGO | 5 | 667 | 22 / 5 | 1 990 | not repackaged |
| logistic-system | C/C++ | SE | 7 | 630 | 17 / 7 | 3 005 | not repackaged |
| people-management | C/C++ | SE, DB | 6 | 540 | 9 / 7 | 1 434 | not repackaged |
| xlsx2csv | C/C++ | SE | 10 | 476 | 8 / 5 | 2 142 | not repackaged |
| actor-relationship-game | Java | ALGO, API | 8 | 493 | 16 / 4 | 1 274 | not repackaged (needs a TMDB key) |
| idcenter | Java | SE | 4 | 333 | 4 / 3 | 1 027 | not repackaged |
| image-similarity | Java | SE, CV | 3 | 382 | 2 / 2 | 1 377 | not repackaged |
| java-heap | Java | ALGO | 3 | 632 | 2 / 2 | 1 256 | not repackaged |
| redis-cache | Java | SE, DB | 9 | 779 | 17 / 1 | 1 472 | not repackaged |
| listen-now-frontend | JavaScript | Web | 6 | 232 | 0 / 1 | 997 | not repackaged |
| login-registration | JavaScript | Web | 6 | 223 | 0 / 3 | 1 395 | not repackaged |

Notes on the table:
- Upstream calls `login-registration` "register", `java-heap` "Leftist Trees and Fibonacci Heaps
  Comparison", `graph-cpp` "Graph BFS DFS" and `particle-swarm-optimization` "PSO".
- Upstream's test counts agree with the hidden-test counts we found for `lice` (31), `arxiv-digest`
  (42), `stocktrends` (9) and `hone` (12).

## 4. The four projects used so far (from each PRD's opening)

- **`lice`:** a command-line tool that writes a licence file (BSD, MIT, GPL and others) for a software
  project from templates, filling in the year and the organisation.
- **`hone`:** a Python package that converts a flat CSV file into nested JSON, with custom delimiters
  and schemas.
- **`arxiv-digest`:** a tool that queries the arXiv API by category, author, title and abstract,
  filters by how recently papers were published, and prints the results or saves them to CSV.
- **`stocktrends`:** a Python program that computes financial indicators (Renko, line break, point and
  figure charts from price data) for trend analysis.

## 5. Picking a project for a given test

- **Bigger specification:** the C/C++ projects are the largest (`logistic-system` 3 005 words,
  `xlsx2csv` 2 142, `graph-cpp` 1 990). All are below our `lend` task (2 120 words in 7 files) except
  `logistic-system`, and none is repackaged yet. DevEval cannot answer the scale question.
- **Tests stated in the specification:** not given by either source; classify the tests first, as in
  `test-classification.json`. Doing that before a run would show how much any format can help.
- **Cheap and Python-only:** `readtime`, `geotext`, `chakin` and `particle-swarm-optimization` are
  usable and unused; their specs are small (524 to 982 words).
- **Needs the network at test time:** `arxiv-digest` (the live arXiv service; see TRIAL §11) and
  `actor-relationship-game` (TMDB). Avoid them when a clean comparison matters.

## 6. Who owns the projects, and why the hidden tests check unstated details (2026-10-14)

Sources opened 2026-10-14: each project's own files in `download/deveval/python-<p>-implementation/environment/deveval_source_repo/`
(README, LICENSE, setup files); the paper arXiv:2403.08604 v1 HTML, §4.1 "Dataset Construction" and
Appendix C, read through a summarising fetch; the upstream repository's GitHub API record and all of its
issues (5, all closed).

**Layers.** The code belongs to independent open-source authors on GitHub. DevEval's team
(GitHub organisation `open-compass`; the authors' affiliations were not checked) picked the
repositories, wrote the four documents and prepared the tests. Harbor (laude-institute) only repackages
DevEval as Harbor tasks; it adds nothing to the specification or the tests.

| Project | Original repository (from the project's own files) |
|---|---|
| chakin | `chakki-works/chakin` (README image link) |
| geotext | `elyase/geotext` (README install line) |
| hybrid-images | `ReynoldZhao/Project1_Hybrid_Images` (README; MIT, "Copyright (c) 2019 ReynoldZhao") |
| lice | Jeremy Carbaugh / Sunlight Foundation (licence text; repository URL not in the files) |
| particle-swarm-optimization | `nathanrooy/particle-swarm-optimization` (README) |
| readtime | `alanhamlett/readtime` (README; "Copyright (c) 2016 by Alan Hamlett") |
| stocktrends | `chillaranand/stocktrends` (README install line) |
| hone, arxiv-digest | no author or URL in the files; not traced |

**Why the tests check things the documents do not state.** Per the paper (§4.1): repositories were taken
from "a GitHub dump"; annotators were given templates and wrote the design documents to correspond to
the existing code; they "were also required to run existing unit and acceptance tests, or to develop
additional tests". So the documents were written *from* the code and the tests come from (or were
written against) that code. Nothing checked that every name, string or default a test uses appears in
the documents. The paper's appendix (C.2, C.4) reports models getting names wrong and following the
original repositories' imports, but treats that as a model error, not a specification gap. The
upstream repository was last pushed 2024-05-30; none of its 5 issues raises the point.

**Community reports of the same problem elsewhere** (not about DevEval): NL2Repo-Bench issue #17
"Hidden tests require API surface that start.md never names" (2026-08-19; e.g. 28 of 30 symbols the
`funcy` tests call are absent from its specification) and #19 (three more tasks); its issue #21
reports grading images that contain the reference code (as DevEval's Harbor images do, TRIAL §3) and
#12 agent-written tests leaking into scoring (our round-8 fault). Records: `../zero2repo/TRIAL.md` §4.

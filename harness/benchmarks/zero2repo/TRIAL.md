# Trial record — Zero2Repo (formerly CodingBench, 2026)

> **Kind:** benchmark, with its own runner (`cbrun`) and a Harbor adapter · **State:** downloaded and
> read 2026-10-14, **not run** (installing its harness was blocked by the session's permission check;
> the owner decides) · **Recommendation: strongest candidate seen so far for "tests only check what the
> specification states"; worth a no-model check next (build one case as a Harbor task, run `nop`).**
> Asked by the owner after round 12 (DevEval tests depend on unstated details).
> Rules: no number that was not printed by a command here. Claims about the paper first came from a
> summarising fetch of the arXiv HTML (2026-10-14); on 2026-11-20 the full text (v3 PDF) was read and
> they were checked against it (§2).

## 1. Source

| | |
|---|---|
| Paper | arXiv:2609.38269, *Zero2Repo: Can Coding Agents Build Repositories from Scratch?* Yang, Shi, … Ai, Yang (26 authors), cs.SE. First seen as v2 (01 Oct 2026) through a summarising fetch; **full text of v3 (18 Oct 2026, 19 pages) read 2026-11-20**. Cited in the final report as `yang2026zero2repo` |
| Code / data | `github.com/OpenEdgeHQ/Zero2Repo`, created 2026-05-29, last push 2026-10-14, 11 stars (GitHub API, 2026-10-14) |
| Version tried | commit `0ecc523` (2026-10-14), shallow clone, 20 MB |
| Licence | **None found**: no LICENSE file; the README's "License" section says "See repository license terms". GitHub reports no licence. Redistribution is therefore not allowed by default; keep it in `download/` only |
| Downloaded to | `download/Zero2Repo/` (ignored by git) |

## 2. What a case is (read from `benchmark/cases/case001`, the README and the paper)

- **Agent sees:** `Full_PRD.md` (features with normal, boundary and failure cases), `Interface_Contract.md`
  (package name, public entry points, signatures, return and error types), sometimes
  `Hardware_Requirements.md`, and an empty `/app`.
- **Hidden:** an acceptance suite under `milestones/final/tests/`, run in a fresh offline container
  after an explicit submit. Binary reward (all tests pass or 0). No model judge.
- **Built from a real repository at a pinned commit** (`source/manifest.json`), with names
  **neutralised** so the model cannot recall it: case001 is `hukkin/tomli` renamed `tomlparse`, with a
  list of 57 "sensitive terms" (`tomli`, the author's name, URLs) kept out of the public files.
- **Traceability:** `coverage_matrix.json` maps feature ids (F01…) to capabilities; test files are
  per feature (`F01_acceptance.py` …); `review_verdict.json` records a scored review (e.g.
  `prd_accuracy` 5 with a rationale that "each [obligation] has a live hidden assertion").
- **Per the paper (v3 full text, §3.2; confirmed 2026-11-20):** acceptance tests "turn PRD feature points
  into executable checks against the interfaces fixed by the Interface Contract", and upstream tests are
  rewritten against these interfaces; expected outcomes are "computed without calling the candidate";
  adversarial validation requires implementations with injected defects or prohibited shortcuts to get
  zero reward; and structural checks "verify that requirements, interface references, and test references
  agree". *Not found in v3:* the summary's claim of one gap found after release (task 009 relies on
  `GIT_SSH`, not in the spec). Either v2 had it or the summary was wrong; v2 was not read.
- **No reference solution is shipped**, so a reference (`oracle`) check like DevEval's is not possible
  without rebuilding the upstream code under the new names.

## 3. The 17 cases (commit `0ecc523`)

Words: `wc -w` of the two public files. Test definitions: a regex count of test functions in the hidden
files (excluding helpers and `conftest`), **approximate**.

| Case | Upstream | Language | PRD words | Contract words | Test defs (approx.) | Review file |
|---|---|---|---|---|---|---|
| case001 | hukkin/tomli | Python | 3 715 | 870 | 302 | yes |
| case002 | envfilehq/python-envfile | Python | 5 011 | 1 917 | 272 | no |
| case003 | ymlcodecorg/ymlcodec | TypeScript | 5 130 | 1 633 | 399 | yes |
| case004 | pallets/itsdangerous | Python | 3 665 | 1 483 | 258 | yes |
| case005 | python-hyper/h11 | Python | 6 501 | 1 208 | 395 | yes |
| case006 | pallets/click | Python | 10 831 | 3 146 | 463 | no |
| case007 | pyauth/pyotp | Python | 3 920 | 998 | 80 | no |
| case008 | ada-url/ada | C++20 | 3 567 | 1 775 | 161 | no |
| case009 | git-lfs/git-lfs | Go | 9 879 | 3 483 | 492 | no |
| case010 | nltk/nltk | Python | 5 992 | 2 184 | 197 | no |
| case011 | jmespath/jmespath.py | Python | 5 982 | 826 | 296 | no |
| case012 | dmmulroy/anti-slop | TypeScript | 6 173 | 991 | 442 | no |
| case013 | membundle-memory/homebrew-tap | Go | 6 255 | 3 244 | 572 | no |
| case014 | navfilter/NAVFILTER | C11 | 8 651 | 4 673 | 320 | no |
| case015 | iczelia/balrogg | C99 | 5 069 | 1 158 | 169 | no |
| case016 | seyedehsanhadi/sloptrim | Python + Node.js | 11 682 | 7 087 | 263 | no |
| case017 | manishrjain/zroar | Zig | 5 296 | 1 244 | 234 | no |

**Against DevEval:** specifications are 4 585 to 18 769 words per case (PRD + contract) (DevEval: 524 to 3 005), so
they also reach the scale our `lend` task (2 120) does not. Tests are many per case (approx. 80 to 572
against DevEval's 2 to 42), but the reward is all-or-nothing; a per-test score would come from the
junit output, as we did for DevEval.

## 4. Community reports seen while choosing (GitHub issues, read 2026-10-14)

- **NL2Repo-Bench** (`multimodal-art-projection/NL2RepoBench`, 104 Python tasks, upstream tests used
  as they are): #17 "Hidden tests require API surface that start.md never names" (e.g. 28 of 30
  symbols the `funcy` tests call are absent from the 1 428-line spec), #19 more cases, #21 grading
  images contain the reference code (a `justext` submission without code scores 58 / 61), #12 the
  agent's own tests can leak into scoring. Same three faults we met in DevEval. Not downloaded.
- **Commit0** (`commit-0/commit0`, MIT, 54 Python libraries): the agent gets the API documentation and a
  skeleton with every signature, so tests and interface agree by construction, but the input is a code
  skeleton, not a specification to compile. #113: git history exposed the original code (fixed). Not
  downloaded.
- **Zero2Repo**: 5 issues, all closed, all about its own runner; #4 is a review of case006 (447 / 476
  tests, reward 0) asking maintainers to confirm unresolved contract points.

## 5. Next step (needs the owner)

1. Allow installing its harness in a separate venv (`download/.venv`), then
   `zero2repo-harbor --case-id case001` to make a Harbor task and run Harbor's `nop` agent: does it
   build, and does doing nothing score 0? No model call.
2. Read case001's hidden tests against its Interface Contract and classify them S/U/R/C as for DevEval
   (does the paper's claim hold?).
3. Only then one model run, with the owner's go-ahead.

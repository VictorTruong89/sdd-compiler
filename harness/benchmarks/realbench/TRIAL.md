# Trial record — RealBench

> **Kind:** benchmark + own pipeline · **State:** TRIED 2026-10-12 — **could not be downloaded** ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: reject, because it cannot be obtained.** No code, data or website address was
> found in the paper or by two web searches. Nothing was run.
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From the survey §2 and §8 (arXiv HTML read 2026-09-29): 61 Python repositories created after
Dec 2024; input is text requirements plus UML diagrams; measures Requirement@k, Architecture@k,
Completion@k, Execution@k, Pass@k; it evaluates plain LLM generation strategies, not tool-using agents.
**No repository link or licence was found in the paper text.**

## 1. Source

| | |
|---|---|
| Paper | Li, Deng, Zhang, Zhang, Shao, Zhao, Wang, Jin, Li, Liu, Fang, Dong, *RealBench: A Repo-Level Code Generation Benchmark Aligned with Real-World Software Development Practices*, arXiv:2604.22659; DOI 10.1145/3797106; listed as an FSE 2026 research paper. arXiv HTML read in full on 2026-10-12 (both halves) **through a summarising fetch** |
| Code / data URL | **Not found.** The paper says rubric instructions are "available on our website" and gives no address; the only GitHub link is `github.com` itself, as the source of the repositories |
| Version or commit tried | — |
| Licence (read where) | None stated for the data |
| Download size | — |
| Downloaded to | nothing downloaded |

## 2. The five questions

Answered **from the paper only** (summarised fetch); nothing could be checked on real data.

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | What does one task's specification look like? | Natural-language requirements for the repository (written by programmers or taken from READMEs) plus a two-level UML design (package diagram and class diagram) given to the model as JSON text. Average length: **not reported** | Paper |
| 2 | Can it be replaced by our three formats? | On paper, yes: requirements plus design is the same kind of input as DevEval's. *Cannot be tried* | — |
| 3 | Can it score a project built outside its pipeline? | Unknown. Tests are hand-written, about 50.05 per repository, 79.76 % line coverage (paper's figures). The harness is not described | Paper |
| 4 | What does it need to run? | Unknown | — |
| 5 | Which of our metrics does it give? | Completion rate, execution pass rate, test pass rate, Requirement@k, Architecture@k. The last two use a repository-summarising agent (DeepWiki) as an aid, i.e. a model in the scoring loop | Paper |

## 3. The one number

**None.** There is nothing to run.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | arXiv HTML, characters 0–100 000 and 100 000–end, asked for every code, data or website URL | None for RealBench |
| 2026-10-12 | Web search: the full title with "github dataset" | Paper, FSE listing, a citation page. No repository |
| 2026-10-12 | Web search: "RealBench … Jia Li Ge Li FSE 2026 github.com replication package" | Same. No repository |

Not done: writing to the authors; the ACM Digital Library page (it may list an artifact); the FSE
listing page itself.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **reject —
not obtainable.**
**Reason:** a benchmark that cannot be downloaded cannot be used, whatever its design. The proposal
named it as a candidate benchmark *and* platform; the report should say plainly that no artifact was
found on 2026-10-12.
**What we lose by this choice:** on paper it is the closest to our design after DevEval (requirements
plus UML, repositories newer than the models' training data, which DevEval lacks).
**To reopen:** check the ACM page for an artifact link, or e-mail the authors.

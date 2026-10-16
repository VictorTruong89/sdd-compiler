# Trial record — BaxBench (2025)

> **Kind:** benchmark (backend generation from an OpenAPI specification) · **State:** downloaded and
> read 2026-10-14, not run · **Recommendation: reject as our main benchmark** — the tests do target only
> stated endpoints, but each specification is tiny (66 to 387 words) and has 0 to 2 functional tests, so
> there is nothing for a compiler to consolidate.

## 1. Source

| | |
|---|---|
| Paper | arXiv:2502.11844, *BaxBench: Can LLMs Generate Secure and Correct Backends?* (not opened; title from the repository README) |
| Code | `github.com/logic-star-ai/baxbench`, MIT ("Copyright (c) 2025 SRI Lab, LogicStar.ai"), last push 2026-01-30, 105 stars (GitHub API, 2026-10-14) |
| Version tried | commit `de885cd` (2025-10-22), shallow clone, 16 MB, in `download/baxbench/` (ignored by git) |

## 2. What was measured

28 scenarios in `src/scenarios/*.py` (excluding `base.py`, `__init__.py`). Each holds an OpenAPI 3
specification (`_API_SPEC`), a short prose version (`_TEXT_SPEC`), functional tests (`func_test*`) and
security exploits. A task is a scenario times one of 14 frameworks (README).

- OpenAPI words per scenario (regex over `_API_SPEC`): 66 (`calculator`) to 387 (`recipes`).
- Functional tests per scenario (`^def func_test`): 0 (`pdf_to_text`) to 2; most have 1.
- Tests call the HTTP endpoints, request fields and status codes that the OpenAPI document names
  (read in `login.py`), so the "unstated name" problem of DevEval does not arise here.

## 3. Why not

The specification is one API document per task, far below DevEval and our `lend` task; one or two
functional tests give no per-requirement signal. It could serve later as a small control for "stated
interface, tiny spec", not for the compiler's question.

# Implementation notes

Package `lend` (`pip install -e .` gives the `lend` command; no runtime dependencies). Code in `lend/cli.py`, data in `.lend/data.json`. Commands: `init`, `member add`, `item add`, `checkout`, `renew`, `return`, `status --json`, `report --out`. Exit codes 0–4 as specified. Tests: `python -m pytest tests` (pytest is in the `test` extra); they map to the rules by behaviour, and code is marked `# spec: N-…`.

All checklist ids are implemented in code, except:

- N-000081 (print the report on the first Saturday): a human routine, not tool behaviour.
- N-000084 (report row carries email): not implemented; contradicts N-000109 (see OPEN_QUESTIONS 3).
- N-000085/N-000086 (fees over $5 stop lending): not implemented; contradicts N-000057 (OPEN_QUESTIONS 4).
- N-000020/N-000021: satisfied by absence (no fee-payment command).
- Out-of-scope items (N-000123) are simply absent.
- No dedicated performance test for N-000121 (single JSON file read; fast).
- Only a subset of ids have one test each; others are covered indirectly or by code inspection.

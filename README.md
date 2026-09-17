# SDD Compiler

> **Status:** rel01 in progress (opened 2026-09-14, target 2026-09-30). Placeholder README.

A compiler for specifications: it turns a set of Markdown spec files into a checked graph of atomic
specs, and reports where those specs contradict, duplicate or under-specify each other.

**rel01 (in progress):** `sddc compile <spec folder>` → a spec graph in `.sdd/`, plus a report of
every conflict found. See [`sdd/specs/vision.md`](sdd/specs/vision.md).

*TODO — install, quick start and usage, once rel01 ships.*

## Repository map

| Path | What |
|---|---|
| `CLAUDE.md` | Working agreement for AI agents |
| `sdd/` | Specs, release design, decisions — [map](sdd/README.md) |
| `docs/lectures/` | HTML lectures explaining the design reasoning |
| `src/` · `tests/` | Python CLI code and tests *(empty until F1 is specified)* |
| `sdd/archive/chat_history/` | Pre-rel01 brainstorm exports |

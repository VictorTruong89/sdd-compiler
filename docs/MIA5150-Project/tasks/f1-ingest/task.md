You are building a new Python codebase from scratch in the current directory, which is empty except
for `spec/`.

{SPEC_LINE}

Implement feature **F1 (Ingest)**: the `sddc` command-line tool's `init`, `ingest` and `status`
commands, exactly as the specification describes them. Other features (atomizer, graph store,
retrieval, conflicts, compile, export) are out of scope: do not build them.

Rules:
- Read only the specification in `spec/`. It is the only source of requirements.
- Deliver an installable Python package with a `pyproject.toml`, so that `pip install -e .` provides
  the `sddc` command. Python 3.12. You may use PyPI libraries; declare every dependency.
- Write your own tests and run them.
- Where the specification leaves something open, choose, and list each choice in
  `OPEN_QUESTIONS.md` with the requirement it concerns.
- Finish with `IMPLEMENTATION_NOTES.md`: what you built, and every requirement you did not implement,
  with the reason.

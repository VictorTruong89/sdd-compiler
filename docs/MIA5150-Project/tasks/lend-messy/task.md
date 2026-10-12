You are building a new Python codebase from scratch in the current directory, which is empty except
for `spec/`.

{SPEC_LINE}

Implement the `lend` command-line tool exactly as the specification describes it.

Rules:
- Read only the specification in `spec/`. It is the only source of requirements.
- Deliver an installable Python package with a `pyproject.toml`, so that `pip install -e .` provides
  the `lend` command. Python 3.12. You may use PyPI libraries; declare every dependency.
- Write your own tests and run them.
- Where the specification is unclear or contradicts itself, choose, and list each case in
  `OPEN_QUESTIONS.md`: what the specification says, where, and what you chose.
- Finish with `IMPLEMENTATION_NOTES.md`: what you built, and every requirement you did not implement,
  with the reason.

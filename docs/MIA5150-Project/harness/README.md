# Study harness — run a coding agent on a task, then score it

> Built 2026-09-30 for the Phase D pilot (`sdd/design/rel01_design/HANDOVER_code_ready_graph.md`) and
> the week-6 pilot of the proposal. Step 2 of G3-3 §1: it lives outside the compiler (F7 D9). No file
> here is read by `sddc`.

## Layout

| Path | What |
|---|---|
| `harness/run_task.py` | One trial: copy the task's inputs for one spec format into an empty workspace, run Claude Code headless **in a sandbox**, with a $ ceiling and a wall-clock timeout; keep the transcript and a `run.json` |
| `harness/score.py` | Install the agent's package and run the hidden tests **in the same sandbox**; map results to the requirement list; count the spec ids the agent accounted for |
| `harness/sandbox.py` | The bubblewrap command: system read-only, `/home` and `/tmp` hidden, a fresh home, the workspace at `/work`, environment cleared (no `ANTHROPIC_API_KEY`) |
| `tasks/f1-ingest/` | The first task: `task.md` (the fixed task text), `inputs.json` (what each format gets), `requirements.md` (R1–R28), `hidden_tests/` (26 black-box tests) |

## The F1 pilot (approved by the owner 2026-09-30: task F1, model Sonnet)

```bash
cd docs/MIA5150-Project/harness
python3 run_task.py --task ../tasks/f1-ingest --format markdown --model sonnet --budget-usd 10 --dry-run
python3 run_task.py --task ../tasks/f1-ingest --format markdown --model sonnet --budget-usd 10
python3 run_task.py --task ../tasks/f1-ingest --format export   --model sonnet --budget-usd 10
python3 score.py --run ~/sddc-runs/study-runs/<run> --task ../tasks/f1-ingest
```

- **Inputs, same content in both formats.** Markdown: the 9 frozen spec files the pilot graph was
  compiled from (`~/sddc-runs/pilot-graph-R000023-specs/specs`). Export: the frozen export of that graph,
  gate passed with the owner's 21 verdicts (`~/sddc-runs/pilot-export-R000023`, manifest
  `pilot-export-R000023.sha256`).
- **Ceiling: $10 estimated API-equivalent per run.** The owner asked for about twice the earlier Haiku
  ceiling. There was no Haiku *agent* ceiling; the nearest figures are the Haiku compile rounds capped
  at 200 and 300 calls, ≈ $3.88 and ≈ $4.89 (build-plan I-94). Twice the larger ≈ $9.78 → **$10**,
  enforced by `claude --max-budget-usd`. *What one Sonnet run actually takes is to be measured.*
- **The pilot task is excluded from reported results** (G3-3 §6). If the export loses, the export is
  fixed first.

## ⚠ Before the first run: the sandbox needs one system change (owner)

Ubuntu 24.04 restricts unprivileged user namespaces through AppArmor
(`kernel.apparmor_restrict_unprivileged_userns = 1`), so `bwrap` fails with
`setting up uid map: Permission denied`. Both scripts refuse to run without the sandbox. They do not fall
back: an agent with `bypassPermissions` outside a sandbox could read this repository, including the
hidden tests and the current specs.

The usual fix is an AppArmor profile that lets `bwrap` alone create namespaces:

```bash
sudo tee /etc/apparmor.d/bwrap >/dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF
sudo apparmor_parser -r /etc/apparmor.d/bwrap
```

Then `run_task.py --dry-run` must report every probe `ok`: home hidden, `~/sddc-runs` hidden, spec
visible, `claude --version` runs, no API key.

## What is recorded

- `run.json`: task, format, requested and reported model, Claude Code version, ceiling, exit code, turns,
  wall time, `est_api_equivalent_usd` (Claude Code's `total_cost_usd`), usage, and a **contamination
  audit** (any tool call naming a path outside the task).
- `score/score.json`: hidden tests passed / total, requirements passed by test, requirements left for the
  human audit (R20, R28), F1 `AC-`/`CT-` labels the agent mentions, `# spec:` marks, F1 checklist ids
  mentioned (export only), and whether `pyproject.toml`, `OPEN_QUESTIONS.md`, `IMPLEMENTATION_NOTES.md`
  exist. `pip freeze` of the scoring environment is kept (`freeze.txt`): packages come from PyPI at
  scoring time.

## Checked without a model (2026-09-30)

- The hidden tests pass on this repository's own implementation (26 / 26) and fail on a command that
  does nothing (26 / 26 failed): they discriminate.
- The probe and the scorer both stop with exit 4 when the sandbox cannot start (as now). End-to-end
  scoring inside the sandbox is **not yet verified**: it needs the AppArmor change.

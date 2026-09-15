# `.claude/hooks/` — PLACEHOLDER

No hooks are active. `.claude/settings.json` has an empty `hooks` object.

Candidates for rel01 (undecided):

- **Spec-read gate:** a `PreToolUse` hook on `Edit|Write` that denies edits to governed paths until
  the governing spec has been read in the session (pattern from `collective-investment-ai-assistant`).
- **Compile trigger:** a hook that runs the SDD Compiler after a spec file under `sdd/specs/` is
  edited, so the tool dogfoods itself.
- **Study logging:** a `PostToolUse` hook on `Read|Grep|Glob` that logs which spec units were read,
  for the effectiveness comparison.

A hook script is added here only together with its `settings.json` entry. A configured hook whose
script is missing fails every tool call.

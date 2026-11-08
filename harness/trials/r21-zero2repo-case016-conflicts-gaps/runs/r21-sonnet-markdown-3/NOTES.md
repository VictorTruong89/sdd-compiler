# NOTES

Layout: `scripts/detect.py` (detector), `hooks/prosecheck-*.js` (+ `hooks/prosecheck-lib.js` shared helpers, `hooks/hooks.json`),
`commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents whose body is `/prosecheck $ARGUMENTS`),
`.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `.claude-plugin/plugin.json`. No build step.

## Disagreements inside the specification (what each side says, what I built)

1. **Ledger retention.** PRD (Non-functional constraints, FP-06 `show`): a ledger last modified more than seven days ago is gone, seven days or younger is kept.
   Interface Contract (Config filenames): "A ledger untouched for more than one day is deleted at the next session start." Built: **seven days** (pruned at session start and on read).
2. **Ledger record count.** PRD FP-05: "At most the newest 20 records are kept." Contract (Plugin config and ledger): "Each ledger keeps its newest 50 records." Built: **20**.
3. **apply_patch path limit.** PRD FP-05: "at most 16 distinct paths". Contract (Post-tool-use reply): "At most ten paths of one payload are scored." Built: **16**.
4. **Stats prose-score threshold.** PRD FP-06: printed when the trimmed slice is longer than 200 characters. Contract (`stats` Reply): longer than 500 characters. Built: **200**.
5. **Stats: named transcript vs newer one.** PRD FP-06: "a named transcript wins over a newer one". Contract (`stats` Transcript rows): when `projects` holds a transcript newer than the named one, the newer is read. Built: **named transcript wins** (PRD).
6. **Catalogue 17 weight.** PRD FP-01: the parallelism form is weight zero, the tailing-negation form is score-moving (and 17 is among the 50 score-moving numbers). Contract (Findings): both forms carry weight zero. Built: **PRD** (tailing negation moves the score, parallelism does not).
7. **Single decisive family floor.** PRD FP-01 says both "A decisive finding always lifts the score to at least 45, whatever the confidence" and "A single decisive family at `none` or `low` confidence does not take that 45 floor". Built: the specific rule: single decisive family gets the 45 floor only at `moderate`/`high` confidence; two decisive families get 65 always.
8. **Stop phrases.** PRD FP-04: "A prompt that contains `stop prosecheck` anywhere switches the tool off." PRD FP-06 and Contract: only the entire prompt (`stop prosecheck` / `prosecheck off`) does; extra words make an ordinary prompt. Built: **entire prompt only**.
9. **`PROSECHECK_DEFAULT_MODE` precedence.** PRD FP-04: used only when nothing valid is stored. Contract (Host environment): "when it is set, it takes precedence over the stored level." Built: **stored level wins**, env is the fallback before `full`.
10. **Several file operands.** PRD FP-01 and Contract (Several file operands): the first file is scanned. Contract Signature: "the last one is the file scanned." Built: **first operand**, with a stderr notice naming it.
11. **Trailing double space.** PRD FP-03 normal behaviour: two trailing spaces ending a prose line are a markdown hard break and are kept; FP-03 boundary: they are removed, "required, not optional". Built: **removed**.
12. **No-break spaces.** PRD terminology: "Every no-break space becomes an ordinary space"; FP-03: NBSP/NNBSP are kept in listed positions (digit neighbour, before `:;!?»›%€`, after `«‹`). Built: the **positional exceptions**.
13. **Transition clusters (37).** FP-01 rule 37 needs two or more openers in one paragraph; a sentence under rule 36 says one sentence opening with a transition "already fires". Built: **two or more per paragraph**.
14. **utm_source (64 vs 65).** The 64 bullet says any `utm_source` left in a link is an AI tracking parameter; the 65 bullet says only the listed hosts. Built: **65's exact host list**.
15. **Label caps.** PRD gives guard 5, check 8, show 5; Contract defers to the PRD. Built: 5 / 8 / 5.

## Unstated details and my assumptions

- Score weights, per-family point formula, resample count/seed (20/8/4 resamples by length, seed 1729), hyphen-compound list, marketing-slop list, stock adjective list: not stated; chosen freely (see `detect.py`). Weights are per family (8–20 points, hit count adds up to 2x); caps and floors follow the PRD.
- Model-dialect family (2) fires only with two or more hits (PRD: "needs two hits").
- Homoglyph count metric counts lookalike characters; findings 66 count the same.
- Character-layer findings (62, 66, 67, 68) are computed on the raw scan window, including inside code fences (code masking applies to the lexical families).
- Zip extraction: paragraphs/slides/cells joined with a single `\n`; notebook markdown cells joined with a blank line; epub order follows the OPF spine; member size cutoff 64 MB.
- A NotebookEdit payload with only `file_path` is scored; an apply_patch line without a colon names no path; `apply_patch` bodies are read from `tool_input.command` (also `patch`/`input`).
- `check` on a nonexistent `.pdf` reports `cannot read` (existence is checked before extension).
- The stats hook de-duplicates assistant rows by `message.id` (rows without an id each count once) and takes the max usage per id.
- Ledger file for a missing `session_id` is `.prosecheck-ledger`; ids are percent-escaped for the file name.
- `init` section is recognised by its start marker or heading text; the live (session) contract names this machine's detector path, the exported one does not.

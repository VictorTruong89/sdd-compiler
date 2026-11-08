# NOTES

prosecheck 0.9.3: `scripts/detect.py` (Python stdlib, helpers in `scripts/*.py`) and Node hooks in `hooks/`
(`prosecheck-lib.js` is shared). Menu documents: `commands/prosecheck.md`, `install/prosecheck-command.md`.
Cursor rule: `.cursor/rules/prosecheck.mdc`. No build step.

## Disagreements in the specification, and what I built

1. **Ledger retention.** Interface Contract ("Config filenames"): "A ledger untouched for more than one day is deleted
   at the next session start." PRD (non-functional constraints, FP-06 `show`): older than seven days is gone, seven days
   or younger is kept. Built: 7 days. Age is counted in whole days, so a ledger exactly 7 days old is kept. Session
   start deletes ledgers older than that, and `show` ignores them.
2. **Ledger size.** PRD FP-05: "At most the newest 20 records are kept." Contract: "Each ledger keeps its newest 50
   records." Built: 50 kept, and `show` lists all of them.
3. **apply_patch path limit.** PRD FP-05: "at most 16 distinct paths". Contract (post-tool-use reply): "At most ten paths
   of one payload are scored." Built: 10 (the lower limit satisfies both "at most" statements).
4. **Tailing negation (17).** PRD FP-01: the tailing-negation form is score-moving. Contract (Findings): "Both forms of
   catalogue 17 are writing advice and carry weight zero." Built: parallelism form weight 0, tailing negation
   score-moving (PRD). Keys are `17_negative_parallelism` and `17_tailing_negation`.
5. **Single decisive finding.** PRD FP-01 says both "A decisive finding always lifts the score to at least 45, whatever the
   confidence" and "A single decisive family ... only when confidence is above `low`". Built: the specific rule. One
   decisive family gets the floor of 45 only at moderate/high confidence; two distinct decisive families get at least 65.
6. **`PROSECHECK_DEFAULT_MODE`.** Contract: "when it is set, it takes precedence over the stored level." PRD FP-04: it is used
   only when nothing valid is stored. Built: the PRD rule (stored valid level, else the environment word, else `full`),
   so `/prosecheck lite` etc. keep working when the variable is set.
7. **Stop phrase.** PRD FP-04: "A prompt that contains `stop prosecheck` anywhere switches the tool off." PRD FP-06 and the
   Contract: only the entire prompt (`stop prosecheck` / `prosecheck off`, any case) does. Built: entire prompt only.
8. **Stats transcript choice.** PRD FP-06: "a named transcript wins over a newer one". Contract (Transcript rows): a newer
   transcript under `projects` is read instead. Built: the named `transcript_path` wins; the newest `.jsonl` under
   `<config>/projects` is used only when none is named. Assistant rows sharing one message `id` count as one turn
   (largest usage values per id; their text is joined).
9. **Stats prose score threshold.** PRD: printed when the trimmed slice is longer than 200 characters. Contract: longer
   than 500. Built: 500.
10. **Several file operands.** Contract signature: "the last one is the file scanned"; the same document later and the PRD
    say the first is scanned. Built: the first is scanned and a notice line on stderr names it.
11. **Transition clusters (37).** PRD FP-01 says two or more opening transitions in one paragraph fire it, and the
    challenges bullet says one transition-opened sentence "already fires" it. Built: two or more in one paragraph.
12. **Size units.** `over 512 KB` / `over 4096 KB` are printed for the plain-text and archive caps (4 MB = 4096 KB).

## Not stated in the specification; my assumptions

- **Score formula.** Not given. Each score-moving family adds `weight * (1 + 0.25 * min(hits-1, 4))`, the sum is multiplied
  by 1.3 and capped at 100, then the PRD caps and floors are applied (one family: at most 40; only rhythm kinds: at most
  40; only sentence monotony: at most 20; decisive, short-document and long-document floors). Weights are in `META` in
  `scripts/detect.py`.
- Hyphenated stock-pair list (4), marketing-slop list (69), named outlet lists, resample count (20, seed fixed,
  5th to 95th percentile, widened to include the point score) are my choice, as the PRD allows.
- Boldface (56) fires on any `**bold**` span; contraction absence (55) needs first-person words at 2% of the text and at
  least three written-out forms with more than half of all contractible forms written out; semicolon/parenthesis underuse
  (46) means no semicolon and at most one `(`; homoglyph hit count = number of lookalike characters.
- Plain text and archives joined with `\n` between paragraphs, slides, cells and chapters (no blank line is added).
- A `NotebookEdit` payload carrying only `file_path` is scored. A patch line without a colon names no path.
- `/prosecheck check` on an extension outside the twenty is scored as plain text with the 512 KB cap.
- A failed ledger row reads: "Python not found", "detector timed out", "detector produced no result",
  "detector printed text that is not a structured report", "report had no numeric score", "file could not be read".
- The live contract names this machine's detector path at `full`/`strict`; the exported one never does.
- Markers `<!-- prosecheck:begin -->`/`end` wrap the `AGENTS.md` section; a heading `# Writing contract (` also counts as present.
- Ledger files: `.prosecheck-ledger-<session_id>` (characters outside `A-Za-z0-9._-` become `_`), or `.prosecheck-ledger` with no session.

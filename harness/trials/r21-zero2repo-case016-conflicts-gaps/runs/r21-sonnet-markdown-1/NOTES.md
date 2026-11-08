# NOTES

Layout: `scripts/detect.py` (+ helpers `extract.py`, `chars.py`, `families.py` next to it), `hooks/*.js`, `commands/prosecheck.md`
and `install/prosecheck-command.md` (menu documents, body `/prosecheck $ARGUMENTS`), `.cursor/rules/prosecheck.mdc`,
`hooks/hooks.json`, `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`. No build step.

## Disagreements in the specification (and what I built)

| Topic | One side | Other side | Built |
| --- | --- | --- | --- |
| Which file is scanned with several operands | Interface "Signature": "When several operands are given, the last one is the file scanned" | PRD FP-01 and Interface "Several file operands": "the first file is scanned" | First file scanned; stderr notice names it. |
| Ledger age limit | PRD (non-functional, FP-06): older than seven days is gone, seven days or younger is kept | Interface "Config filenames": untouched for more than one day is deleted at next session start | Seven days. Session start deletes older ledgers; `show` also treats an older ledger as empty. |
| Ledger length | PRD FP-05: newest 20 records | Interface "Plugin config and ledger": newest 50 | 20. |
| apply_patch path cap | PRD FP-05: at most 16 distinct paths | Interface "Post-tool-use reply": at most ten | 10 (the smaller cap satisfies both "at most" readings). |
| Catalogue 17 weight | PRD FP-01: parallelism form is writing advice, tailing-negation form is score-moving (50 score-moving + 12 advice = 62) | Interface "Findings": both forms are weight zero | PRD: tailing negation moves the score, parallelism form is weight zero. |
| Level precedence | PRD FP-04: stored valid word wins; the environment word is used only when nothing valid is stored | Interface "Host environment": `PROSECHECK_DEFAULT_MODE` takes precedence over the stored level | PRD (stored valid level first, then env, then `full`). |
| Stop phrase | PRD FP-04: a prompt that contains `stop prosecheck` anywhere switches off | PRD FP-06 and Interface: only the entire prompt (`stop prosecheck` / `prosecheck off`) does; extra tokens make it an ordinary prompt | Entire prompt only (case-insensitive, surrounding whitespace trimmed). |
| `stats` transcript choice | PRD FP-06: a named transcript wins over a newer one | Interface "Transcript rows": a newer transcript in `projects` is read instead of the named one | Named `transcript_path` wins. |
| `stats` prose score threshold | PRD FP-06: slice longer than 200 characters | Interface "Reply": longer than 500 characters | 500. |
| Trailing two spaces in cleanup | PRD FP-03 "What is trimmed": two trailing spaces (hard break) are kept | PRD FP-03 "Boundary": removed, "required, not optional" | Removed. |
| Transition words | PRD 36 note: a single sentence opening with a transition word "already fires" 37 | PRD 37: two or more sentence-opening transitions in one paragraph | Two or more in one paragraph. |

## Things the specification does not state (assumptions)

- Score formula: not given. Each score-moving family adds a base value (about 10, decisive 18-20, rhythm/format families 6-8) plus a small increment per extra hit with a per-family cap; the sum is then limited by the stated rules (single family <= 40, rhythm-only <= 40, monotony-only <= 20) and lifted by the stated floors (45/65 decisive, short-document and long-document family-count floors).
- `homoglyphs` metric counts lookalike characters; the finding's `count` is the same number.
- Family 2 (model-dialect) needs two hits in total to fire (PRD FP-04: "needs two hits").
- Lists for families 4 and 69 are my own; hedge, bold, emoji, etc. thresholds not stated (46: under 300 words never fires, no semicolon and at most one "("; 55: first-person words at least 2% of words and written-out forms outnumbering contracted ones 1.5:1; 41: six or more sentences with strictly alternating direction, each step at least 4 words and 1.6x; 71: at least 20% of six-word shingles repeated, minimum 12 shingles; 70: three or more rules in a document of at least 24 lines).
- Character-layer findings (62, 66, 67, 68) are computed on the whole scan window; markdown masking (code, tables, quotes) applies to the pattern families only.
- Extracted archive/notebook paragraphs are joined with single newlines (empty paragraphs dropped), text is stripped at both ends.
- `--ci`: 30 sentence-resamples (8 for windows over 40,000 chars) with a fixed seed; the interval is widened to contain the point score.
- Detector errors on `.pdf`/`.rtf`: both are `empty input` (exit 1).
- Guard failure reasons: "python not found", "detector output was not a structured report", "report had no numeric score", "detector timed out", "detector gave no usable result" (no output / failed exit), "file could not be read" (path missing).
- A NotebookEdit payload that has only `file_path` is scored; an apply_patch line without a colon does not name a path.
- Ledger files are named `.prosecheck-ledger-<session_id>` (unsafe characters become `_`); no session id uses `.prosecheck-ledger`.
- Stats counts each assistant message id once (later rows with the same id take the larger token figure).
- `init` resolves the shipped Cursor rule under the plugin root and falls back to an embedded copy of the same text when the file is missing.

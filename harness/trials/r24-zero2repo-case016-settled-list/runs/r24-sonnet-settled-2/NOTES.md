# NOTES

Layout: `scripts/detect.py` (detector), `hooks/*.js` (session-start, prompt-submit/router, subagent-start, post-tool-use, stats; shared code in `hooks/lib.js`), `commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents forwarding `$ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`.

## Spec conflicts and what was built

The 17 conflicts in `spec/RULINGS.md` were built as ruled:
1. Help usage goes to stdout (exit 0); usage errors go to stderr.
2. A decisive finding always lifts the score to at least 45 (PRD line 93), whatever the confidence.
3. Hedge stacking (54) is weight zero (PRD line 90), not score-moving.
4. Both forms of catalogue 17 (`17_negative_parallelism`, `17_tailing_negation`) are weight-zero advice (IC line 148).
5. A no-break space (U+00A0/U+202F) that holds something together (digit beside, before `: ; ! ? » › % €`, after `« ‹`) is kept by `--clean`; the others become U+0020.
6. Two trailing spaces ending a prose line are kept by `--clean` (markdown hard break); other trailing whitespace is removed. I keep them only when exactly two spaces trail and a non-blank line follows.
7. Catalogue 65 fires only when the `utm_source` host is one of the listed AI domains.
8. `stop prosecheck` anywhere in a prompt switches the tool off (stores `off`); when it is the entire prompt (or `prosecheck off` is), a block reply is also sent. When it is only part of a prompt the stored level becomes `off` and the hook prints nothing.
9. `PROSECHECK_DEFAULT_MODE` applies only when no valid level is stored.
10. `.pdf`/`.rtf` are not prose files (detector: empty input; guard: ledger "binary"); the `show` empty-ledger wording still mentions `.docx` and `.pdf`.
11/12. Two or more operands succeed; the LAST operand is scanned (IC line 106). The stderr notice lists all operands, so it contains the first operand exactly as given.
13. `apply_patch` scores at most 16 distinct paths.
14. Ledger keeps the newest 50 records.
15. Ledger kept until more than 7 days old (checked at session start, and also when a ledger is read or written).
16. `stats`: when `projects` holds a transcript newer than the named one, the newer one is read. If the named path does not exist, it is reported as unreadable.
17. Session-prose score printed when the trimmed slice is longer than 200 characters.

Further disagreements I found that the rulings file does not list:
- PRD FP-01 line 116 (end of the family-36 bullet) says "A single sentence that opens with one of the transition words of 37 already fires transition clusters", while family 37 (line 117) says "two or more sentence-opening transitions ... in one paragraph". I built the explicit family-37 rule (two or more in one paragraph).
- PRD line 155 (family 61) calls "from 9 to 5" a false range (15), while family 15 (line 110) says only the rhetorical sweep ("from the dawn ... to the modern") fires. I built family 15's rule; numeric spans do not fire 15.
- IC line 21 says "at most one file operand" (already ruled, see 11).
- PRD FP-05 "up to five labels" vs IC check cap: guard lists at most 5 labels, `check` at most 8, `show` at most 5, as each section states.

## Things the spec does not state (my assumptions)

- **Score formula.** Not given. Each score-moving family adds points (10; 12 for AI vocabulary; 20 for decisive families; 6 for rhythm kinds), scaled up to 3x by hit count, summed and capped at 100. Then the stated caps (one family: at most 40; rhythm-only: at most 40; monotony-only: at most 20) and floors (short/long document floors, 45 for one decisive family, 65 for two) apply.
- **Hit thresholds** the PRD leaves open: model-dialect vocabulary (2) needs two hits (as FP-04 says); every other family fires on a single hit unless its rule says otherwise. Bold (56) and inline-header lists (33) fire on one occurrence.
- **Lexical lists** the PRD leaves to the implementer (hyphenated clichés 4, marketing slop 69, stock adjectives for 6) are my own short lists.
- **Heuristics:** "ends in a noun" for catalogue 6 is approximated (last word of the chain is not adjectival); 46 fires at 300+ words with no semicolon and at most one "("; 55 needs first-person pronouns at 3%+ of words and more written-out than contracted forms; 41 needs six sentences alternating strictly with jumps of at least 5 words.
- **Masking** (code fences, inline code, quote runs, tables, badges, front matter) keeps character offsets; character-layer findings (62, 66, 67, 68) are computed on the raw window including such regions.
- **Archive extraction** joins paragraphs, slides, cells and chapters with a single line feed, then strips both ends. Notebook markdown cells are joined with a line feed. Sheets and slides are read in numeric file order; epub chapters in OPF spine order when readable. No archive-member size cutoff.
- **`--ci`** uses 20 resamples (fewer on big inputs) with a fixed seed, 5th–95th percentile, widened to include the point score.
- **Unknown option** parsing is sequential: help/`-h` seen before an unknown option wins. A lone `-` is an unknown option.
- **Ledger** file name is `.prosecheck-ledger-<session id, sanitized>` (`.prosecheck-ledger` with no session id). Records hold base name only. Timeouts, missing Python, unusable output, no score, and no result each have their own readable reason (no numbers in them).
- **Guard**: `apply_patch` lines without a colon do not name a path; a `NotebookEdit` carrying only `file_path` is scored. Unknown tool names are ignored.
- **`check` path argument**: unquoted paths take the rest of the line (so spaces work); the stats transcript, `show`, and `init` use the process's working directory / host JSON as the IC states.
- **Stats**: assistant rows sharing a message `id` count as one turn (the last row's usage is used, text is joined); rows without an id each count as a turn.
- **First start**: the level flag is written on first session start whenever the effective level is not `off`; with `off` from the environment nothing is stored.
- **Contract wording** is mine; it never uses the phrase "source code".

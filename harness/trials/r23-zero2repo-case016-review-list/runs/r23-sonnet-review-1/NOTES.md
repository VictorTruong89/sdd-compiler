# NOTES

Layout: `scripts/detect.py` (detector), `hooks/prosecheck-*.js` (+ `prosecheck-common.js`), `install/prosecheck-command.md` and `commands/prosecheck.md` (menu document, body `/prosecheck $ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`. No build step.

## Disagreements in the specification, and what was built

1. **Where usage goes.** PRD FP-01 Public entry: usage "goes to the error stream"; PRD FP-01 Boundary and IC `--help`: usage "to standard output", exit 0. Built: stdout, exit 0.
2. **Single decisive floor.** PRD FP-01: "A decisive finding always lifts the score to at least 45, whatever the confidence" vs "A single decisive family at `none` or `low` confidence does not take that 45 floor." Built: the 45 floor applies only when confidence is above `low`; two decisive families give at least 65 at any confidence.
3. **Hedge stacking (54).** Listed as weight-zero writing advice (line 90) vs "Each sentence with stacked hedges adds to the score" (family rules). Built: weight zero; reported, never moves the score.
4. **Tailing negation (17).** PRD: tailing-negation form is score-moving; IC: both forms of 17 are weight zero. Built: PRD (`17_tailing_negation` moves the score, `17_negative_parallelism` is weight zero).
5. **No-break spaces.** Terminology "Every no-break space becomes an ordinary space" vs FP-03 list of kept NBSP/NNBSP (digit neighbour, before `: ; ! ? » › % €`, after `« ‹`). Built: the FP-03 exceptions are kept; all other NBSP become U+0020. Kept ones are not counted.
6. **Hard-break trailing spaces.** FP-03 "What is trimmed" keeps two trailing spaces vs FP-03 Boundary "removed even when two spaces were meant as a hard break... required". Built: removed.
7. **Zero-width characters.** FP-01 "A zero-width character inside the text is an invisible character" vs FP-03 positional exceptions and "a character the scrub keeps is not counted". Built: exceptions apply; kept characters are not counted. The same function drives counting and cleanup.
8. **`utm_source`.** FP-01 line "Any `utm_source` parameter ... (65)" vs 65's rule "fires only when that whole host name is one of those domains". Built: only the seven listed hosts fire 65.
9. **`stop prosecheck`.** FP-04 "contains `stop prosecheck` anywhere" vs FP-06/IC entire prompt only. Built: whole prompt only (case-insensitive, trimmed); extra words make it an ordinary prompt.
10. **`PROSECHECK_DEFAULT_MODE`.** PRD FP-04: only when nothing valid is stored; IC Host environment: takes precedence over the stored level. Built: IC (valid env word wins, then stored word, then `full`). `status`, hooks and guard all use this effective level.
11. **`.pdf`.** FP-06/IC empty-ledger text mentions `.pdf` deliverables, FP-02 says pdf is not prose. Built: pdf/rtf are never scored, the guard records them as binary ("not re-scored"); the empty-ledger text keeps the wording.
12. **Number of operands.** IC "at most one file operand" vs "two or more still succeed". Built: extra operands accepted.
13. **Which operand.** IC Signature "last one is scanned" vs IC/PRD "first". Built: first, with a stderr notice `note: only the first file was scanned: <first>`.
14. **apply_patch path cap.** PRD 16 vs IC ten. Built: 16.
15. **Ledger size.** PRD 20 vs IC 50. Built: newest 20.
16. **Ledger age.** PRD 7 days vs IC one day. Built: 7 days (deleted at session start and ignored/deleted by `show`).
17. **stats transcript.** PRD/IC `transcript_path`: named wins; IC Transcript rows: newer one read. Built: a named transcript always wins; newest under `projects` only when none is named.
18. **Session-prose threshold.** PRD 200 characters vs IC 500. Built: 200 (trimmed slice longer than 200).
19. **Model-dialect "needs two hits".** FP-04 says two hits, FP-01 family 2 states no such condition. Built: one hit fires family 2 (so every banned word is enforced).
20. **Welcome vs "never name prosecheck".** Built: welcome names prosecheck (it is shown once to the user); the contract itself never names it.

Also: FP-01 family 36 contains the stray sentence "A single sentence that opens with one of the transition words of 37 already fires transition clusters", which contradicts family 37 (two or more in one paragraph). Built: family 37 as stated (two or more transitions in one paragraph).

## Not stated in the specification (assumptions)

- **Scoring formula.** Per fired score-moving family: `weight * (1 + 0.25*min(count-1,4))`, weights 5-22 (decisive 20-22, lexical 8-12, structural 6), summed and capped at 100, then the caps/floors in the PRD in this order: one family caps at 40; rhythm-only caps at 40; sentence-monotony only caps at 20; decisive floors (45 / 65); short-document and long-document family-count floors.
- **Which lists are the implementer's choice** (4 hyphenated pairs, 69 slop phrases, 11 outlets) use my own lists. 6, 15, 25, 33-35, 41, 46, 55, 70, 71 thresholds not stated exactly: 41 = six sentences alternating with each step at least 5 words and a 1.5 ratio; 46 = at least 300 words, no `;`, at most one `(`; 55 = first-person words at least 2% (and at least 3), written-out forms at least 3 and more than contracted; 71 = at least 20% of six-word shingles repeated; 70 needs at least 24 lines; 56 fires at one bold span.
- **Homoglyph count** is the number of lookalike letters (used for finding count and `homoglyphs` metric). Arabic-presentation lookalikes are a small hand-picked set.
- **Masking** replaces excluded regions (code fences, inline code, 2+ blockquote lines, table rows, badge lines, front matter) with spaces at the same offsets, so character-layer counts, samples and cleanup positions stay aligned. Cleanup itself scrubs the whole input (not masked, not windowed).
- **Extraction separators**: paragraphs, slides, cells, chapters, spreadsheet cells joined with a single `\n`. Member size cutoff 32 MB. xlsx sheets are read in file-number order; epub in OPF spine order (fallback: file name order).
- **`--ci`** uses 40/12/5 seeded resamples (by text size) of sentences, with low/high at the 5th/95th percentile, widened to include the point score.
- **Cleanup line ending**: restores `\r\n` if the input ended with `\r\n`, else `\n`. Only blank leading lines are trimmed, not indentation of the first line.
- **`check`** on non-prose extensions is passed to the detector (plain text cap). Labels in `tells:` are sorted by hit count. Reply to unreadable/absent path is `cannot read <path>`.
- **NotebookEdit** payloads with only `file_path` are scored. apply_patch lines without a colon do not name a path. Patch paths are read from `command` (also `patch`/`input`) only when the tool name contains "patch" or is missing.
- **Guard failure reasons** (no digits in them): `Python not found`, `detector printed text that is not a structured report`, `report has no numeric score`, `detector timed out`, `detector produced no output or exited without a usable result`; unreadable file: `file not readable`.
- **Stats** counts distinct assistant message ids (rows without an id each count once; per id the largest usage is used); transcript search under `projects` is recursive.
- A session id with no `session_id` uses the ledger file `.prosecheck-ledger`; otherwise `.prosecheck-ledger-<sanitised id>`.
- Session start writes the effective level into `.prosecheck-active` when no valid flag exists; the welcome appears only when the flag file did not exist.

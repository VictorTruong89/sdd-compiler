# NOTES

Implementation notes for prosecheck 0.9.3. Section 1 lists every place where the specification disagrees with itself and what was built. Section 2 lists what the specification leaves unstated and what was assumed. Section 3 gives the file layout.

## 1. Specification conflicts

Items 1–17 are the rulings in `spec/RULINGS.md`; each is built as ruled. Items 18 onward are conflicts the rulings file does not cover.

1. **Usage message destination.** PRD FP-01 "Public entry" (lines 82–83) says the usage message goes to the error stream; PRD FP-01 "Boundary" (line 167) says help prints it to standard output and succeeds. Ruling: help goes to standard output with exit 0; usage *errors* go to the error stream. Built: `--help`/`-h` write usage to stdout, exit 0.
2. **Floor for one decisive finding.** PRD FP-01 line 93 (floor 45 whatever the confidence) vs line 94 (no floor at `none`/`low`). Ruling: always at least 45. Built in `compute_score`.
3. **Hedge stacking.** PRD line 90 (weight zero) vs line 128 (adds to score). Ruling: weight zero. Built: catalogue 54 is advice.
4. **Tailing-negation form of 17.** PRD line 91 (score-moving) vs IC line 148 (weight zero). Ruling: both forms weight zero. Built: `17_tailing_negation` and `17_negative_parallelism` are both advice.
5. **No-break spaces.** PRD line 30 (every one becomes a space) vs line 212 (kept when they hold something together). Ruling: kept per line 212. Built in `_nbsp_kept`.
6. **Markdown hard break.** PRD line 214 (kept) vs line 223 (removed). Ruling: kept. Built: `scrub()` keeps exactly two trailing spaces on a prose line; catalogue 68 does not fire on those lines either.
7. **`utm_source` values.** Ruling: only exact AI host names fire 65. Built in `f_ai_tracking`.
8. **`stop prosecheck` position.** PRD FP-04 line 240 and ruling: "anywhere in a prompt switches the tool off". PRD FP-06 line 285 and IC `/prosecheck` > Stop phrases line 411: only the entire prompt. Built: any prompt containing `stop prosecheck` (case-insensitive) stores `off`; the prompt then falls through as an ordinary prompt, which emits nothing while off. The entire-prompt `stop prosecheck` / `prosecheck off` still returns the block reply naming `off`.
9. **`PROSECHECK_DEFAULT_MODE`.** IC line 63 (takes precedence) vs PRD line 246 (only when nothing valid is stored). Ruling: stored valid level wins. Built in `effectiveLevel()`.
10. **`.pdf`.** Ruling: not a prose file. Built: `.pdf`/`.rtf` are binary; the ledger records them as "not re-scored"; the detector treats them as empty input.
11. **Several file operands.** IC line 21 ("at most one") vs IC line 180 and PRD line 168 (succeed). Ruling: accepted.
12. **Which operand is scanned.** IC line 106 (last) vs IC line 180 and PRD line 168 (first). Ruling: the **last** operand is scanned. Built in `main()`.
13. **`apply_patch` path limit.** PRD line 264 (16) vs IC line 260 (ten). Ruling: 16. Built: `MAX_PATHS = 16` in `guard.js`.
14. **Ledger record cap.** PRD line 265 (20) vs IC line 91 (50). Ruling: 50. Built: `LEDGER_CAP = 50`.
15. **Ledger retention.** PRD line 57 (seven days) vs IC line 65 (one day). Ruling: seven days. Built: `pruneLedgers()` deletes ledgers older than seven days at session start; `readLedger()` returns nothing for older ledgers.
16. **Transcript choice for `stats`.** PRD line 292 and IC line 646/681 (the named transcript) vs IC line 650 (a newer transcript in the projects folder). Ruling: the newer one wins. Built in `chooseTranscript()`.
17. **Session-prose score threshold.** PRD line 292 (more than 200 characters) vs IC line 662 (more than 500). Ruling: 200. Built: `SCORE_MIN = 200` in `stats.js`.
18. **Interval switch name.** IC line 25 calls `--ci` the resampled interval; PRD FP-01 says "a resampled interval". Not a conflict in substance; built as `--ci`.
19. **Stop phrases in the router versus the stop-phrase list.** Already covered by item 8.
20. **Session start writes the flag.** IC line 239 requires later hooks to see the stored level after a session start; PRD line 246 says the environment applies only when nothing valid is stored. Built: when no valid flag exists, session start stores the effective level (environment or `full`). Consequence: an environment value is frozen into the flag at first session start. This follows IC line 239, and the flag then beats the environment as ruled.
21. **Welcome detection.** PRD line 238 says "when no mode flag exists yet"; built as "the `.prosecheck-active` file does not exist", so an invalid flag file does not re-trigger the welcome.

## 2. Unstated details and assumptions

- **Score formula.** The specification fixes the bands, floors, caps, and confidence, but not the per-family weights or how hits combine. Built: each score-moving family adds `weight × (1 − 0.6^hits)`, weights 6–14 (`FAMS` in `scripts/detect.py`), with decisive families at 14. The caps and floors then apply in the order: single-family cap at 40 (20 for sentence-length monotony alone; 40 for rhythm-only), then decisive floors (45 for one, 65 for two), then the short-document and long-document floors.
- **Family thresholds the specification leaves open.** Model-dialect vocabulary needs two hits (FP-04 says so). Boldface overuse fires at two or more bold spans. Em-dash overuse fires per paragraph at two or more dashes. Decorative rules fire at three or more standalone rules in a document of at least 24 lines. Semicolon/parenthesis underuse fires on documents of at least 300 words with no semicolon and at most one parenthesis. Contraction absence fires when first-person words are at least 2% of words (and at least 3) and at least 80% of contractable forms are written out.
- **Word lists the specification leaves to the implementer.** Hyphenated clichés (4), canonical marketing slop (69), stock adjectives for chains (6), marketing openers (3), and the placeholder bracket names (63). These are representative lists, not complete ones.
- **Sentence and paragraph segmentation.** Sentences end at `.`, `!`, `?` followed by whitespace; heading lines are excluded. Paragraphs are separated by blank lines.
- **Masking.** Front matter, fenced code (CommonMark closing rules), blockquote runs of two or more lines, table rows, badge-only lines, and inline code spans are blanked before pattern matching. Character-layer findings (62, 66, 67, 68) use the unmasked window.
- **Invisible-character keep rules.** Implemented per FP-03 as far as the positions can be checked locally. Emoji tag sequences, ideographic selectors, ZWSP beside CJK/Thai/Lao/Khmer/Myanmar/kana, soft hyphens between letters, bidi marks in right-to-left documents, Mongolian selectors, and Khmer vowels are kept; everything else in the invisible class is removed.
- **Homoglyph lookalikes.** The table in `_LOOK_PAIRS` covers the Cyrillic, Greek, and Armenian letters that look like the listed Latin letters. Arabic-presentation lookalikes are not included. A token qualifies when it mixes ASCII Latin letters with lookalikes and holds no other non-ASCII letter.
- **Trailing whitespace (68).** Counted per line, except an exact two-space hard break on a prose line; leading whitespace before the first character; trailing spaces at end of text; two or more newlines at end of text.
- **Interval (`--ci`).** The four contiguous sentence blocks are each scored, and the low and high of those scores, together with the point score, form the interval. Fewer than four sentences gives `score_ci: null` with a note.
- **Extraction details.** `.xlsx` cells are joined one per line; `.epub` files whose names contain `nav` or `toc` are skipped; notebooks join markdown cells with line breaks. The archive-member cutoff is not enforced.
- **Cleanup output.** Cleanup works on the whole text, not the window, so a rescan of the output reports zero invisible characters. Output carries a final newline only when the input had one.
- **Unknown option.** A lone `-` is treated as an unknown option, following the literal text of IC line 106.
- **Guard.** Paths are resolved against the payload `cwd` when given, else the hook's working directory. `NotebookEdit` uses `notebook_path`, falling back to `file_path`. An `apply_patch` line counts as a path only when it has the colon. Instruction files are matched by lower-cased name. A file that is missing is recorded as a failed read, and no nudge is produced.
- **Ledger.** Stored as a JSON array in `.prosecheck-ledger-<session>` (or `.prosecheck-ledger` when no session id is given). Only base names are stored.
- **`show`.** A flagged row reads "flagged"; an unflagged row with labels reads "under threshold".
- **`check`.** Non-prose extensions (for example `.py`) get "not a prose format prosecheck scores" and no score.
- **Doctor.** The Python probe runs the detector on a fixed sentence through stdin. The settings check creates and removes a temporary file in the config folder.
- **Stats.** Assistant rows are deduplicated by `message.id` for turn and token counts; text blocks from all assistant rows are used for the prose slice. A named transcript that cannot be read yields the missing-transcript reply and does not fall back.
- **Contract export.** The exported contract in `AGENTS.md` contains no install path and no user name; the live session contract contains the detector path. The `CLAUDE_PLUGIN_ROOT` line appears once at full and strict only.
- **Stats hook.** `prosecheck-stats.js` is shipped as a hook entry point, but `hooks/hooks.json` does not register it, because `/prosecheck stats` is answered by the prompt-submit router.
- **Skill fallback path.** The detector lookup falls back to `skills/prosecheck/scripts/detect.py`, but no skill directory is shipped.
- **Python `-I`.** Hooks run the detector with `python -I`, which ignores user site and environment variables, so a planted module in the working directory cannot shadow the stdlib.

## 3. Layout

- `scripts/detect.py`: detector (standard library only).
- `hooks/prosecheck-activate.js`, `prosecheck-tracker.js`, `prosecheck-subagent.js`, `prosecheck-guard.js`, `prosecheck-stats.js`: hook entry points.
- `hooks/hooks.json`: hook registration (session start, prompt submit, subagent start, post-tool-use).
- `hooks/lib/`: shared modules (`core.js`, `contract.js`, `commands.js`, `router.js`, `guard.js`, `stats.js`).
- `commands/prosecheck.md`: menu command; its body forwards `$ARGUMENTS` to the router.
- `.cursor/rules/prosecheck.mdc`: shipped Cursor rule, prose globs only.
- `.claude-plugin/plugin.json`: plugin manifest.
- `spec/`: unchanged.

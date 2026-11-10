# NOTES

Build notes for prosecheck 0.9.3: where the specification disagrees with itself, what it leaves out, and what was built. Section numbers below match `spec/CONFLICTS.md` where a conflict is listed there. The spec files were not edited.

Layout built:

- `scripts/detect.py`: the detector (Python 3.9+, standard library only).
- `hooks/prosecheck-activate.js`, `hooks/prosecheck-tracker.js`, `hooks/prosecheck-subagent.js`, `hooks/prosecheck-guard.js`, `hooks/prosecheck-stats.js`: the plugin hooks; `hooks/hooks.json` registers the four that the host fires.
- `hooks/lib/common.js` and `hooks/lib/commands.js`: shared logic (config, level flag, ledgers, contract text, detector bridge, `/prosecheck` replies).
- `commands/prosecheck.md`: the menu document (`$ARGUMENTS` body).
- `.cursor/rules/prosecheck.mdc`: the shipped prose-only Cursor rule.
- `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`, `README.md`.

## Conflicts and how they were resolved

Rule used throughout: when two statements disagree, the more specific statement wins; when the Interface Contract (IC) defers a behaviour to the PRD, the PRD wins. Each entry names both sides and the choice.

1. **Where the usage message goes (CONFLICTS 1).** PRD FP-01 "Public entry" (lines 82–83) says the usage message goes to the error stream. PRD FP-01 "Boundary" (line 167) and IC `scripts/detect.py` > Usage (line 110) say `--help`/`-h` print it to standard output and exit 0. **Built:** standard output, exit 0.

2. **Floor for one decisive family (CONFLICTS 2).** PRD FP-01 line 93: "A decisive finding always lifts the score to at least 45, whatever the confidence." PRD FP-01 line 94: a single decisive family at `none` or `low` confidence does not take the 45 floor. **Built:** line 94 (the specific rule). A single decisive family reaches 45 only at `moderate` or `high` confidence; two distinct decisive families reach 65.

3. **Hedge stacking (CONFLICTS 3).** PRD line 90 lists 54 among the 12 writing-advice numbers (weight zero). PRD line 128 says "each sentence with stacked hedges adds to the score." **Built:** weight zero (line 90 is the explicit list). The finding is still reported.

4. **Tailing-negation form of 17 (CONFLICTS 4).** PRD line 91 says the tailing-negation form is score-moving. IC `scripts/detect.py` > Findings (line 148) says both forms carry weight zero. **Built:** tailing negation scores (PRD). The parallelism form is weight zero (PRD line 91 and IC). Keys: `17_tailing_negation` (scores) and `17_negative_parallelism` (advice).

5. **No-break spaces (CONFLICTS 5).** PRD Terminology (line 30) says every no-break space becomes an ordinary space. PRD FP-03 (line 212) keeps no-break spaces that hold something together (digit on either side; before `: ; ! ? » › % €`; after `« ‹`). **Built:** the FP-03 rule (more specific). Kept spaces are not counted, and cleanup leaves them alone.

6. **Markdown hard-break spaces (CONFLICTS 6).** PRD FP-03 "What is trimmed" (line 214) keeps two trailing spaces; PRD FP-03 "Boundary" (line 223) says that collapse "is required, not optional." **Built:** removal (line 223, stated as required). Trailing spaces are reported as finding 68 and cleanup removes them.

7. **Zero-width characters (CONFLICTS 7).** PRD FP-01 line 159 says any zero-width character inside the text is invisible; PRD FP-03 (lines 211, 215) keeps them in the listed positions. **Built:** FP-03's positions (more specific). A kept character is not counted, and a rescan of cleaned output reports zero.

8. **`utm_source` (CONFLICTS 8).** PRD line 131 says any `utm_source` is a tracking parameter; PRD line 132 says it fires only for the seven listed host names. **Built:** line 132 (specific). Other values are not findings.

9. **`stop prosecheck` (CONFLICTS 9).** PRD FP-04 line 240 says a prompt that *contains* `stop prosecheck` switches off. PRD FP-06 line 285 and IC `/prosecheck` > Stop phrases (line 411) say the whole prompt. **Built:** whole prompt, case-insensitive (`stop prosecheck` or `prosecheck off`). Anything else is an ordinary prompt.

10. **`PROSECHECK_DEFAULT_MODE` precedence (CONFLICTS 10).** PRD FP-04 line 246: the environment applies only when nothing valid is stored. IC Host environment (line 63): when set, it takes precedence over the stored level. **Built:** PRD. A stored valid level always wins; the environment word is used only when nothing valid is stored, then `full`. On the first session start the resolved level is written to the flag, so the environment word then becomes the stored level.

11. **`.pdf` as a deliverable (CONFLICTS 11).** PRD FP-06 line 290 lists `.pdf` among deliverables that get ledger rows; PRD FP-02 and the non-goals say `.pdf` is not a prose format. **Built:** `.pdf` and `.rtf` are not scored. They get a "not re-scored (binary format)" ledger row, consistent with FP-05.

12. **Number of file operands (CONFLICTS 12).** IC line 21 says "at most one file operand"; IC line 180 and PRD FP-01 line 168 say two or more still succeed. **Built:** success. The first file is scanned and a notice naming it goes to the error stream.

13. **Which operand is scanned (CONFLICTS 13).** IC line 106 says the last; IC line 180 and PRD line 168 say the first. **Built:** the first.

14. **`apply_patch` path limit (CONFLICTS 14).** PRD FP-05 line 264 says at most 16 distinct paths; IC `Post-tool-use reply` (line 260) says ten. **Built:** 16 (PRD FP-05 is the rule for what a ledger and a guard do; the IC's line is a reply-format note).

15. **Ledger record count (CONFLICTS 15).** PRD FP-05 line 265 says the newest 20 records; IC `Plugin config and ledger` (line 91) says 50. The IC defers "what a ledger records and how long it is kept" to the PRD. **Built:** 20.

16. **Ledger retention (CONFLICTS 16).** PRD Non-functional "Privacy" (line 57) and FP-06 (line 290): a ledger modified more than seven days ago is gone; seven days or younger is kept. IC `Config filenames` (line 65): deleted after one day at session start. The IC defers retention to the PRD. **Built:** seven days. Stale ledgers are pruned at session start, and `show` ignores any ledger older than seven days.

17. **Which transcript `stats` reads (CONFLICTS 17).** PRD FP-06 line 292: a named transcript wins over a newer one. IC `stats` > Transcript rows (line 650): the newer transcript is read. **Built:** the named transcript when readable (PRD line 292 and IC `transcript_path`). The newest transcript under `projects` is used only when no readable named path is supplied.

18. **Minimum slice for the session-prose score (CONFLICTS 18).** PRD FP-06 line 292: longer than 200 characters. IC `stats` > Reply (line 662): longer than 500. **Built:** 200 (PRD FP-06 is the behavioural rule).

19. **Model-dialect words (CONFLICTS 19).** PRD FP-04 line 236: model-dialect vocabulary "needs two hits." PRD FP-01 line 101: no such condition. **Built:** two or more hits (the more specific line). A single "genuinely" or "nuanced" does not fire family 2.

20. **Welcome versus silence (CONFLICTS 20).** PRD FP-04 line 235: the contract never names prosecheck. PRD FP-04 line 238 and IC Welcome block (line 201): the one-time welcome says prosecheck is installed and lists the four commands. **Built:** the welcome names prosecheck (it is shown once, to the user, on first run). The contract body stays silent.

Other spec inconsistencies found while building (not in CONFLICTS.md):

21. **Default-mode flag and welcome.** IC `hooks/prosecheck-activate.js` says the welcome appears when no mode flag exists. PRD FP-04 says the welcome appears on a fresh install. **Built:** the welcome is shown only when the flag file is absent and the resolved level is not `off`. The flag is written on the first start.

22. **Check label versus stats "not scored" marks.** IC `check` > Not scored says over-cap files show `over <KB> KB`. For archives it uses the archive cap in kilobytes (4096). **Built:** `over 512 KB` for plain text and `over 4096 KB` for archives and notebooks, exactly as the IC lists them.

23. **Stats hook registration.** `prosecheck-stats.js` is listed as a hook entry in IC `Plugin hooks`, but `/prosecheck stats` is also routed by the prompt-submit hook. **Built:** the stats file exists and emits the same block reply. It is not registered in `hooks/hooks.json`, so `stats` is not answered twice.

## Gaps the specification does not state, and what was assumed

Scoring (FP-01 is silent on how the base score is computed):

- Each score-moving family gets `5 + 2 * min(hits, 5)` points, plus 6 for a decisive family. Points are summed, then capped by the rules below, then raised to any floor, and clamped to 0–100.
- Caps: no score-moving family, 0. Only monotony (40), 20. Only rhythm kinds (40, 44), 40. Exactly one score-moving family, 40. Otherwise uncapped. Floors override caps.
- Small-document floors use `words < 120`; large-document floors use `words >= 400`. "Words" are runs of letters, digits, apostrophes, and hyphens in the masked prose.
- Words for confidence are counted in the masked prose (code and front matter excluded).

Detector internals:

- Masking (no findings inside): YAML front matter, CommonMark fenced code (with the closing-fence rule), inline code, blockquote runs of two or more lines, markdown table rows, badge-only lines.
- Sentence splitting: on `[.!?]` followed by whitespace, after stripping list markers and skipping headings.
- Sentence-length monotony and uniform paragraph length use the coefficient of variation with population standard deviation.
- The `--ci` interval is computed from eight sentence subsets (four quarters and four leave-one-quarter-out). Low and high are the min and max of those scores. The point score is unchanged. It needs at least four sentences.
- Character layer (FP-03): invisible means `Cc` other than tab/LF/CR, `Cf`, variation selectors, tag characters, and the explicit default-ignorable list. Kept positions are implemented as the spec lists them. The homoglyph table covers Cyrillic, Greek, and a few Armenian lookalikes; **Arabic-presentation lookalikes are not in the table** (the spec leaves the list open, and I did not find a safe mapping). Non-standard spaces are `Zs` other than U+0020. Line and paragraph separators become line feeds in cleanup only.
- CRLF is kept as CRLF in cleanup output; analysis treats CRLF as LF.
- Trailing whitespace (finding 68): a line ending in space or tab, text ending in two or more newlines, or whitespace before the first character. Cleanup removes trailing spaces and tabs on every line, leading blank lines, and all trailing whitespace; one final newline (CRLF or LF) is restored when the input had one.
- Cleanup runs on the full extracted text, not only the window.
- Degenerate repetition (71): six-word runs; fires when at least 20% of run positions repeat.
- Hyphen-for-en-dash (61) matches `YYYY-YYYY` with the first year earlier than the second.
- Family 25 requires the one-word answer immediately after the question mark.
- Family 37 counts paragraphs with two or more transitions; the sample names them.
- Family 40 needs at least three sentences; family 41 needs six.
- Archive reading: members larger than 64 MB are ignored (implementer's choice). Notebook cells that are not objects make the whole notebook empty.
- EPUB reading order: the OPF spine when present, otherwise sorted XHTML files. Items with the `nav` property are skipped.
- Error-message text: `empty input`, `cannot read input: <path>: ...`, `unknown option '<opt>' (see --help)`.

Plugin behaviour:

- Ledger file names: `.prosecheck-ledger-<session>` (characters outside `[A-Za-z0-9_]` replaced with `_`), or `.prosecheck-ledger` when no session id is supplied. Each row stores the base name, time, kind, score, band, phrase, up to five labels, flagged, and truncated. Failure reasons have the file's full path replaced by its base name.
- `show` lists rows newest first. The label cap is five. The `check` label cap is eight.
- `check` does not write a ledger row.
- The guard handles `Write`/`Edit`/`MultiEdit` (`file_path`), `NotebookEdit` (`notebook_path`, falling back to `file_path`), and `apply_patch` (`*** Add File:`, `*** Update File:`, `*** Move to:` lines with a colon). `*** Delete File` is not a scored path.
- Guard paths: skipped under `node_modules`, `.git`, the plugin root, and the exact instruction names or their stems with a non-prose extension. Relative paths resolve against `cwd`.
- The guard flags when the score is strictly above 40 (full) or 20 (strict). The nudge names the base name, the phrase, the score, the band, up to five labels, and asks for a fix.
- The doctor's Python check runs the detector on one built-in sample sentence.
- `init` appends the contract to an existing `AGENTS.md` between `<!-- prosecheck:contract:start -->` and `<!-- prosecheck:contract:end -->` markers. A second run detects the existing copy by either marker or the contract heading and leaves the file unchanged. The export names no machine path and no user name.
- The live contract (session start and subagent) names the absolute detector path, which the IC allows.
- Stats: assistant messages are counted once per message `id`. Token totals sum `output_tokens` and `cache_read_input_tokens` over those unique messages. The prose slice drops fenced code and keeps the last 40,000 characters.
- Prompt-submit reminder when the level is not `off`: a non-command prompt gets one line naming the live level.

Not done:

- `install/prosecheck-command.md` was not created; `commands/prosecheck.md` is the menu document the spec allows.
- No automated test suite is shipped. Verification was manual: the detector was run on sample Markdown, DOCX, XLSX, ODT, EPUB, and IPYNB files and on error paths, and each hook was run with sample payloads. The contract text was checked against the Interface Contract's string rules.

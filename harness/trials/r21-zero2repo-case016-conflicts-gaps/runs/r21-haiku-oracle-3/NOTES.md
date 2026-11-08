# NOTES

Implementation notes for prosecheck 0.9.3 built from `spec/` (export `store_hash` in `spec/export.meta.json`).
Layout and run instructions are in `README.md`. Checklist accounting for every id is in `SPEC_COVERAGE.md`.

Conventions used below: "PRD" = `spec/packs/04..16` (Full_PRD), "IC" = `spec/packs/17..40` (Interface_Contract).
Pack numbers are cited the way the spec's own MAP.md does them.

## 1. Conflicts and the choice made

The export was made with `--allow-open`, so the 23 contradictions listed in `spec/MAP.md` are unsettled
(CF-000011, 080, 081, 082, 083, 086, 114, 168, 179, 195, 196, 210, 211, 214, 219, 221, 234, 235, 236, 237,
238, 239, 240). The table gives, for each, what each side says, where it is, and what was built.

Rule applied: where the Interface Contract (IC) and the PRD disagree, the IC wins, because the IC is the
observable surface that tests exercise and the PRD says exact observables belong in the IC. Where both
sides are inside the IC, the majority or the more specific statement wins. Each row says which applied.

| Id | Side A (location) | Side B (location) | Built |
|---|---|---|---|
| CF-000011 | Ledger keeps "at most the newest 20 records" (PRD FP-05, pack 14, N-000436) | "Each ledger keeps its newest 50 records" (IC global observables, pack 20, N-000729) | **50** (IC wins). `hooks/lib.js` `LEDGER_KEEP`. |
| CF-000080 | "Every no-break space becomes an ordinary space" (PRD terminology, pack 05, N-000037) | no-break space (U+00A0) or narrow no-break space (U+202F) that holds digits, punctuation or guillemets together is not normalized (PRD FP-03, pack 12, N-000307) | **Exception kept**: such no-break spaces are kept, all others become U+0020. `scripts/detect.py` `nbsp_kept`. Low confidence in the spec itself. |
| CF-000081 / 082 / 083 | Usage message "goes to the error stream" (PRD FP-01, pack 10, N-000098) | `--help`/`-h` "prints the usage message to standard output and exits 0" (pack 18 N-000640; pack 21 N-000740; pack 10 N-000232) | **Standard output** for `--help`/`-h` (IC, 2 of 3 statements, and the usage is a success reply). Unknown options still go to stderr. |
| CF-000086 / 114 | "A decisive finding always lifts the score to at least 45, whatever the confidence" (pack 10, N-000134) | "A single decisive family raises it to at least 45 only when confidence is above `low`" (pack 10, N-000136; N-000137 agrees) | **Family rule**: one decisive family gets the 45 floor only at moderate or high confidence; two distinct decisive families get 65 at any confidence. |
| CF-000168 | "A prompt that contains `stop prosecheck` anywhere switches the tool off" (pack 13, N-000383) | "the same words with anything else before or after them are an ordinary prompt" (pack 15, N-000475; pack 31 N-000885 "entire prompt") | **Entire prompt only** (case-insensitive, trimmed). `hooks/lib.js` `routePrompt`. |
| CF-000179 / CF-000221 | Stats reads "the host-named `transcript_path`" and "a named transcript wins over a newer one" (pack 39 N-001107; pack 15 N-000544) | "When the projects folder holds a transcript newer than the named one, the newer transcript is read" (pack 39 N-001113) | **Named transcript wins** when `transcript_path` is supplied; the newest `.jsonl` under `CLAUDE_CONFIG_DIR/projects` is used only when it is absent. |
| CF-000195 / 196 | "Trim spaces and tabs at the end of every line" (pack 12, N-000312); "Two trailing spaces that end a line of prose ... are kept" (N-000314) | "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break ... That collapse is required" (pack 12, N-000330) | **Removed** (N-000330 is the more specific statement and is marked required). |
| CF-000210 / 235 | "Any `utm_source` parameter left in a link is an AI tracking parameter" (pack 10, N-000174) | "fires only when that whole host name is one of those domains" (N-000175, N-000176) | **Only the seven listed hosts** fire family 65. |
| CF-000211 / 214 | "the first file is scanned" (pack 10 N-000234; IC N-000719 and N-000783) | "the last one is the file scanned" (IC `scripts/detect.py`, N-000739) | **First file** is scanned (three statements vs one). A stderr notice names it. |
| CF-000219 | "a single sentence that opens with one of the transition words of 37 already fires transition clusters" (pack 10, N-000157) | "two or more sentence-opening transitions ... in one paragraph" (pack 10, N-000158) | **Two or more** per paragraph (the family's own definition). |
| CF-000234 | Hedge stacking (54) is writing advice with weight zero (pack 10, N-000119) | "Each sentence with stacked hedges adds to the score" (pack 10, N-000170) | **Advice, weight zero** (the family list says so). |
| CF-000236 | apply_patch scores "at most **16** distinct paths" (PRD FP-05, pack 14, N-000429) | "At most ten paths of one payload are scored" (IC post-tool-use reply, pack 24, N-000834) | **10** (IC wins). `hooks/lib.js` `APPLY_PATCH_CAP`. |
| CF-000237 | Ledger "last modification more than seven days old is gone" (PRD non-functional, pack 07, N-000069) | "A ledger untouched for more than one day is deleted at the next session start" (IC, pack 21/20, N-000702) | **One day** (IC wins): ledgers older than 24 h are deleted at session start. The seven-day statement is therefore never observable. |
| CF-000238 | "When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words" (PRD FP-04, pack 13, N-000390) | "`PROSECHECK_DEFAULT_MODE` ... when it is set, it takes precedence over the stored level" (IC, pack 19, N-000701) | **Environment wins** when it names a valid level (IC statement). `effectiveLevel()` in `hooks/lib.js`. |
| CF-000239 | session-prose score printed when the slice is "longer than 200 characters" (PRD FP-06, pack 15, N-000554) | "longer than 500 characters" (IC stats, pack 39, N-001117) | **500** (IC wins). `STATS_MIN_CHARS`. |
| CF-000240 | Tailing-negation form of catalogue 17 is "score-moving" (PRD pack 10, N-000126) | "Both forms of catalogue 17 are writing advice and carry weight zero" (IC pack 21, N-000750) | **Advice, weight zero** for both forms (IC wins). Both keys still appear: `17_negative_parallelism` and `17_tailing_negation`. |

Other tensions that are not in the MAP's contradiction list but that a reader will hit:

- **Hook-level stop phrase and mode storage.** `stop prosecheck` and `prosecheck off` store `off`. `/prosecheck on` stores `full`, not the last level used. (IC N-000904, N-000906.)
- **`/prosecheck status` and the doctor mode line report the effective level**, which is the environment level when set, otherwise the stored level. (Follows CF-000238.)
- **First-run flag write.** The spec says "later hooks see the stored level" and "including the default `full` when no flag existed" but does not say the flag is written. The activate hook writes `full` to `.prosecheck-active` when no valid flag exists. The welcome is keyed on the flag file's absence.
- **Ledger file name.** The spec names the files `.prosecheck-ledger` or `.prosecheck-ledger-<something>`. Built as `.prosecheck-ledger-<session_id>` with characters outside `[A-Za-z0-9_-]` replaced by `_`. Without a session id: `.prosecheck-ledger`.
- **Usage text beyond the first line** is free (IC N-000741). Written as a short description.

## 2. Things the spec does not state, and what was assumed

### Detector (`scripts/detect.py`)

- **Score formula.** The spec fixes bands, caps, floors, and families, not the arithmetic that produces a raw score. Built: each score-moving family fired contributes `6 + 3 * min(hits - 1, 6)` points (max 24), summed and capped at 100. Writing-advice families contribute nothing. Then caps and floors from the spec apply (single family <= 40, rhythm-only <= 40, sentence-length monotony alone <= 20, short- and long-document floors, decisive floors). Clean text scores 0.
- **Word count** for confidence and floors: runs of letters, digits, apostrophes, and hyphens (`words_of`), computed on the scanned window's prose.
- **Confidence reason text** is free and written in `score_document`.
- **Lexicons.** The spec gives the families by example and says some lists are the implementer's choice: hyphenated word pairs (family 4), marketing-slop phrases (69), promotional phrases (3), and the synonym clusters (8) are built from the examples in the spec. Emoji ranges, the Cyrillic/Greek/Armenian lookalike table (66), and the placeholder patterns (63) are also chosen here.
- **Family 1 inflection.** "An inflected form is the same word" is implemented as stem plus common suffixes (`-s`, `-es`, `-ed`, `-ing`, and `-e` variants). Irregular forms are not covered.
- **Family 6 "ends in a noun".** Not checked; only the four-word comma chain with at least one adjective-like word is required.
- **Family 11 notability.** The "two named outlets" rule is approximated as two capitalized tokens after the credit verb.
- **Family 25 question-answer.** The question is limited to 80 characters and must start with an auxiliary.
- **Family 41 and 55.** The spec says "strict alternation nearly every time" and "most of the forms that could be contracted are written out". Built as six sentences with alternating signs and each step at least half the mean length; and first-person share of at least 3 percent with at least three written-out forms and more than twice as many contracted forms.
- **Family 46** ("long document") is read as at least 300 words and no semicolon, with at most one open parenthesis.
- **Family 56 boldface** fires on one or more bold spans. The spec gives no threshold.
- **Family 60 curly quotes** counts all four curly quote characters, including U+2019 (apostrophe). Advice, so it does not move the score.
- **Family 70** needs at least 24 lines and at least three horizontal-rule lines.
- **Family 71 threshold.** Built as: repeated six-word runs are at least 20 percent of all six-word runs.
- **Character-layer counts** (62, 66, 67, 68) are computed on the raw window, not the masked prose. Code blocks are masked for the lexical families only. The spec does not say whether code is exempt from the invisible-character rule. Keeping it raw means a stray zero-width character inside a code fence is still reported.
- **Masking** uses line rules for fences (CommonMark opening and closing), blockquote runs of two or more lines, table rows (lines starting with `|`), badge lines, and YAML front matter. Inline code is blanked per line.
- **CRLF** is normalized to LF before analysis. A lone CR is kept (it is not an invisible character under the spec).
- **Sample text** is a 60-character-plus excerpt with newlines turned into spaces and `...` marking cuts.
- **Resampled interval (`--ci`).** Not specified beyond "low/high, 0-100, low <= high". Built: 40 seeded resamples (seed 1729) of half the sentences (8 for documents over 60 KB), 5th to 95th percentile, widened to include the point score. Note: the point score is never changed by `--ci`.
- **Archive-member size cutoff** (N-000291) is not enforced. Archives are capped only by the 4 MB file cap, which the detector itself does not check. The guard and `check` enforce the cap.
- **Extraction of unknown XML details.** Table and worksheet ordering follows the workbook and its relationships. Numeric cells are skipped. Docx and pptx paragraphs are joined with line feeds. EPUB chapters are read in name order, navigation and `head` excluded.
- **Plain text decoding.** Invalid UTF-8 bytes are replaced with U+FFFD. Without a BOM the input is decoded as UTF-8, not guessed.
- **Standard input.** `-` as an operand means standard input, as does no operand.
- **Cleanup scope.** Cleanup works on the whole extracted text, not only the 262,144-character window. The rescan checks in the tests use the window.
- **Zero-width kept positions.** Implemented as listed in FP-03; the bidi-control rule keeps bidi characters only when the document contains right-to-left script characters.
- **Invisible-character kept rule for TAG characters** keeps them only inside an emoji tag sequence that starts with U+1F3F4 (black flag).
- **Exit status** for a successful run with several files is 0 (IC N-000719).

### Plugin hooks (`hooks/`)

- **Config directory.** `CLAUDE_CONFIG_DIR`, else `~/.claude` (IC host environment).
- **Plugin root.** `CLAUDE_PLUGIN_ROOT`, else the parent of `hooks/` (the directory containing this repository).
- **Detector discovery.** `scripts/detect.py` under the plugin root, then `skills/prosecheck/scripts/detect.py`. The shipped tree has only the first.
- **Python lookup.** `python3`, then `python`, then `py` on PATH. A missing name is treated as "Python not found" only if none of the three launch.
- **Timeouts.** The detector run is killed at 8 s (plain text) or 15 s (archives and notebooks). A timeout is a failed check, not a hang.
- **Session-start contract.** Printed as plain text. The welcome comes first only on the first start.
- **Live contract paths.** The live contract (session and subagent) names the detector path (allowed by FP-04). The exported `AGENTS.md` does not (portable).
- **Export location.** `init` writes `AGENTS.md` and `.cursor/rules/prosecheck.mdc` in the directory named by the payload's `cwd` when present, otherwise the hook process's working directory.
- **Export section marker.** HTML comments `<!-- prosecheck:contract:start -->` and `...:end -->`. A second `init` checks for the start marker.
- **Cursor rule.** Shipped at `.cursor/rules/prosecheck.mdc` in the plugin root (IC N-000665 and N-001095). Its globs are written as one comma-separated line, which is how Cursor reads them.
- **Guard eligibility.** Extensions are the 20 formats. `.pdf` and `.rtf` are recorded as binary when they exist, and as an unreadable failure when they do not.
- **Guard skip list.** `node_modules`, `.git`, anything under the plugin root, and the instruction names (`claude.md`, `claude.local.md`, `agents.md`, `agents.local.md`, `skill.md`, `memory.md`) and their stems with a non-prose extension (or none). Skipped files are not recorded.
- **Failure reasons** (FP-05 N-000449..454): "Python not found on PATH", "the detector timed out", "detector output was not a structured report", "report has no numeric score", "detector produced no usable result" (shared by empty output and by a non-zero exit, as the spec requires).
- **Stats turn count.** Assistant turns are counted as distinct message ids (`message.id`, or the row's `uuid`). Repeated rows for one message do not add turns or tokens; the maximum usage value is taken. The spec does not say how repeated rows are handled.
- **Stats prose slice.** Assistant text is joined per message, fenced code removed, and the last 40,000 characters kept.
- **Show row ordering** is save order, newest first. Rows show "flagged" or "under threshold" only when labels exist.
- **Doctor settings check** writes and deletes a probe file in the config directory.
- **Doctor Python check** runs the detector on a short sample string.
- **Help reply** contains the lines the spec requires. The first line names the live level only.
- **Command replies** are plain text in the block `reason`. They avoid digits and other standalone integers where the spec forbids them (`show` empty ledger, `check` not-scored replies, doctor).

### Packaging

- **No build step.** Nothing to install. The detector is run with `python3 scripts/detect.py`; the hooks with `node hooks/<name>.js`.
- **`.claude-plugin/plugin.json` and `hooks/hooks.json`** are not specified by the spec. They are the host registration files that a Claude Code plugin needs. Schema taken from the common Claude Code plugin format; check against the host version in use.
- **Command menu document** at `commands/prosecheck.md` (a copy is at `install/prosecheck-command.md`). Front matter is minimal; the body is `/prosecheck $ARGUMENTS` as the spec requires.
- **Bundled skill file** (PRD: a file that instructs the host agent how to rewrite). Not shipped. The spec says the skill "is not a feature point" and "not a detector obligation" (PRD pack 06 N-000050, N-000051; pack 09 N-000092; IC N-000673).

## 3. Not built, and why

- **Bundled skill file and its rewrite instructions.** Not a feature point (PRD pack 06 N-000050..51). Not shipped.
- **Recorded-session demo, documentation checker, bundled evaluation script, status-line helper.** Listed as non-goals and "not product surfaces" (PRD pack 09 N-000093; IC N-000673).
- **PDF and RTF extraction.** Non-goal (PRD pack 09 N-000086). Both are binary and yield no prose.
- **In-place rewriting of `.docx`, `.epub`, `.odt`, `.ipynb`** (non-goal, pack 09 N-000091). Cleanup prints text only.
- **Hosted service, account, website.** Non-goal (pack 09 N-000089).
- **Authorship classification.** Non-goal (pack 09 N-000082); the score is described as a triage heuristic everywhere.
- **Member-size limit on archives** (N-000291, implementer's choice). Not enforced inside the detector (see section 2).

## 4. Verification

- `python3 -m unittest discover -s tests -v` runs the whole suite (82 tests: `tests/test_detector.py` for the detector, `tests/test_hooks.py` for the hooks; the hook tests need `node` on PATH and create their own temp config and work directories).
- The two acceptance-criterion ids in the spec, `N-000305` and `N-000309`, have tests named `test_N_000305_rescan_reports_zero_invisible_hits` and `test_N_000309_rescan_reports_zero_nonstandard_space_hits` (pack 12 AC list).
- The hook tests check the reply constraints from the IC (the `doctor`, `help`, `show`, `check`, `stats`, `init` shapes and the contract constraints for `lite`, `full`, and `strict`).

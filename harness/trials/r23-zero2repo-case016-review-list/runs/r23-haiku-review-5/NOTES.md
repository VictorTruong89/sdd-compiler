# prosecheck: notes on conflicts, choices, and unstated details

This file records (1) every disagreement between the files in `spec/`, with what each side says, where it is,
and what was built, and (2) what the specification does not state, with the assumption made.
Where the specification conflicts with itself, the more specific rule was preferred unless noted.
Section numbers below follow `spec/CONFLICTS.md`. "PRD" is `spec/Full_PRD.md`, "IC" is `spec/Interface_Contract.md`.

## 1. Conflicts

**1. Where the usage message goes.**
PRD FP-01 "Public entry" (lines 82-83): "The usage message goes to the error stream, so that standard output carries only reports."
PRD FP-01 "Boundary / error behavior" (line 167) and IC `scripts/detect.py` > Usage (line 110): help "prints the usage message to standard output and succeeds."
Built: `--help` and `-h` print usage to stdout, exit 0. Errors (unknown option, empty input, unreadable path) print only the JSON error object to stderr. Usage is never printed to stderr.

**2. Floor for a single decisive finding.**
PRD FP-01 "Normal behavior" (line 93): "A decisive finding always lifts the score to at least 45, whatever the confidence."
PRD FP-01 "Normal behavior" (line 94): "A single decisive family at `none` or `low` confidence does not take that 45 floor."
Built: line 94 (the specific rule). One decisive family raises the score to 45 only at `moderate` or `high` confidence. Two or more decisive families raise it to 65 regardless of confidence.

**3. Whether hedge stacking changes the score.**
PRD FP-01 "Normal behavior" (line 90): catalogue 54 is one of the 12 writing-advice numbers, "weight zero".
PRD FP-01 "Family rules" (line 128): "Each sentence with stacked hedges adds to the score."
Built: line 90, the explicit advice list. Hedge stacking is reported as a finding but never moves the score.

**4. Whether the tailing-negation form of catalogue 17 moves the score.**
PRD FP-01 "Normal behavior" (line 91): "The **tailing-negation form** is score-moving."
IC `scripts/detect.py` > Findings (line 148): "Both forms of catalogue 17 are writing advice and carry weight zero."
Built: the PRD. Tailing negation (`17_tailing_negation`) is score-moving. The parallelism form (`17_negative_parallelism`) is weight zero. The IC's "both forms" sentence was not followed.

**5. Whether every no-break space is turned into a space.**
PRD Terminology, "Character cleanup" (line 30): "Every no-break space becomes an ordinary space."
PRD FP-03 "What is normalized" (line 212): a no-break space or narrow no-break space is kept when it holds something together (digit on either side; before `: ; ! ? » › % €`; after `« ‹`).
Built: line 212 (the detailed rule). Those no-break spaces are kept in both cleanup and counting. All others become U+0020.

**6. Whether a markdown hard break's trailing spaces are kept.**
PRD FP-03 "What is trimmed" (line 214): two trailing spaces are kept. PRD FP-03 "Boundary / error behavior" (line 223): the collapse "is required, not optional."
Built: line 223. Trailing spaces and tabs are removed from every line, including two-space hard breaks.

**7. Whether every zero-width character in the text is invisible.**
PRD FP-01 "Normal behavior" (line 159): "A zero-width character inside the text is an invisible character."
PRD FP-03 "What is removed" (line 211) and "Cleanup agrees with detection" (line 215): a listed set of zero-width characters in listed positions is kept, and kept characters are not counted.
Built: the kept-position rules win for the listed positions (a job-doing ZWJ, ZWNJ, ZWSP, variation selector, soft hyphen between letters, and so on). Everywhere else they are invisible and counted. Line 159 is therefore read as "except where FP-03 keeps them".

**8. Whether any `utm_source` value triggers catalogue 65.**
PRD FP-01 "Family rules," chat reference markup (line 131): "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
PRD FP-01 "Family rules," AI tracking parameters (line 132): fires "only when that whole host name is one of those domains".
Built: line 132. Only the seven listed hosts fire. The host is read as far as a host name can continue, and a trailing sentence period is ignored.

**9. Whether `stop prosecheck` must be the whole prompt.**
PRD FP-04 "Normal behavior" (line 240): "A prompt that contains `stop prosecheck` anywhere switches the tool off."
PRD FP-06 (line 285) and IC `/prosecheck` > Stop phrases (line 411): the entire prompt, letter case ignored.
Built: the entire prompt (trimmed, case-insensitive) for `stop prosecheck` and `prosecheck off`. Anything else around the phrase is an ordinary prompt.

**10. Precedence of `PROSECHECK_DEFAULT_MODE`.**
PRD FP-04 "Boundary / error behavior" (line 246): the variable applies only when nothing valid is stored.
IC "Naming conventions" > Host environment (line 63): "when it is set, it takes precedence over the stored level."
Built: the IC. A valid environment value wins over the stored flag, and the stored flag is used otherwise, then `full`. Consequence: while the variable is set to a valid word, `/prosecheck off` and similar commands still write the flag but the variable determines the live level. This is noted here because it is surprising in use.

**11. Whether `.pdf` is a prose file.**
PRD FP-06 (line 290) and IC `show` > Empty ledger (line 582) mention `.pdf` deliverable rows. PRD Terminology (line 27), FP-02 (line 195), and the non-goals (line 68) say `.pdf` is not one of the twenty formats.
Built: `.pdf` and `.rtf` are not prose and are never extracted or scored. The guard records them as binary rows ("not re-scored"). The empty-ledger reply names `.docx` and `.pdf`, as both specifications require.

**12. How many file operands the detector accepts.**
IC `scripts/detect.py` (line 21): "at most one file operand". IC `scripts/detect.py` > Several file operands (line 180) and PRD FP-01 "Boundary" (line 168): two or more operands still succeed.
Built: two or more operands succeed. The first is scanned, and one notice line goes to stderr.

**13. Which operand is scanned when several are given.**
IC `scripts/detect.py` > Signature (line 106): "the last one is the file scanned." IC line 180 and PRD line 168: the first.
Built: the first operand (two sources against one). The notice line names the first operand exactly as given.

**14. Maximum paths in one `apply_patch` payload.**
PRD FP-05 (line 264): "at most **16** distinct paths." IC post-tool-use reply (line 260): "At most ten paths of one payload are scored."
Built: 16 paths are scored, as the PRD governs guard behavior. The IC's ten-path sentence is in the reply-format section, and the reply lists every flagged file.

**15. Records a session ledger keeps.**
PRD FP-05 (line 265): the newest **20** records. IC "Plugin config and ledger" (line 91): the newest **50**.
Built: 20. The IC defers "what a ledger records and how long it is kept" to the PRD.

**16. How long a session ledger is kept.**
PRD non-functional "Privacy" (line 57) and FP-06 (line 290): a ledger older than **seven days** is gone; seven days old or younger is kept. IC "Config filenames" (line 65): deleted when untouched for **one day**.
Built: seven days. Session start deletes ledgers older than seven days, and `show` does not list a ledger older than seven days. The IC defers retention to the PRD.

**17. Which transcript `stats` reads when a newer one exists.**
PRD FP-06 (line 292): "a named transcript wins over a newer one." IC `transcript_path` (line 681) and `stats` > Signature (line 646): the named transcript is read. IC `stats` > Transcript rows (line 650): the newer transcript is read.
Built: the named transcript wins (two sources against one). The newest-transcript search applies only when no transcript path is supplied.

**18. Minimum slice length for the session-prose score.**
PRD FP-06 (line 292): longer than **200** characters. IC `stats` > Reply (line 662): longer than **500**.
Built: 200. The PRD states the behavior and the IC states the reply shape, so the behavior threshold is the PRD's.

**19. Whether one use of a model-dialect word fires the family.**
PRD FP-04 "Normal behavior" (line 236): model-dialect vocabulary "needs two hits". PRD FP-01 "Family rules" (line 101): no two-hit condition.
Built: line 101 (one hit fires). The banned-list words still fire through the AI-vocabulary family, and the dialect family needs one hit.

**20. Whether the welcome can name prosecheck when the contract forbids it.**
PRD FP-04 (line 235): the contract is "silent — never ... name prosecheck". PRD FP-04 (line 238): the first-run welcome says "prosecheck is installed and on".
Built: the welcome names prosecheck because it is shown once to the user, as line 238 requires. The contract text that the agent follows tells the agent not to name prosecheck or report scores in its replies.

**Additional inconsistencies found while building (not in `spec/CONFLICTS.md`):**

**21. The IC's `doctor` "Shape" and the PRD's "four successful-check" wording.** Both agree. Built as four check lines plus a title and a closer, with `[OK]` on successful lines only.

**22. Stated `scripts/detect.py` error objects vs. the PRD error kinds.** The IC table gives exit 1 for empty input and unreadable input. The PRD gives a "structured error" for both. Built to the IC table: `empty input` exits 1, `cannot read input: ...` exits 1, unknown option exits 2.

**23. Stated check reply for `.pdf`.** The IC says the reply names "no readable text" and the base name. Built exactly so.

## 2. Things the specification does not state (assumptions)

**Scoring formula.** The PRD gives caps and floors but no base formula. Built: each fired score-moving family contributes `min(15 + 4 × (hits − 1), 27)` points; the total is capped at 100. Then, in order: one score-moving family caps the score at 40; a set of score-moving families that is only rhythm kinds (40, 44) caps it at 40; only sentence-length monotony (40) caps it at 20; decisive floors apply (65 or 45); then the short-document floors (under 120 words: two families from the listed set give 25, three give 45) and long-document floors (400 words or more: five families give 25, six give 45).

**Confidence.** `none` below 40 words; `low` below 120 words, or below 300 words with one score-moving family; `moderate` below 300 words; `high` at 300 words or more. Words are runs that start with a letter or digit and may contain apostrophes and hyphens.

**Scan preparation.** CRLF and lone CR are normalized to LF before scanning and cleanup. The 262,144-character window is the first 262,144 code points of the extracted text. Lexical patterns run on a masked copy of the window: YAML front matter, fenced code (CommonMark fences), inline code spans, blockquote runs of two or more lines, markdown table rows, and badge-only lines are blanked, with newlines and length kept. Character-layer families (62, 66, 67, 68) run on the raw window, so an invisible character inside a code fence is still counted. The spec does not say which way this goes.

**Sentences and paragraphs.** Sentences are split at `.`, `!`, or `?` followed by whitespace or end of line, and at each line end. Paragraphs are blank-line separated runs. Sentence-length monotony and uniform paragraph length use the word counts of those units.

**Pattern details the spec left open.** Family 1 uses the listed words with inflections. Family 2 (model-dialect) uses one hit to fire. Family 3 uses `leading` only as "leading provider/brand/company/firm/name/edge/player" to avoid matching "leading to". Family 4 (hyphenated pairs) and family 69 (canonical phrases) use a short list; the spec says the list is the implementer's choice. Family 6 (stacked adjectives) looks for four or more comma-or-"and"-joined words where a non-final word is a stock evaluative adjective or ends in an adjective suffix. Family 11 (notability) is a heuristic. Family 25 (question-answer) requires the question to be at most 80 characters. Family 55 (contraction absence) requires at least three first-person words, at least 2 % first-person share, no contraction, and at least three expanded forms. Family 61 requires the earlier year to be the smaller one. Family 70 (decorative rules) requires at least 24 lines and three rules. Family 71 (degenerate repetition) requires at least 20 % of six-word runs to occur more than once. Family 56 (boldface) fires on any `**bold**` span in prose.

**Counts.** Invisible characters, non-standard spaces, and homoglyphs are counted per character (or per run for homoglyph runs). Trailing-whitespace hits count each affected line, plus one for two or more final newlines, plus one for leading whitespace.

**Samples.** Excerpts are up to about 60 characters with `…` at cut ends and newlines turned into spaces. Character-layer samples name the code point and character position instead.

**`--ci` interval.** Bootstrap over sentences with a fixed seed: 30 resamples for text up to 50,000 characters, 8 above that. The interval is the minimum and maximum of the resampled scores, clamped to include the point score and to 0 through 100. It is omitted with a note when there are fewer than four sentences.

**Cleanup.** Visible text, combining marks, and non-Latin words are left as they are. Homoglyph folding applies only to runs that meet the homoglyph condition. Leading blank lines are removed, trailing whitespace on each line is removed, and one final line feed is restored only when the input ended with one. Extracted zip and notebook text is printed without a trailing newline, because extraction trims it.

**Extraction.** Paragraphs, slides, cells, and chapters are joined with a single line feed (the spec says "line breaks"), not a blank line. Plain text is decoded as UTF-8 with replacement characters for invalid bytes; UTF-16 with a byte-order mark is decoded as UTF-16. A zip whose XML cannot be parsed yields empty input. EPUB reads the spine of the OPF package, skips navigation documents and `head`, `style`, and `script` content, and falls back to sorted XHTML names if the package cannot be read. Notebook markdown cells are joined with a line feed; a notebook with a markdown cell whose source is neither a string nor a list of strings yields empty input.

**Plugin root and config.** The plugin root is `CLAUDE_PLUGIN_ROOT` when set, otherwise the parent of `hooks/`. The config directory is `CLAUDE_CONFIG_DIR`, otherwise `~/.claude`. The mode flag is `.prosecheck-active`, holding one word with no newline. Ledgers are `.prosecheck-ledger-<session>` (session characters outside `A-Za-z0-9_-` become `_`), or `.prosecheck-ledger` with no session id. Ledgers are JSON arrays.

**Session start.** When no mode flag exists, the effective level (environment, or `full`) is written to the flag, so later sessions see it and do not show the welcome again. When the effective level is `off`, the flag is still written and nothing is printed.

**Guard.** Paths are resolved against the payload `cwd`. Skipped without a ledger record: paths with a `node_modules` or `.git` segment, paths inside the plugin root, instruction-file names (`claude.md`, `claude.local.md`, `agents.md`, `agents.local.md`, `skill.md`, `memory.md`, and their stems with a non-prose extension). Extensions outside the 22 scored or binary extensions get no record. A missing file is recorded as failed with reason `cannot read file (not on disk)`. Only score-moving labels appear in nudges and ledger rows (advice keys are filtered out), capped at five. Failure reasons are `python not found`, `timed out after N s`, `detector output was not a structured report`, `report had no numeric score`, `no usable result from the detector`, and `detector failed: <stderr line>`.

**Check and show.** `check` shows up to eight labels. `show` shows up to five labels per row. Failed rows in `show` are shown with the reason. The empty-ledger reply is "nothing scored yet in this session" with the `.docx` and `.pdf` mention.

**Doctor.** The Python check runs the bundled detector on a short sample with a 20-second timeout. The settings check creates the config folder if needed and tests that it is writable.

**Init.** `AGENTS.md` is recognized by the marker `<!-- prosecheck:contract:start -->`. The export is appended after existing bytes with one blank line. The Cursor rule is copied from `<plugin root>/.cursor/rules/prosecheck.mdc`. That shipped rule is generated from the `lite` contract text, so it contains no detector step, no threshold, and no band phrase.

**Stats.** Assistant rows are deduplicated by `message.id`. Text blocks from several rows with one id are kept once each. The token totals use the last `usage` seen for that id. Fenced code is removed from the prose slice before the 200-character check.

**Hooks and exit codes.** Every hook exits 0. Malformed input is treated as an empty object. `prosecheck-stats.js` is shipped but not listed in `hooks/hooks.json`, because the spec's hook list does not say which host event it should answer; it prints the stats reply as plain text when run directly.

**Detector invocation.** Hooks find Python by trying `python3`, `python`, then `py` on `PATH`. The detector is called as `python detect.py -- <file>` so names beginning with a dash are safe. The lone argument `-` is treated as an unknown option, as the IC's rule for arguments beginning with `-` requires.

## 3. Verification performed

- Detector on sample texts: AI-style text scores 100 (pervasive tells); plain human-style prose scores 0 (clean); empty input, whitespace-only input, a missing path, an invalid archive, an unknown option, `--help`, `--clean`, two operands, and `--ci` all behave as the IC table says.
- Extraction from generated `.docx`, `.pptx`, `.xlsx`, `.odt`, `.epub`, and `.ipynb` files, with cleanup output checked.
- Character layer: zero-width spaces are removed; soft hyphens between letters and no-break spaces between digits are kept; mixed-script runs are folded in cleanup; whole non-Latin words are not folded.
- Timing: each adversarial 512 KB input (long invisible-character runs, long space runs, long fenced blocks, long tables, many short sentences, many list markers) finishes in about 1 second, within the 8-second budget. Several regular expressions whose whitespace classes could run across blank lines were quadratic on large input; they were tightened during this check.
- Hooks, run with an isolated `CLAUDE_CONFIG_DIR`: first-run welcome and once-only behavior; `/prosecheck` and `/prosecheck:prosecheck` routing; level changes; stop phrases; the unknown-word reply; doctor with four OK lines, with Python absent, and with the tool off; `check` on a readable file, a directory, a missing path, and an empty argument; the guard's Write, Edit, NotebookEdit, and apply_patch paths, including skips, binary and oversize rows, and a malformed payload; `show` ordering and per-session separation; `stats` on a named transcript and a missing one; `init` with existing and missing `AGENTS.md`, lite and full contracts, and the off state.
- Contract and help requirements (banned-word presence, `source code` preceded by `never` or `not`, the 40/20 targets, `--clean` at strict only, the portable export lines, help line content, doctor closers) checked by script.

Not verified: Windows and macOS launchers (`py` argument conventions), real Claude Code hook event payloads, and the host's own handling of the `PostToolUse` and `SubagentStart` envelopes.

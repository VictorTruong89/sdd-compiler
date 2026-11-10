# NOTES: prosecheck build

This file records how the specification was read and built. Every spec disagreement that the
rulings in `spec/RULINGS.md` settle is listed first, then disagreements the rulings do not cover,
then things the specification does not state and what was assumed. `spec/` is unchanged.

Abbreviations: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`, HW = `spec/Hardware_Requirements.md`.

---

## A. Disagreements settled by RULINGS.md

Each item gives both sides with their locations, then the ruling, then what was built.

1. **Where the usage message goes.** PRD FP-01 "Public entry" (line 82) says the usage message goes
   to the error stream. PRD FP-01 "Boundary" (line 167) says help prints it to standard output and
   succeeds. Ruling: help writes usage to stdout and exits 0; usage errors go to stderr.
   Built: `--help`/`-h` print usage to stdout, exit 0. Unknown options print a JSON error to stderr, exit 2.

2. **Floor for a single decisive finding.** PRD FP-01 "Normal behavior" line 93 says a decisive
   finding always lifts the score to at least 45. Line 94 says a single decisive family at `none`
   or `low` confidence does not get that floor. Ruling: the 45 floor always applies.
   Built: any decisive family sets score ≥ 45, whatever the confidence; two or more set ≥ 65.

3. **Hedge stacking and the score.** PRD FP-01 line 90 says catalogue 54 is weight-zero writing
   advice and must not change the score. Line 128 says each sentence with stacked hedges adds to
   the score. Ruling: 54 is writing advice with weight zero. Built: 54 is reported as a finding
   but never counts toward the score or any family count.

4. **Tailing-negation form of catalogue 17.** PRD FP-01 line 91 makes the tailing-negation form
   score-moving. IC `scripts/detect.py` > Findings (line 148) makes both forms weight zero. Ruling:
   both forms are weight zero. Built: `17_negative_parallelism` and `17_tailing_negation` are both
   advice. Neither moves the score or counts as a family.

5. **No-break spaces.** PRD Terminology "Character cleanup" (line 30) says every no-break space
   becomes an ordinary space. PRD FP-03 "What is normalized" (line 212) keeps some. Ruling: keep
   the no-break spaces that hold something together (line 212 list), normalise the rest.
   Built: U+00A0 and U+202F are kept when a digit is on either side, before `:;!?»›%€`, or after
   `«‹`. Other Zs spaces are normalised. Cleanup and the scan agree on which are counted.

6. **Markdown hard-break trailing spaces.** PRD FP-03 line 214 says two trailing spaces that end a
   line of prose are kept. Line 223 says they are always removed. Ruling: kept (line 214).
   Built: cleanup keeps exactly two trailing spaces on a non-blank line that is followed by another
   non-blank line. The detector still reports these lines under 68 (writing advice, no score effect).

7. **`utm_source` and catalogue 65.** PRD FP-01 line 131 says any `utm_source` in a link is 65.
   Line 132 says it fires only when the whole host name is one of the listed AI domains. Ruling:
   the host rule (line 132). Built: 65 fires only on `utm_source=<exact listed host>`, with the
   host ending at a character that cannot continue a host name.

8. **`stop prosecheck` placement.** PRD FP-04 line 240 says `stop prosecheck` anywhere in a prompt
   switches the tool off. PRD FP-06 line 285 and IC `/prosecheck` > Stop phrases (line 411) say only
   the entire prompt counts. Ruling: anywhere (FP-04 line 240).
   Built: a prompt containing `stop prosecheck` anywhere (any case) stores `off` and is blocked with
   a reply naming `off`. `prosecheck off` counts only as the entire prompt. Side effect: an ordinary
   sentence that contains the phrase is also blocked; this follows the ruling.

9. **`PROSECHECK_DEFAULT_MODE` precedence.** PRD FP-04 line 246 says the environment applies only
   when nothing valid is stored. IC "Naming conventions" line 63 says the variable takes precedence
   over the stored level. Ruling: a valid stored level wins (line 246).
   Built: stored valid level, then the environment word, then `full`. On first session start the
   effective level is written to the flag file.

10. **Whether `.pdf` is a prose file.** PRD FP-06 line 290 lists `.docx` and `.pdf` deliverables as
    "prose files" in the `show` empty-ledger text. PRD line 27 and line 195 say `.pdf` is not in the
    twenty formats. Ruling: `.pdf` is not a prose file; the wording of line 290 and the IC empty-ledger
    reply (line 582) stays as written.
    Built: `.pdf` and `.rtf` are not scored and are recorded as binary. The `show` empty-ledger reply
    uses the wording as written.

11. **How many file operands.** IC `scripts/detect.py` line 21 says "at most one file operand".
    IC line 180 and PRD FP-01 line 168 say two or more succeed. Ruling: two or more are accepted and
    succeed (IC line 180).
    Built: multiple operands succeed with exit 0.

12. **Which operand is scanned.** IC `scripts/detect.py` Signature (line 106) says the last
    operand is scanned. IC line 180 and PRD line 168 say the first. Ruling: the last one (IC line 106).
    Built: the last operand is scanned. Stderr gets one notice line naming the scanned file and the
    ignored ones, so the first operand also appears (see B1).

13. **Maximum paths in one `apply_patch` payload.** PRD FP-05 line 264 says at most 16 distinct paths.
    IC "Post-tool-use reply" line 260 says at most ten. Ruling: 16 (PRD line 264).
    Built: at most 16 distinct paths per payload.

14. **Records kept per ledger.** PRD FP-05 line 265 says the newest 20. IC "Plugin config and ledger"
    line 91 says the newest 50. Ruling: 50 (IC line 91).
    Built: each ledger file keeps its newest 50 records.

15. **How long a ledger is kept.** PRD Non-functional "Privacy" line 57 says seven days (kept at seven
    days or younger). IC "Config filenames" line 65 says one day. Ruling: seven days (PRD line 57).
    Built: ledgers older than seven days are deleted at session start and are not listed by `show`.

16. **Which transcript `stats` reads.** PRD FP-06 line 292 says a named transcript wins over a newer
    one. IC `stats` > Signature (line 646) and `transcript_path` (line 681) say the named one is read.
    IC `stats` > Transcript rows (line 650) says the newer one is read. Ruling: the newer transcript
    (IC line 650).
    Built: when `transcript_path` is named and a `.jsonl` under `CLAUDE_CONFIG_DIR/projects` is newer,
    the newer one is read. An unreadable named path gives the "no transcript" reply.

17. **Minimum slice length for the session-prose score.** PRD FP-06 line 292 says more than 200
    characters. IC `stats` > Reply (line 662) says more than 500. Ruling: 200 (PRD line 292).
    Built: the score line is printed when the trimmed slice is longer than 200 characters.

---

## B. Disagreements the rulings do not settle

B1. **Notice line for several operands.** IC line 180 says the notice line contains the *first*
operand. Ruling 12 scans the *last*. The notice must name the scanned file and the operands it
ignored, and both readings need the names to appear. Built: one line on stderr,
`detect.py: N file operands given; scanning only the last one, '<last>' (not scanned: '<first>', ...)`.
That contains the first operand exactly as given and the scanned operand.

B2. **Ledger age and listing.** PRD FP-06 line 290 says a ledger older than seven days is not listed
by a later session. IC line 65 says it is deleted at the next session start. Both are satisfied by
the seven-day rule: `show` ignores ledgers older than seven days, and session start deletes them.

B3. **Model-dialect family and "needs two hits".** PRD FP-04 line 236 says the model-dialect family
"needs two hits". PRD FP-01 line 101 gives no count. Built: the whole family 2 needs at least two hits.

---

## C. Things the specification does not state, and what was assumed

### Detector (`scripts/detect.py`)

- **Base score formula.** The PRD gives caps, floors, bands, and confidence rules, but no base formula.
  Built: each scoring family with `h` hits contributes `w * (1 - 0.5 ** e)`, where `e = h * 300 / max(words, 300)`
  and `w` is the family weight (default 8; decisive 14; rhythm 5; boldface 4; emoji 6; char-layer
  space 6; title case 5; decorative rules 5; degenerate repetition 8). The sum `S` gives
  `score = round(100 * (1 - exp(-S / 30)))`. The PRD caps and floors are then applied in this order:
  single family → 40; rhythm-only → 40; monotony-only → 20; decisive → 45 (and 65 for two);
  short-document floors (25/45); long-document floors (25/45). Advice findings never enter `S`.
- **Family count thresholds not given.** Built:
  - Boldface (56): one or more bold spans fire it.
  - Em-dash overuse (58): a paragraph with two or more em dashes counts once per paragraph.
  - Hyphen clichés (4), canonical marketing phrases (69), synonym clusters (8), and the promotional
    list (3) use the implementer's word lists. The "leading" phrase in 3 only fires after "the, a,
    an, our, your".
  - Emoji and pictographic ranges (57) are listed in `detect.py`.
  - Question-answer (25), inline-header lists (33), and the other regex families use the patterns
    given in the PRD text.
  - Mid-essay bullets (34) fire only when the document has no heading.
  - Mechanical alternation (41) fires after six sentences with four-word swings or more in alternating direction.
  - Contraction absence (55) needs at least three first-person words, at least 3% of words, at least three
    uncontracted forms, and at least 70% of contractable forms uncontracted.
- **Words.** Runs of letters, digits, apostrophes (straight or curly), and hyphens that contain a
  letter or digit. Words are counted on the masked text (excluded regions are not counted).
- **Sentences and paragraphs.** Sentences end at `.!?` followed by whitespace, or at a line break.
  Paragraphs are blocks of non-blank lines.
- **Masking.** Front matter, fenced code (CommonMark fence closing), inline code spans, blockquote runs of
  two or more lines, table rows and separator rows, and badge-only lines are blanked before the
  pattern families run. Character-layer findings (62, 66, 67, 68) are computed on the whole scan window,
  so an invisible character in a code block is still reported. This is a judgement call.
- **Character layer.** Invisibles are Cc (other than tab, LF, CR), Cf, variation selectors, the
  default-ignorable extras, and the TAG and VS supplement blocks. Keep rules are implemented for each
  position the PRD lists (emoji tags, CJK variation selectors, ZWSP beside no-space scripts, soft hyphen
  between letters, bidi marks in documents with RTL script, Mongolian and Khmer rules, ZWJ/ZWNJ beside
  joining scripts or emoji). Homoglyph folding covers Cyrillic, Greek, and Armenian lookalikes only.
  Arabic-presentation lookalikes are not in the map.
- **Heading and title rules.** Title case (59) skips headings with fewer than three words, all-caps headings,
  and headings starting with a non-letter. Fragmented headers (35) use a following line of four words or fewer and
  forty characters or fewer that shares a word of three letters or more with the heading.
- **Trailing whitespace (68).** Counts each line ending in a space or tab, the start of text when it begins
  with whitespace, and the end of text when it ends with two or more newlines. A CR before LF is not counted.
- **Scan window and truncation.** `truncated` is true when the extracted prose is longer than 262,144
  characters. Findings come only from the window.
- **Extraction.** `.docx`, `.pptx`, `.xlsx`, `.odt`, `.ods`, `.odp`, `.epub`, and `.ipynb` are read with the
  standard library. Archive members over 64 MB uncompressed are skipped. Malformed XML inside a readable zip
  gives empty input. An `.ipynb` whose markdown cells are not strings or lists of strings gives empty input.
  Plain text is decoded as UTF-8 (with optional BOM) or UTF-16 (with BOM). Other bytes are replaced.
- **Cleanup.** Applied to the full extracted text, not just the window. Output is written as UTF-8 with no
  added trailing newline beyond the one restored line ending.
- **`--ci` interval.** Bootstrap over sentences with a fixed seed (12 resamples; 4 when the window is over
  60,000 characters). The interval is the 10th to 90th percentile, widened to include the point score.
  Fewer than four sentences gives `score_ci: null` with a note.
- **Error output.** One JSON object on stderr (`{"error": ...}`), as the last non-empty line. Internal
  exceptions are reported as `internal error: <ExceptionClass>` with exit 1, with no traceback.

### Plugin hooks and commands

- **Config directory and flag file.** `CLAUDE_CONFIG_DIR`, else `~/.claude`. The flag `.prosecheck-active`
  holds the level word with no trailing newline. On session start with no flag, the effective level
  is written, and the welcome is shown once.
- **Welcome.** Shown only when the flag file did not exist at session start, and not when the effective level is `off`.
- **Ledger.** `.prosecheck-ledger-<sanitised session id>` (or `.prosecheck-ledger` with no session id),
  one JSON record per line. Records keep the base name, kind (`scored`, `skip`, `failed`, `binary`), score,
  band, hook phrase, up to five labels, flagged state, truncation state, and a reason for failures.
  Failure reasons contain no digits, so they do not collide with the size-skip figure.
- **Guard.** Paths come from `file_path`, `notebook_path`, or apply_patch `*** Add File:` / `*** Update File:` /
  `*** Move to:` lines, read from `command`, `input`, or `patch`. Relative paths resolve against `cwd`.
  Skipped silently: paths under `node_modules` or `.git`; files inside the plugin root; instruction names
  (`claude.md`, `agents.md`, and similar, plus their stems with a non-prose extension); non-eligible extensions;
  directories. Recorded as failed when the path is not on disk and the extension is eligible. Recorded as
  `binary` for `.pdf` and `.rtf`. Recorded as `skip` when the file is over its cap. The threshold is 40 at
  `full` and 20 at `strict`. A file is flagged only when its score is strictly above the threshold.
- **Failure reasons.** Five distinguishable kinds: `Python cannot be found`; `the detector produced no usable
  result`/`no output`; `the detector output is not a structured report`; `the report has no numeric score`;
  `the detector timed out`. Detector error messages are shown when the detector writes one.
- **Stats.** Assistant rows are de-duplicated by message `id` (last row wins). Rows without an id count
  individually. Output tokens and cache-read tokens are summed over the de-duplicated rows. Fenced code is
  removed from the joined assistant text before the last 40,000 characters are scored.
- **Doctor.** The Python probe runs the bundled detector on a short sample through standard input. The
  settings check writes and removes a temporary file in the config directory.
- **Check.** Quotes and a leading `@` are removed before the path is resolved. Plain text over 512 KB, and
  archives or notebooks over 4096 KB, are reported as over that cap. Timeouts are 8 s (plain) and 15 s (archive).
- **Init.** Writes `AGENTS.md` in the current working directory. The section is wrapped in
  `<!-- prosecheck:contract:start -->` and `<!-- prosecheck:contract:end -->` markers and is
  detected by the marker or the `## prosecheck writing contract` heading. The export does not contain the
  install path or the user name, and it is generated from the level (not from the environment).
- **Cursor rule.** Shipped at `.cursor/rules/prosecheck.mdc`. `init` copies it when the destination is
  missing, and writes a built-in copy if the shipped file cannot be read.
- **Contract wording.** At `full` and `strict`, the live contract names the detector path on this machine.
  The export names only `<DETECTOR>` and the one `CLAUDE_PLUGIN_ROOT` line.
- **Help reply.** The first line names the level. The reply lists each subcommand on its own line, with
  `off | on` sharing a line.
- **Detector path lookup.** `scripts/detect.py` under the plugin root, then `skills/prosecheck/scripts/detect.py`.
  The skill copy is not shipped; the lookup exists so the spec's fallback works.

---

## D. What was not built or verified

- The skill's rewrite instructions, the recorded-session demo, the bundled evaluation script, and the
  status-line helper are non-goals (PRD "Non-goals") and were not built.
- No Windows or macOS run was done. The code uses `py` as the last Python candidate and standard-library paths only.
- No `.pdf`/`.rtf` extraction (not required). No Arabic-presentation homoglyph map.
- The scoring weights and the word lists are the implementer's choice (see C). They were checked against
  the PRD's caps, floors, and bands with targeted inputs, not against a reference corpus.
- Verified by hand: CLI errors and help; scoring floors and caps; the character layer on sample text;
  the contract wording against the IC constraints (a script checked 21 properties); every hook in turn with a
  scratch config directory; the Python-missing path; off and lite modes; stats on a generated transcript;
  extraction on generated docx, pptx (one slide was malformed in the test fixture), xlsx, odt, epub, and ipynb files.

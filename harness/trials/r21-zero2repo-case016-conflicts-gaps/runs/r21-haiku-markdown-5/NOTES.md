# prosecheck 0.9.3: build notes

Build of the specification in `spec/` (`Full_PRD.md` = PRD, `Interface_Contract.md` = IC, `Hardware_Requirements.md` = HW).
Layout: `scripts/detect.py` (detector), `hooks/*.js` (plugin hooks), `commands/prosecheck.md` (menu document),
`hooks/hooks.json` and `.claude-plugin/plugin.json` (registration), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule).

## 1. Conflicts inside the specification

For each one: what each side says (with location), then what was built.

1. **Decisive families and the 45 floor.**
   PRD FP-01 says "A decisive finding always lifts the score to at least 45, whatever the confidence", and in the next sentence
   "A single decisive family at `none` or `low` confidence does not take that 45 floor."
   **Built:** the specific rule. One decisive family gives the 45 floor only at `moderate` or `high` confidence. Two or more give 65.

2. **Stop phrases.**
   PRD FP-04 (session-start/prompt section): "A prompt that contains `stop prosecheck` anywhere switches the tool off."
   PRD FP-06 and IC `/prosecheck` "Stop phrases": the entire prompt, and "the same words with anything else before or after them are an ordinary prompt."
   **Built:** entire-prompt match only (case-insensitive), for both `stop prosecheck` and `prosecheck off`.

3. **Which file is scanned with several operands.**
   IC `scripts/detect.py` "Signature": "When several operands are given, the last one is the file scanned."
   IC "Several file operands" and PRD FP-01: "the first file is scanned" and the error stream notes it.
   **Built:** the first operand. The notice on stderr is `detect.py: only the first file was scanned: <first operand>`.

4. **Ledger retention.**
   IC "Config filenames": "A ledger untouched for more than one day is deleted at the next session start."
   PRD non-functional "Privacy" and FP-06 `show`: kept for seven days; `show` does not list a ledger older than seven days.
   **Built:** both. Session start deletes ledger files untouched for more than one day (IC), and `show` ignores ledgers older
   than seven days (PRD). In practice the one-day deletion governs, since a later session never lists a ledger that a session
   start has already removed.

5. **Ledger size.**
   PRD FP-05: "At most the newest 20 records are kept." IC "Global observables": "Each ledger keeps its newest 50 records."
   **Built:** 50 (the IC states the number as a global observable).

6. **Session-prose score threshold in `stats`.**
   PRD FP-06: printed "only when that slice ... is longer than 200 characters." IC `stats` Reply: "When the scored slice is longer
   than 500 characters, the reply contains `session prose ai_tell_score`."
   **Built:** 500 (IC).

7. **`PROSECHECK_DEFAULT_MODE` precedence.**
   PRD FP-04: the environment supplies the level only "when nothing valid is stored."
   IC "Host environment": "when it is set, it takes precedence over the stored level."
   **Built:** the IC rule, so the environment value wins. Consequence: while the variable is set, `/prosecheck off` or `full` still
   writes the flag file, but the hooks keep using the environment value until it is unset.

8. **Named transcript versus newer transcript in `stats`.**
   PRD FP-06: "a named transcript wins over a newer one."
   IC `transcript_path`: "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
   **Built:** the named transcript wins (PRD). The newest-transcript search applies only when no `transcript_path` is given.

9. **How many `apply_patch` paths are scored.**
   PRD FP-05: "at most **16** distinct paths." IC post-tool-use reply: "At most ten paths of one payload are scored."
   **Built:** 10 (IC). Paths beyond ten are ignored and not recorded.

10. **Markdown hard-break spaces in cleanup.**
    PRD FP-03: "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
    The same section: "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required, not optional."
    **Built:** removed (the later, explicit "required" rule).

11. **Transition clusters (37) versus the formulaic-challenges note (36).**
    PRD FP-01 family 37: "two or more sentence-opening transitions ... in one paragraph."
    PRD FP-01 family 36: "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
    **Built:** 37 fires at two or more in one paragraph. The single-sentence note in family 36 is not implemented.

12. **Help output stream versus usage on the error stream.**
    PRD FP-01 "Public entry": "The usage message goes to the error stream, so that standard output carries only reports."
    PRD FP-01 boundary and IC `--help`: help prints usage to **standard output** and exits 0.
    **Built:** help goes to standard output (both the PRD boundary rule and the IC state this). Errors (unknown option, empty input, unreadable input) print only the JSON error object on stderr, with no usage text.

13. **Doctor's closing line and the `off` mode.**
    PRD FP-06 doctor: when only the mode is `off`, the closer "names the `on` command." IC doctor: that closer must contain the form the user typed and "scored", and not "not re-scored".
    **Built:** the IC wording; the closer names `/prosecheck on` (or the namespaced form) and says saved files are not scored.

14. **Cursor rule location.** IC "Host environment" says `init` looks for the shipped Cursor rule at `.cursor/rules/prosecheck.mdc` under the plugin root; PRD FP-06 says `init` "copies the shipped Cursor rule". Both are satisfied by shipping `/app/.cursor/rules/prosecheck.mdc`.

## 2. Gaps: not stated in the specification (choices made)

**Scoring.** The PRD gives caps, floors, bands and confidence but no base formula. Built:
- A "family" is a catalogue number; both forms of 17 count as 17 for the family count.
- Each score-moving family contributes `min(25, 6 + 8 * hits_per_100_words)`, with hits per 100 words over `max(words, 100)`.
  Rhythm families (40, 44) contribute a flat 6. The sum is capped at 100.
- The PRD caps and floors apply on top: single family capped at 40 (unless the decisive floor applies), rhythm-only at 20 (only 40 present)
  or 40, and the short-document and long-document word-count floors, and the decisive floors.
- Confidence thresholds follow the PRD exactly. Words are runs of letters/digits with inner `'`, `’` or `-`.

**Thresholds and word lists for the 62 machine-checked patterns** (the PRD names the families but not every term or threshold):
- 4 (hyphenated pairs), 60-61 wording, 69 (canonical phrases), 8 (synonym clusters), 6 (stock evaluative adjectives plus adjective suffixes),
  11 (outlets, follower counts), 14, 15, 26, 27, 36, 39, 47-48, 50 and 51 are the PRD's examples, extended by reasonable synonyms.
- 56 (boldface overuse) fires at **three or more** bold spans (the PRD gives no count).
- 46 (semicolon/parenthesis underuse): fires only on documents of 300 words or more with no semicolon and at most one `(`.
- 55 (contraction absence): needs at least 50 words, first-person pronouns at 2% or more of words, at least three uncontracted forms, and at least 80% uncontracted (or no contractions).
- 40 (sentence-length monotony): at least three sentences, coefficient of variation below 0.35. 44: at least four paragraphs, coefficient of variation below 0.4.
- 41 (alternation): at least six sentences in strict alternation with steps of at least 6 words.
- 42 (opener repetition): three or more sentences in a paragraph share their first two words.
- 58 (em dash): two or more em dashes in one paragraph.
- 59 (title case): three or more words, at least two major words, all capitalised; all-caps and digit/symbol-initial headings excluded.
- 70 (decorative rules): three or more horizontal-rule lines in a document of at least 24 non-empty lines.
- 71 (degenerate repetition): at least 20% of six-word runs occur more than once, and at least 12 words in total.
- 57 (emoji): the main emoji and pictograph blocks (U+1F000–U+1FAFF, U+2600–U+27BF, U+2B50, U+2B55).
- 63 (placeholder): the PRD's patterns, plus `[Company name]`-type slots with the company/client/person/name/place/source/product/author words.
- 65: exact host names from the PRD, with the host ending at a non-hostname character.
- 25 (question-answer): a short auxiliary question answered by one answer word and a period or exclamation mark.
- 13 (article title as proper noun): "The List/Index/Compilation/Collection/Catalogue/Guide/Overview of … is/are a/an/the" with up to six words in the title.

**Blanking rule.** The PRD's "inside the window, these generate no findings" list is implemented by blanking those lines before rules run
(front matter, fenced code, blockquote runs of two or more lines, table rows, badge lines, inline code spans).

**Character layer.**
- The set of "other default-ignorable or filler codepoints" is a short explicit list (U+115F, U+1160, U+3164, U+FFA0, U+034F, U+17B4, U+17B5, U+180B–U+180F, and the Cf category).
- The homoglyph map covers a documented subset of the Cyrillic, Greek and Armenian lookalikes (U+0430 and others). The PRD asks for a set, and this is not exhaustive.
- Keep rules follow the PRD's list. "Digit on either side" for the no-break space uses `str.isdigit()`.
- A document's RTL status (for bidi marks) comes from Hebrew, Arabic and related blocks anywhere in the window.

**Extraction.**
- `.docx`/`.pptx`: paragraphs and tables in document order; slides in numeric order.
- `.xlsx`: sheets in numeric file order (not the workbook's `<sheets>` order); each cell is one line.
- `.odt`/`.odp`/`.ods`: `text:s` becomes spaces, `text:tab` a tab, `text:line-break` a newline; annotations are skipped.
- `.epub`: spine order from the OPF (falls back to sorted file names); files with `epub:type="…nav…"` are skipped; script, style, head and nav content are removed; tags are stripped and entities decoded.
- `.ipynb`: markdown cells joined by newlines; any malformed cell list yields empty input.
- Archive member size cutoffs are not applied inside the detector (the PRD leaves that to the implementer and the plugin checks the file size on disk).
- Unknown extensions are read as plain text (per the IC's note on `.py`).

**Cleanup.**
- CRLF and CR line endings become LF before analysis and cleanup.
- Line and paragraph separators (U+2028/2029) become line feeds.
- Non-standard spaces other than the kept no-break spaces become U+0020.
- Trailing spaces and tabs on each line are removed, leading blank lines are removed, and the text ends with one line feed only if the input did.

**Interval (`--ci`).** 30 deterministic resamples of the prose sentences (fixed seed 20240601); the interval is the 5th to 95th percentile, clamped so it contains the point score. The point score is unchanged.

**Exit codes and messages.** `empty input` (exit 1); `cannot read input: <path> (...)` (exit 1); `unknown option '<opt>' (see --help)` (exit 2). The notice line for several operands is plain text on stderr; the failure JSON stays the last line.

**Hook behaviour.**
- Plugin root: `CLAUDE_PLUGIN_ROOT` when set, else the parent of `hooks/`. Config directory: `CLAUDE_CONFIG_DIR`, else `~/.claude`.
- The stored level is written on session start when the flag file is missing or invalid, and the welcome is printed only when the flag file did not exist.
- Level resolution: `PROSECHECK_DEFAULT_MODE` (if valid), else the stored flag, else `full`.
- Guard: `apply_patch` paths are read from lines beginning `*** Add File:`, `*** Update File:` or `*** Move to:`, which must carry a colon. `NotebookEdit` uses `notebook_path`, falling back to `file_path`.
- Guard: a path that does not exist is recorded as failed (`file could not be read (not found on disk)`). Directories are ignored. Files over the cap are recorded as skipped with the limit in bytes.
- Guard: "Python not found", "the detector timed out", "the detector output was not a report", "the report had no numeric score", and "no usable result from the detector" are the five distinct failed-check reasons. An empty result shares the last reason.
- Ledger rows hold the base name, kind, score, band, phrase, labels (at most five), and flags. No document text and no full path.
- `check` strips one leading `@` and one pair of quotes; relative paths resolve against the payload `cwd` (or the process cwd).
- `check` on a PDF or RTF file says `no readable text`. An unreadable path says `cannot read`.
- `init` writes to the payload `cwd` (or the process cwd). It wraps the contract in `<!-- prosecheck:contract:start/end -->` markers and detects an existing copy by those markers or the `## Prose writing contract` heading.
- `stats` dedupes assistant rows by `message.id`; text is taken from `text` content parts; fenced code is removed before the last 40,000 characters are scored.
- Doctor's Python probe runs the detector on a fixed two-sentence sample from stdin.
- `hooks/hooks.json` uses the Claude Code `hooks` format. The `PostToolUse` matcher is `Write|Edit|MultiEdit|NotebookEdit|apply_patch`.
- The command menu file is `commands/prosecheck.md`, with the `$ARGUMENTS` body the PRD describes (the `install/prosecheck-command.md` alternative is not created).
- The bundled skill is not shipped. The detector check falls back to `skills/prosecheck/scripts/detect.py` as the IC describes, so a later skill bundle works without changes.

## 3. What was verified here

Verified by running the code (Linux, Python 3.13, Node 22). The hidden tests and a live Claude Code session were not available.
- Detector: help, unknown option (exit 2), missing path, empty input, bad zip, PDF, `--clean` on plain text, docx, epub, odt and ipynb, BOM and UTF-16 input, two-operand notice, `--` with a dashed file name, `--ci` on short and long documents, and the 262,144-character window with a 524,288-byte input.
  Timings on 262,144-character and 400,000-invisible-character inputs were under one second.
- Character layer: zero-width space removed, Cyrillic lookalikes folded in a Latin word, no-break space kept after a digit, trailing spaces and extra final blank lines removed.
- Hooks: session start (welcome once, flag written), subagent envelope, prompt reminder, all twelve subcommands, stop phrases, `on`/`off` persistence, unknown word, `check` (scored, quoted, missing, PDF, no path), `show` (newest first, per-session ledgers), `doctor` (four lines and closers, both namespaces, Python missing), `init` (idempotent, lite/full/strict export rules), `stats` (named transcript, missing transcript).
- Guard: flagged write, unflagged edit (silent), `apply_patch` with two paths, PDF binary record, `CLAUDE.md` skip, missing file recorded, Python missing recorded.
- Contract text: banned vocabulary present at every level; "source code" always preceded by `never` or `not` in its sentence; full contains 40 and no `--clean`; strict contains 20 and `--clean`; lite contains neither 40 nor "light tells".
- A bug found and fixed: `mkdir -p` (recursive) looped forever under an unwritable path such as `/proc/…`. Directory creation is now bounded (`ensureDir`).

## 4. Known limits

- The score formula, lists and thresholds in section 2 are this build's choices; the PRD leaves them open. Expect the numbers to shift when those choices are tuned, though the caps, floors, bands and confidence rules follow the PRD.
- Windows and macOS were not exercised. The Python lookup is `python3`, then `python`, then `py` (with no `-3` argument).
- Each hook is a standalone Node script. Nothing here was loaded into a real host, so the host's own event payloads (field names beyond those in the IC) are untested.

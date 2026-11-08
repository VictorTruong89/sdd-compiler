# prosecheck: build notes

What is here, how it was checked, and every place the spec disagreed with itself, was silent, or
needed a choice. Spec ids are `N-000nnn`. Pack numbers are from `spec/MAP.md`.

## What was built

| Path | What it is |
| --- | --- |
| `scripts/detect.py` | Standard-library detector: extraction of the 20 formats, 71-pattern scan, 0–100 score and bands, `--clean`, `--ci`, error objects. |
| `hooks/prosecheck-lib.js` | Shared Node helpers: level storage, detector bridge (python3, python, py), per-file scan, contract texts, ledger. |
| `hooks/prosecheck-activate.js` | session-start hook: welcome once, then the writing contract. |
| `hooks/prosecheck-tracker.js` | prompt-submit hook and the `/prosecheck` command router (levels, status, help, show, check, doctor, init, stats, stop phrases). |
| `hooks/prosecheck-stats.js` | `stats` implementation (also runnable as a hook). |
| `hooks/prosecheck-subagent.js` | subagent-start hook: the contract in the SubagentStart envelope. |
| `hooks/prosecheck-guard.js` | post-tool-use hook: saved-file guard for Write, Edit, MultiEdit, NotebookEdit, apply_patch. |
| `hooks/hooks.json`, `.claude-plugin/plugin.json` | Registration of the hooks and the plugin manifest. Not in the spec's files list; added so the plugin loads. |
| `commands/prosecheck.md` | Slash-command menu document (`$ARGUMENTS` forwarding). |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule copied by `init`. Generated from the same contract text as the hooks. |
| `tests/test_detector.py`, `tests/hooks.test.js` | 35 detector tests and 23 hook/command tests. Run `python3 -m unittest discover -s tests` and `node --test tests/hooks.test.js`. |
| `SPEC_TRACE.md` | Every checklist id and where it is implemented or tested. |

Nothing was fetched from the network. No existing implementation was consulted.

## Verification

- `python3 -m unittest discover -s tests`: 35 tests, all pass (Python 3.13 here; the code uses only 3.9-compatible syntax).
- `node --test tests/hooks.test.js`: 23 tests, all pass (Node 22).
- Manual runs: every hook exits 0 on malformed input and with Python missing; the guard, `check`, `show`, `init`, `doctor`, `stats` produce the replies the spec describes.
- Timing: a full 262,144-character window scans in under 1 s, including adversarial long-line inputs (after bounding regex gaps).

## Conflicts in the spec, and what was built

Sixteen conflicts are marked UNSETTLED in `spec/MAP.md` (the export was made with `--allow-open`). The
others below were found while reading and are not in the unsettled list.

1. **Ledger retention count (CF-000011).** `N-000436` (FP-05, pack 14): "At most the newest 20 records are kept." vs `N-000729` (Interface, pack 20): "Each ledger keeps its newest 50 records." Built: **20**. The interface defers to the PRD for retention ("What a ledger records and how long it is kept are the PRD's rules").

2. **Ledger age (not in the unsettled list).** PRD `N-000069`/`N-000528`/`N-001040`: a ledger older than seven days is gone and not listed. Interface `N-000702` (pack 19): "A ledger untouched for more than one day is deleted at the next session start." Built: **seven days** for both listing and deletion at session start, because the PRD is the stated authority for retention and one day would make the seven-day rule impossible.

3. **Usage message stream (CF-000081, CF-000082, CF-000083).** `N-000098` (pack 10): "The usage message goes to the error stream" vs `N-000232`/`N-000640`/`N-000740`: `--help`/`-h` prints usage to standard output and exits 0. Built: **`--help`/`-h` print usage on stdout**, exit 0. Error paths print only the JSON error object on stderr (no usage). The `N-000098` sentence was read as applying to usage printed on failure.

4. **Decisive-finding floor (CF-000086, CF-000114).** `N-000134`: a decisive finding "always lifts the score to at least 45, whatever the confidence" vs `N-000136`/`N-000137`: a single decisive family reaches 45 only when confidence is above `low`. Built: **the `N-000136`/`N-000137` rule**: one decisive family gives a floor of 45 only at `moderate` or `high` confidence; two or more distinct decisive families give a floor of 65.

5. **Non-breaking space rule (CF-000080).** `N-000037` ("Every no-break space becomes an ordinary space") vs `N-000307` (exception for a no-break space that holds digits or punctuation together). Built: **the `N-000307` exception applies**. A U+00A0 or U+202F with a digit on either side, or before `: ; ! ? » › % €`, or after `« ‹`, is kept and not counted.

6. **Stop phrase (CF-000168).** `N-000383` ("A prompt that contains `stop prosecheck` anywhere switches the tool off") vs `N-000475` ("the same words with anything else before or after them are an ordinary prompt"). Built: **entire-prompt match only** (`N-000475`, and `N-000885`/`N-000886`: "the entire prompt"). Case-insensitive.

7. **Trailing spaces and hard breaks (CF-000195, CF-000196).** `N-000314` (keep two trailing spaces as a markdown hard break) vs `N-000330` (remove trailing whitespace even when meant as a hard break). Built: **trim** (`N-000330` says "required, not optional").

8. **`utm_source` (CF-000210).** `N-000174` ("Any `utm_source` parameter ... is an AI tracking parameter") vs `N-000175` (only the seven named hosts). Built: **the seven named hosts only** (the more specific rule). The host name is matched whole, with a trailing period removed.

9. **Which file is scanned with several operands (CF-000211, CF-000214).** `N-000234`/`N-000719`/`N-000783` ("the first file is scanned") vs `N-000739` ("the last one is the file scanned"). Built: **the first**. Most of the spec says first, and `N-000783` repeats it.

10. **Transition clusters (CF-000219).** `N-000157` (a single transition opener "already fires transition clusters") vs `N-000158` (two or more per paragraph). Built: **two or more per paragraph** (the rule text in FP-01 itself).

11. **Named transcript vs newer transcript (CF-000179, CF-000221).** `N-001107` and `N-000544`: the named `transcript_path` wins. `N-001113`: "the newer transcript is read". Built: **the named transcript wins** whenever `transcript_path` is supplied and readable; the newest transcript under `projects/` is used only when none is named.

12. **Stats score line threshold (not in the unsettled list).** PRD `N-000553` (FP-06, pack 15): the session-prose score is printed when the slice is "longer than 200 characters". Interface `N-001115` (pack 39): "When the scored slice is longer than 500 characters". Built: **500** (the interface is the implementer-facing contract for the reply). Change `SCORE_MIN_CHARS` in `hooks/prosecheck-stats.js` to 200 to follow the PRD instead.

13. **`apply_patch` path limit (not in the unsettled list).** PRD `N-000429`/`N-000430` (FP-05): "at most **16** distinct paths" are scored. Interface `N-000834` (pack 24): "At most ten paths of one payload are scored." Built: **16 are scored** (the PRD's rule). Set `MAX_GUARD_PATHS` in `hooks/prosecheck-lib.js` to 10 to follow the other.

14. **Welcome vs off (not in the unsettled list).** `N-000370`/`N-000386` say the welcome is shown on the first start of a fresh install, while `N-000335`/`N-000791` say off emits nothing. Built: the welcome is shown on a fresh install **unless the effective level is off**, and then the flag is not written.

## Choices where the spec is silent or left it to the implementer

**Score.** The spec gives bands, caps, floors and families, but no base weights. Built:
- Each scoring family adds `10 + 2 × min(hits − 1, 4)` points (so 10 to 18); rhythm families (sentence-length monotony, uniform paragraphs) add 6. Total capped at 100.
- Caps: rhythm-only documents at 40 (20 when only sentence-length monotony fired); a single score-moving family at 40 unless the single-decisive floor applies.
- Floors from the spec are applied after the caps (`N-000135`–`N-000139`).
- Advice families (weight zero) never count, including the parallelism form of 17.

**Words and sentences.** Words are runs of letters, digits, apostrophes and hyphens (`N-000139`). Sentences are split at `.`, `!`, `?` and newlines. Paragraphs are blank-line separated runs of the masked text.

**Code masking (`N-000149`).** Fenced blocks (CommonMark closing rule), inline code spans, runs of two or more blockquote lines, table rows, badge lines, and YAML front matter are blanked for lexical rules. Character-layer rules (62, 66, 67, 68) run on the unmasked window, because cleanup changes the unmasked text.

**Family details the spec leaves open.**
- 2 (model dialect) needs two hits, as stated in the FP-04 text (`N-000359`–`N-000362`).
- 3 (promotional): the three-sentence marketing-opener rule is implemented; "leading" is matched as a bare word, as written.
- 6 (stacked adjectives): no part-of-speech tagging. A run of four or more comma- or "and"-joined words with at least one adjective-like word fires.
- 8 (synonym cycling): plural and -es forms count as the same word.
- 11 (notability): approximated with a capitalised-outlet heuristic.
- 33–35, 37, 42, 44, 46, 55, 58–61, 63, 70, 71: thresholds chosen where the spec says "a few", "several", "noticeable share", or "a fifth or more": opener repetition needs 3 sentences in a paragraph; bold overuse needs 3 spans; alternation needs 6 sentences with differences of at least 6 words; contraction absence needs at least 3 first-person words making up 2% or more of the words, and written-out forms outnumbering contractions by 2 to 1; semicolon underuse needs 300 or more words; degenerate repetition fires at 20% of six-word runs repeated; decorative rules need 3 rules and 24 or more lines.
- 4, 19, 22, 69 (word lists): the spec says the list is the implementer's choice. The lists in `scripts/detect.py` are a reasonable subset.
- 66 (lookalikes): the confusable table is a subset of Cyrillic, Greek and Armenian letters (`_CONFUSABLES`), each mapped to its ASCII letter.
- 7, 9, 28, 29, 43, 45, 49, 52, 53: no detector, as the spec says. They are never reported.

**Character layer.** Removal set = Unicode categories Cc (except tab, LF, CR) and Cf, variation selectors, Mongolian free variation selectors, and a few filler code points. Kept in place (per FP-03): TAG characters after a black-flag base; variation selectors after emoji, symbols, or CJK (or before a combining keycap); ZWJ/ZWNJ beside Indic/Arabic/Hebrew scripts or emoji; ZWSP beside CJK, Thai, Lao, Khmer, or Myanmar; soft hyphen between two letters; bidi controls when the text contains Hebrew or Arabic. Cleanup and detection share one function, so a rescan of cleaned text reports zero.

**Cleanup output.** `--clean` runs on the whole extracted text (not just the window). CRLF and lone CR become LF at extraction, so line endings are not counted as invisible characters.

**Intervals (`--ci`).** A deterministic bootstrap (400 resamples, seed 20240601) over sentence-level hit counts, scaled by density. It is an estimate, not a formal confidence interval. Fewer than four sentences gives `null` and a note.

**Archives.** Extraction is standard-library only (`zipfile`, ElementTree, `html.parser`). Notebook cells use `source` as string or list. Numeric spreadsheet cells are not extracted (the spec says they need not be). No archive-member size cutoff was imposed beyond the file-size caps (`N-000291` leaves it to the implementer).

**Guard.**
- Instruction files (`claude.md`, `agents.md`, `skill.md`, `memory.md`, and their local variants, and their stems with a non-prose extension) are skipped without a ledger record.
- Files under `node_modules`, `.git`, or the plugin's own install tree are skipped. Because the plugin root defaults to the directory above `hooks/`, a repository that is itself the plugin root (as `/app` is) skips files inside it. This follows the spec's rule literally.
- `apply_patch` paths need the colon after `Add File`, `Update File`, or `Move to`.
- `NotebookEdit` scores `notebook_path`, and falls back to `file_path` when there is no notebook path.
- Relative paths resolve against the payload `cwd` when one is supplied, otherwise against the hook's working directory.
- Five check failure reasons are kept distinct (`REASON` in `prosecheck-lib.js`). An empty result and an exit with no usable result share the same reason, as the spec requires.

**Level and environment.** `PROSECHECK_DEFAULT_MODE` (when a valid word) overrides the stored level. Otherwise the stored word is used, else `full`. On session start, a non-off effective level is written to the flag file, so later hooks see it (`N-000379`).

**Doctor.** The Python check runs the detector on a fixed sample sentence and requires a numeric score. The mode line, the detector line, the Python line and the settings line each carry only their own label word, as `N-001003`–`N-001016` require. Filesystem paths are kept off those lines.

**Init.** `AGENTS.md` gets one section beginning with the heading `## Prose writing contract`. The presence check looks for that heading. Existing bytes are kept as the prefix. The exported contract names no machine path and no user name. At `full` and `strict` it names `CLAUDE_PLUGIN_ROOT`, `skills`, and `plugins` on one line. At `strict` it names `--clean`. At `lite` it names none of these.

**Live contract.** At `full` and `strict` the live contract includes the detector path (the spec allows this for a live session). The lite contract has no threshold numbers and no detector path.

**Stats.** Assistant rows are deduplicated by `message.id` (rows without an id count individually). Token totals sum over the unique rows.

**Ledger file names.** `.prosecheck-ledger-<session>` with the session id reduced to `[A-Za-z0-9_-]`, up to 80 characters. Without a session id: `.prosecheck-ledger`.

**Cursor rule globs.** Written as the comma-separated string Cursor reads, with exactly the eight prose globs.

## Not done, or only approximated

- The pattern rules are regular-expression heuristics written from the spec's wording, not a reference implementation. Labels, samples, and the exact counts for some families may differ from what the hidden tests expect; the families most likely to differ are 6, 8, 11, 33–35, and 55.
- The skill file that the spec mentions (`skills/prosecheck/…`) is not shipped. The detector lookup does check that path, so a skill that provides it would be found.
- `/prosecheck check` takes one path token (optionally one pair of matching quotes and one leading `@`), as the spec says; a path with spaces must be quoted.
- No `install/prosecheck-command.md` file. The menu document is at `commands/prosecheck.md` only (the spec allows either or both).
- The welcome text does not change with the level; it always mentions the same caps and commands.

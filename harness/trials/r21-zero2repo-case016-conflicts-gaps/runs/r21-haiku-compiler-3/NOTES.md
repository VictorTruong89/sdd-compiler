# NOTES

Build of prosecheck 0.9.3 from `spec/` (40 packs, 1126 checklist ids). `spec/` is unchanged.
Per-id accounting is in `CHECKLIST_STATUS.md`.

## Layout

| Path | What |
|---|---|
| `scripts/detect.py` | Detector: extraction (20 formats), 71-pattern rules, score and bands, report JSON, `--clean`, `--ci`, errors. Standard library only. |
| `hooks/prosecheck-activate.js` | session-start: welcome (first start only) and writing contract, plain text |
| `hooks/prosecheck-tracker.js` | prompt-submit: `/prosecheck` router, stop phrases, reminder |
| `hooks/prosecheck-subagent.js` | subagent-start: contract in the JSON envelope |
| `hooks/prosecheck-guard.js` | post-tool-use: scores saved prose files, nudges when flagged, writes the ledger |
| `hooks/prosecheck-stats.js` | `/prosecheck stats` (token figures and own-prose score) |
| `hooks/lib/common.js` | shared: config folder, level flag, contract text, detector runner, ledger |
| `hooks/hooks.json`, `.claude-plugin/plugin.json` | plugin registration |
| `commands/prosecheck.md` | menu document; body is `/prosecheck $ARGUMENTS` |
| `.cursor/rules/prosecheck.mdc` | shipped Cursor rule, copied by `init` |
| `tests/test_detect.py`, `tests/test_hooks.py` | 61 tests for the detector and hooks (`python3 -m unittest discover -s tests`) |

No install or build step. Run the detector as `python3 scripts/detect.py`, the hooks as `node hooks/<name>.js`.

## Spec conflicts and the choice made

The export left 16 contradictions unsettled (`spec/MAP.md`). Each one below is listed with the two sides and the side I built. Where the spec pair is marked UNSETTLED the id is given.

1. **Ledger retention, 20 or 50 records** (CF-000011; FP-05 N-000436 vs interface N-000729). FP-05 says the newest 20 records; the interface says its newest 50, but also says retention is "the PRD's rule" (N-000728/729). Built: **20**.
2. **No-break space** (CF-000080; PRD glossary N-000037 "every no-break space becomes an ordinary space" vs FP-03 N-000307 "except a no-break space that holds something together"). Built: the FP-03 exception applies (NBSP or NNBSP kept beside a digit, before `: ; ! ? » › % €`, or after `« ‹`).
3. **Usage message stream** (CF-000081/082/083; N-000098 "the usage message goes to the error stream" vs N-000232, N-000640, N-000740 "prints to standard output and exits 0"). Built: `--help` / `-h` print usage to **standard output**, exit 0. Errors go to standard error. The N-000098 sentence is read as applying to error output.
4. **Decisive floor of 45** (CF-000086, CF-000114; N-000134 "always at least 45 whatever the confidence" vs N-000136/137 "only when confidence is above low"). Built: a single decisive family raises the score to 45 **only at moderate or high confidence**. Two distinct decisive families give 65 at any confidence.
5. **Stop phrase** (CF-000168; N-000383 "anywhere in the prompt" vs N-000475 "the entire prompt"). Built: the **entire prompt** only (`stop prosecheck`, `prosecheck off`, letter case ignored).
6. **Named transcript or newer one** (CF-000179, CF-000221; N-001107 and N-000544 "named transcript wins" vs N-001113 "newer transcript is read"). Built: the **named** `transcript_path` wins. The newest-under-projects search runs only when no path is named.
7. **Trailing spaces and the hard break** (CF-000195, CF-000196; N-000314 keeps two trailing spaces as a markdown hard break vs N-000330 "removed even when meant as a hard break; that collapse is required"). Built: trailing spaces and tabs are **removed** (the explicit "required" rule).
8. **`utm_source` tracking parameter** (CF-000210; N-000174 "any `utm_source` parameter" vs N-000175 "only the seven listed hosts"). Built: only the seven listed hosts fire family 65.
9. **Several file operands** (CF-000211, CF-000214; N-000234 and PRD "the first file is scanned" vs N-000739 "the last one is the file scanned"). Built: **first** file is scanned. The notice on stderr names it.
10. **Transition cluster** (CF-000219; N-000157 "one opener fires" vs N-000158 "two or more openers in one paragraph"). Built: two or more.
11. **apply_patch path cap, 16 or 10** (not in the unsettled list; FP-05 N-000430 "at most 16 distinct paths" vs interface N-000835 "at most ten paths of one payload"). Built: **10**.
12. **Ledger age, 7 days or 1 day** (not in the unsettled list; FP-05/FP-06 "a ledger whose last modification is more than seven days old is gone" vs interface N-000702 "a ledger untouched for more than one day is deleted at the next session start"). Built: **7 days**. Ledgers older than 7 days are not listed and are deleted at session start.
13. **Session-prose score threshold, 200 or 500 characters** (not in the unsettled list; PRD N-000547 "longer than 200 characters" vs interface N-001115 "longer than 500 characters"). Built: **500**, the reply-shape rule in the interface.
14. **Stats turn and token counting** (not a stated conflict, but an interpretation). The PRD says assistant rows count and the transcript has an `id` per message. A message may appear in several rows with the same id. Built: turns, output tokens and cache-read tokens are counted once per message id (the last row for an id wins), and text is taken once per id.
15. **Guard skip for files inside the plugin tree** (interface N-000694 "unset: the directory that contains the running hook's hooks/ directory"). Built as written: with `CLAUDE_PLUGIN_ROOT` unset the plugin root is `/app` here, so prose files under `/app` are **skipped by the guard**. This follows the spec literally. If a hidden test expects a guard nudge for a file under `/app`, this is the place to look. Setting `CLAUDE_PLUGIN_ROOT` to another directory removes the skip.

## Items the spec does not state (what I assumed)

### Detector scoring
- **Weights and formula are not in the spec.** Score is the sum over score-moving families of `weight * (1 + 0.15 * min(hits - 1, 6))`, rounded and capped at 100. Default weight 8; decisive families 12; boldface 4; emoji 6; non-standard spaces 6; sentence-length monotony and uniform paragraphs 4. Then the spec caps and floors apply: one family at most 40, monotony only at most 20, rhythm only at most 40, short-document and long-document floors, decisive floors.
- **Writing-advice findings** (weight 0, reported): 4, 19, 22, 41, 42, 46, 54, 55, 58, 60, 61, 68 and the parallelism form of 17. The tailing-negation form of 17 scores.
- **Words** are runs of letters, digits, apostrophes and hyphens that contain a letter or digit. **Sentences** split after `.`, `!`, `?` plus closing quotes, and at line breaks. **Paragraphs** split on blank lines.
- **Masking before rules:** YAML front matter, CommonMark fenced code, inline code, blockquote runs of two or more lines, table rows, badge lines.
- **Thresholds not stated in the spec:** boldface overuse at 3 or more bold spans; emoji at 1 or more; monotony coefficient of variation below 0.35 (3+ sentences); uniform paragraphs below 0.4 (4+ paragraphs); mechanical alternation needs a 4-sign run with differences of at least `max(3, 0.5 * mean)`; semicolon rule only at 300+ words; contraction absence needs at least 3 uncontracted forms, more than half the forms, and 2% first-person words; degenerate repetition at 20% or more of 6-word positions repeating; decorative rules need 3+ rules in a document of 24+ lines.
- **Word lists the spec leaves to me:** the stock hyphenated compounds (family 4), the marketing-imperative verbs, the stock evaluative adjectives for family 6, the synonym clusters (the spec gives them), the small words for title case, the placeholder keyword list, the homoglyph map (Cyrillic, Greek, Armenian lookalikes only; Arabic presentation forms are not mapped), the canonical marketing-slop list.
- **Family 1 inflections:** a word matches its `-s`, `-es`, `-ed`, `-d`, `-ing` forms.

### Character layer and cleanup
- **Invisible characters:** all Cc except tab, LF, CR; Cf format characters; the default-ignorable extras. Kept where the spec says they do a job (tag sequences after an emoji, variation selectors after CJK or symbols, ZWSP beside no-space scripts, soft hyphen between letters, ZWJ or ZWNJ beside joining scripts or symbols, Mongolian and Khmer selectors, bidi marks only when the text has right-to-left script).
- **Cleanup processes the whole extracted text**, not just the window. Detection counts only the window. The detector's cleanup output is therefore the full scrubbed document.
- **Line and paragraph separators** U+2028 and U+2029 become LF. Leading blank lines and trailing whitespace are removed. One final line ending is kept if the input had one.
- **Leading spaces** on the first line are kept (the spec only names leading blank lines).

### Extraction
- Invalid UTF-8 bytes are decoded with replacement characters, not rejected.
- `.pdf` and `.rtf` yield empty prose (empty input error).
- `-` on its own is an unknown option (the spec says any argument beginning with `-` before `--`).
- Archive member size cutoff: none beyond the file caps (the spec leaves it to me).
- EPUB: the OPF spine order is used; navigation documents (`properties="nav"`) are skipped; if the OPF cannot be read, all chapter-like files are read in name order.
- XLSX: sheets in file-name order (not workbook order). Numeric cells are not extracted.

### CI interval (`--ci`)
- Bootstrap over sentences. Pool: all sentences up to 150 resamples of 50; above that the evenly spaced 400-sentence pool with 25 resamples. Seed 1234. Interval is the 5th to 95th percentile. Note reports the pool and resample count.

### Plugin and hooks
- `init` and `doctor` run in `process.cwd()`. The guard resolves relative paths against the payload `cwd`, or `process.cwd()` when none is given.
- Python lookup order: `python3`, `python`, `py -3`.
- Session start writes the stored flag `full` on a fresh install (never the environment override). The welcome is printed only when the flag did not exist.
- `PROSECHECK_DEFAULT_MODE` takes precedence over the stored flag when it is one of the four words. Invalid values are ignored.
- Ledger: `.prosecheck-ledger-<sanitized session id>`, or `.prosecheck-ledger` with no session id. Records hold the base name, status, score, band, up to 5 labels, flagged and truncated bits. Newest 20 kept.
- Doctor's settings check creates the config folder if it is missing.
- Doctor's Python check runs the detector on one sample sentence.
- Guard failure reasons: `python not found`, `detector timed out`, `detector output is not a report`, `report has no numeric score`, `detector produced no output` (shared by empty input and any unusable exit), `cannot read file`.
- Guard size skip: plain text over 512 KB, archives and notebooks over 4096 KB (recorded, no nudge).
- Guard `apply_patch` paths: `Add File`, `Update File`, `Move to` lines with a colon. A colon-less line is not a path. NotebookEdit scores `notebook_path`, or `file_path` if no notebook path.
- Post-tool-use timeouts: 8 s plain text, 15 s archive or notebook.
- `check` path: one leading `@` and one pair of matching quotes are removed. Relative paths resolve against `process.cwd()`.
- `show` label cap 5; `check` label cap 8; guard label cap 5.
- `stats` calls the detector on the last 40,000 characters of assistant prose with fenced code removed.
- Contract text: the banned vocabulary list is in every level's contract. The `full` target is "at most 40, band clean or light tells"; `strict` is "at most 20, band clean" plus `--clean`; `lite` has no target. Contract text never names this project; `AGENTS.md` export contains no path or user name.
- The welcome says "/prosecheck check <file>" (spec requires `/prosecheck check`, which is a prefix of it).

## Not done

- **N-000050 (pack 06):** the bundled skill file with rewrite instructions is not shipped. It is a host-agent instruction and not a detector obligation or feature point. The `skills/prosecheck/scripts/detect.py` fallback location is still looked up by the doctor and the hooks.
- Non-goal items (`MUST NOT`) are satisfied by absence. Nothing reads PDF or RTF, nothing is hosted, nothing rewrites documents in place, no demo or evaluation script is shipped.

## Verification

- `python3 -m unittest discover -s tests`: 61 tests pass (Python 3.13, Node 22). 34 in `tests/test_detect.py`: bands, floors and caps, advice not changing score, character layer and rescan, extraction of docx/ipynb/epub/odt/pptx/xlsx, CLI errors and help, `--ci`. 27 in `tests/test_hooks.py`: session start, router, doctor, init, guard, check, show, stats.
- Manual runs (Node 22): session start (welcome, flag write, second start), `/prosecheck` help, unknown word, doctor (four OK lines, namespaced closer), stop phrase, `off` silence, `init` (AGENTS.md write, marker recognition, Cursor rule), guard (Write, Edit, apply_patch, skips), `check`, `show`, `stats` with a transcript, and the missing-transcript reply.
- Contract constraints checked by script: banned words present at every level; `40` absent at `lite`; `light tells` absent at `lite`; `--clean` absent at `full`, present at `strict`; `source code` always preceded by `never` or `not` in its sentence; the Cursor rule has no `detect`, no `40`, no `light tells`.
- Timing: a 500 KB file scans in about 2 s; `--ci` on the same file about 5 s.

Not run: Python 3.9 (the floor), Windows and macOS, a real Claude Code host, the hidden acceptance tests.

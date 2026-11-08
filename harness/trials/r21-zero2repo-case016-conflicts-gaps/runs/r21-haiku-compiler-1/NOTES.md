# NOTES

Build notes for the prosecheck project in `/app`. The specification is `spec/` (unchanged). Start with `spec/MAP.md`. The export was made with `--allow-open` and has 16 unsettled contradictions; each one is listed below with what was built.

## Layout

| Path | What it is | Spec packs |
|---|---|---|
| `scripts/detect.py` | Standard-library detector: extraction, character layer, cleanup, 71-pattern scan, score, JSON report | 10, 11, 12, 21 |
| `hooks/prosecheck-activate.js` | Session-start hook: welcome (first run) and writing contract | 13, 22 |
| `hooks/prosecheck-tracker.js` | Prompt-submit hook and `/prosecheck` router (help, levels, status, show, check, doctor, stats, init) | 13, 15, 17, 18, 31-38 |
| `hooks/prosecheck-subagent.js` | Subagent-start hook: same contract in the JSON envelope | 13, 23 |
| `hooks/prosecheck-guard.js` | Post-tool-use saved-file guard and its reply | 14, 24-30 |
| `hooks/prosecheck-stats.js` | Stats: transcript token totals and session-prose score | 15, 39, 40 |
| `hooks/prosecheck-common.js` | Shared: paths, level flag, ledger, detector runner, contract texts | 16-22, 25-28 |
| `hooks/hooks.json` | Host hook registration (my addition, see Assumptions) | — |
| `commands/prosecheck.md` | Slash-command menu document; body is `/prosecheck $ARGUMENTS` | 15, 31 |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule that `init` copies (prose globs only) | 15, 38 |
| `.claude-plugin/plugin.json` | Plugin manifest (my addition) | — |
| `tests/test_detect.py`, `tests/hooks.test.js` | Tests (see How to verify) | — |
| `README.md` | Product description and not-authorship statement | 04, 16 |

Plugin root is `CLAUDE_PLUGIN_ROOT`, or the parent of `hooks/`. `CLAUDE_CONFIG_DIR` defaults to `~/.claude`. `PROSECHECK_DEFAULT_MODE` overrides the stored level when it is one of the four words.

## Conflicts in the specification and what was built

The export's own unsettled ids are marked **(unsettled)**. The others are contradictions I found while reading the packs.

1. **Usage message stream (unsettled, CF-000081, CF-000082, CF-000083).** FP-01 claim N-000098 (pack 10): "The usage message goes to the error stream." Claim N-000232 (pack 10), and the Interface Contract N-000640 (pack 36/21) and N-000740 (pack 21): `--help` / `-h` print the usage message to standard output and exit 0. **Built:** standard output, exit 0. The usage message's first line is exactly `usage: detect.py [--clean] [--ci] [--] [FILE]`.

2. **Decisive-finding floor at low confidence (unsettled, CF-000086, CF-000114).** N-000134 (pack 10): a decisive finding "always lifts the score to at least 45, whatever the confidence." N-000136 and N-000137: a single decisive family reaches 45 only above `low` confidence. **Built:** 45 floor only at `moderate` or `high`. Two distinct decisive families give a 65 floor at any confidence.

3. **`utm_source` (unsettled, CF-000210).** N-000174 (pack 10): "Any `utm_source` parameter left in a link is an AI tracking parameter." N-000175 (pack 10): only values from a seven-host list. **Built:** the seven-host list.

4. **Several file operands (unsettled, CF-000211, CF-000214).** N-000234 (pack 10), and the "Several file operands" section of pack 21: the first file is scanned. Pack 21 "Signature" (N-000739): "the last one is the file scanned." **Built:** the first file, with a notice on standard error that names it.

5. **Transition clusters (unsettled, CF-000219).** N-000157 (pack 10, family 36 text): one sentence opening with a transition word "already fires transition clusters." N-000158: clusters need two or more openers in one paragraph. **Built:** two or more per paragraph.

6. **No-break spaces (unsettled, CF-000080).** N-000037 (pack 05): "Every no-break space becomes an ordinary space." N-000307 (pack 12): no-break spaces holding digits or punctuation are kept. **Built:** the kept cases in N-000307 are kept (a no-break space with a digit on either side, before `: ; ! ? » › % €`, or after `« ‹`).

7. **Two trailing spaces as a hard break (unsettled, CF-000195, CF-000196).** N-000314 (pack 12) keeps them; N-000330 (pack 12) removes them even when meant as a hard break. **Built:** removed, because FP-03 says "That collapse is required, not optional."

8. **Stop phrase inside a longer prompt (unsettled, CF-000168).** FP-04 N-000383 (pack 13): "a prompt that contains `stop prosecheck` anywhere switches the tool off." FP-06 N-000475 (pack 15) and the Interface Contract (pack 31/32): only when the whole prompt is the phrase. **Built:** whole prompt only (case-insensitive, surrounding whitespace ignored).

9. **Ledger retention (unsettled, CF-000011).** FP-05 N-000436 (pack 14): "At most the newest 20 records." Pack 20 N-000729 ("Global observables an implementer must reproduce"): "keeps its newest 50 records." **Built:** 20 (the feature-point rule). Change `LEDGER_MAX` in `hooks/prosecheck-common.js` to switch.

10. **Ledger lifetime (not in the unsettled list).** FP-06 and non-functional constraints (packs 07, 15): a ledger seven days old or younger "is kept." Pack 19 "Config filenames": a ledger untouched for more than one day "is deleted at the next session start." **Built:** session start deletes ledgers untouched for more than one day; `show` lists remaining ledgers modified within seven days. In practice the one-day rule governs, so the seven-day "kept" promise is not met for ledgers aged between one and seven days. Choose one rule and I will change the code to match.

11. **Named transcript versus newer transcript (unsettled, CF-000179, CF-000221).** FP-06 N-000544 (pack 15): a named transcript "wins over a newer one." Interface `stats` N-001113 (pack 40): "the newer transcript is read." **Built:** the named transcript wins; the newest transcript under `projects/` is used only when none is named.

12. **Session-prose score threshold.** FP-06 (pack 15): the score prints when the slice is "longer than 200 characters." Interface `stats` reply (pack 39): `session prose ai_tell_score` appears only when the slice is longer than 500 characters. **Built:** 500 (the reply format is the observable a caller reads).

13. **Paths scored per apply_patch payload.** FP-05 (pack 14): at most 16 distinct paths. Interface post-tool-use reply (pack 24): at most ten. **Built:** ten.

14. **Post-tool-use and check label caps.** No conflict; the caps are stated per surface: guard 5 labels (FP-05), `show` 5 labels (FP-06), `check` 8 labels (interface, pack 35).

15. **Interface `help` text versus the PRD on `status`.** No conflict found; `status` reports the effective level, including an environment override (Interface, pack 33).

## Not stated in the specification: what was assumed

**Scoring (FP-01 gives bands, floors, and caps, but no base formula).**
- Base points: each score-moving family contributes `6 + 2*min(hits-1, 4)` (6 to 14), summed and capped at 100. Caps and floors from the spec are applied after the sum: single-family cap 40 (skipped when the decisive 45 floor applies), rhythm-only cap 40, sentence-length-monotony-only cap 20, then floors.
- Words are runs of letters, digits, apostrophes, and hyphens (`[^\W_]+(?:['’-][^\W_]+)*`), counted on the masked prose. Sentences split on `.`, `!`, `?` followed by space or line end, and on blank lines.
- Advice families (weight zero): 4, 19, 22, 41, 42, 46, 54, 55, 58, 60, 61, 68, and catalogue 17's parallelism form.
- Family 2 (model-dialect) needs at least two hits (FP-04 says so for the dialect words).

**Pattern lists (PRD says some lists are the implementer's choice).**
- Family 4 (hyphenated stock compounds), family 69 (canonical marketing collocations), family 8 (synonym clusters, as given), family 6 (adjective chains): the lists are my choice where the PRD leaves them open. Family 6 uses no part-of-speech tagging: it requires four comma- or "and"-joined words with at least two adjectival items (stock list or adjective suffix).
- Family 11 (notability) uses capitalised words as a proxy for named outlets. Family 13 allows a title of up to nine words. Family 25 needs a question starting with an auxiliary and a one-word answer sentence.
- Families 1 to 71 use the wording in the PRD; inflection handling is approximate (`-s`, `-es`, `-ed`, `-ing`, and `-e` dropping).

**Character layer and cleanup.**
- Homoglyph table: the Cyrillic, Greek, and Armenian lookalikes for the letters listed in FP-01, plus the Cyrillic and Greek capitals. The Arabic-presentation lookalikes are **not** included, so that part of the homoglyph rule is partial.
- Invisible-character rules: candidates are control characters (other than tab, LF, CR), category Cf, the default-ignorable set (variation selectors, Hangul fillers, Khmer vowels, Mongolian selectors, tag characters). Keep rules implement each exception in FP-03. Tag-character walk-back stops after 16 steps.
- Cleanup runs to a fixed point (at most 8 passes), so that a rescan finds no invisible characters, non-standard spaces, or mixed-script runs. I checked this with 1,500 random strings; the unit test checks 300.
- `--clean` applies to the whole extracted text, not only the 262,144-character window.
- CRLF: CR characters are kept; the restored final line ending matches the input.
- Trailing-whitespace hits: one per line with trailing space or tab, plus one for leading whitespace and one for two or more final newlines.

**Interval (`--ci`).** Bootstrap over sentences: 30 resamples (8 above 20,000 characters for speed), seed 0, 5th and 95th percentiles, rounded to integers. The point score is unchanged.

**Extraction.**
- DOCX: `word/document.xml` only; every `w:p` in document order, including table cells.
- PPTX: slides in numeric order; each `a:p` is a line.
- XLSX: sheets in workbook order; shared strings, inline strings, and string-typed cells are read; numeric cells are skipped; one cell per line.
- ODT/ODP/ODS: `content.xml`; each `text:p` and `text:h` is a line; `text:s`, `text:tab`, and `text:line-break` become space, tab, and newline.
- EPUB: `.xhtml`, `.html`, `.htm` in name order; names containing `nav` or `toc` are skipped; `nav`, `style`, `script`, and `head` content is excluded.
- Notebook: markdown cells only; a non-list `cells` or a non-object cell makes the notebook empty.
- Archive member size cutoff: 32 MB uncompressed per member (my choice; the spec leaves it open).
- Unreadable-file reason text: "cannot read the file (not found or unreadable)." Empty results and "no output" share the reason "detector produced no usable result," as the spec requires.

**Hooks and router.**
- Plugin root: `CLAUDE_PLUGIN_ROOT`, else the parent of `hooks/`. Detector: `scripts/detect.py`, else `skills/prosecheck/scripts/detect.py`. The fallback is supported in code but no skill is shipped (see Not done).
- Python lookup order: `python3`, `python`, `py`. A found interpreter that fails is not retried with another name.
- Session-start writes the effective level to the flag file when no flag exists yet, which is how the welcome is shown only once.
- `status` reports the effective level; `on` stores `full`; `PROSECHECK_DEFAULT_MODE` overrides the stored level.
- `init` and `check` resolve relative paths against the payload's `cwd` when given, otherwise the process working directory.
- `check` strips one `@` and one pair of quotes, in that order.
- The detector treats a lone `-` argument as an unknown option (the spec says any argument beginning with `-` before `--` is unknown), so `-` cannot mean standard input.
- Ledger file names: `.prosecheck-ledger` or `.prosecheck-ledger-<session>`, where the session id keeps only letters, digits, and underscores, up to 64 characters.
- Doctor's Python check runs the detector on a fixed sample sentence.
- Stats: assistant rows are de-duplicated by message `id`; the last usage seen for an id is used. The prose slice removes fenced code and keeps the last 40,000 characters. The detector is run on that slice through standard input.
- Guard: `lite` and `off` record nothing (they do not score). Other extensions produce no record. A file that is not found is recorded as failed, but only when its extension is eligible. A directory is ignored.
- Init export: the portable section has the contract, the scoring line for `full` and `strict`, and the `CLAUDE_PLUGIN_ROOT` / `skills` / `plugins` line. It names no install path and no user name.
- Cursor rule globs are a quoted, comma-separated list (the file uses `alwaysApply: false`).

**Host layout (not defined by the spec).** `hooks/hooks.json` and `.claude-plugin/plugin.json` follow the Claude Code plugin layout as I understand it. They are not required by the detector or by the hook contract.

## Not done (with reasons)

- **Bundled skill file** (rewrite instructions, PRD N-000050, N-000051, N-000092): the PRD says it is a host-agent instruction, not a feature point. Not shipped. The `skills/prosecheck/scripts/detect.py` fallback is implemented but nothing ships there.
- **Recorded-session demo, documentation checker, bundled evaluation script, status-line helper** (N-000093, Interface "not in this surface"): non-goals. Not shipped.
- **Reading PDF or RTF** (N-000086): non-goal. They report "no readable text" (detector) or "not re-scored" (guard).
- **Scoring shell-written files** (N-000087, N-000088): non-goal; the guard is not fired for shell writes.
- **Website, account, hosted service, telemetry** (N-000089, N-000064/65): not built.
- **Consulting third-party detectors** (N-000090): not done.
- **Rewriting a document in place with `--clean`** (N-000091): not done; cleanup prints text only.
- **Installable package or compiled extension**: forbidden by the spec; not built.
- **Arabic-presentation lookalike table** (N-000177): partial (see Assumptions).

## Checklist coverage

`spec/CHECKLIST.md` lists 1126 ids. I did not edit `spec/`, so the checklist itself is unchanged. Coverage is recorded here:

- **Implemented and exercised by tests:** the detector surface (packs 10, 11, 12, 21), the router and reply shapes (packs 15, 31-38), the hooks (packs 13, 22-24), the guard (pack 14), stats (pack 39, 40), and the contract export (pack 38).
- **Implemented, checked by hand only:** the per-family pattern rules in pack 10 (covered by the 26 detector tests only where a test names the behaviour), the Interface Contract shape details in packs 17-20, and the non-functional constraints in packs 04-09 (checked by grep: no network modules, no runtime dependencies).
- **Traceability markers:** `# spec: <id>` comments sit beside the detector functions that implement the ids I could map (69 markers). The hooks carry a pack-level pointer rather than per-id markers.
- **Not done:** see the list above.

## How to verify

    cd /app
    python3 -m unittest discover -s tests -t tests     # detector and cleanup tests
    node --test tests/hooks.test.js                    # hook and router tests
    printf 'It is important to note that we delve into the tapestry.' | python3 scripts/detect.py
    python3 scripts/detect.py --help

The hook tests use temporary config and project directories and never touch `~/.claude`.

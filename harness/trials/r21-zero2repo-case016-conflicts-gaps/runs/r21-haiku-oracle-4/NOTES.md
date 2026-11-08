# NOTES

Build of the prosecheck product (spec: `spec/`, version 0.9.3) in `/app`.
No build step: the detector is a Python script and the hooks are Node scripts.

## Layout

| Path | What it is |
|---|---|
| `scripts/detect.py` | Detector CLI (Python standard library). Extraction, cleanup, catalogue scan, score, report. |
| `skills/prosecheck/scripts/detect.py` | Byte-identical copy of the detector. The spec's fallback location; re-copy it if `scripts/detect.py` changes. |
| `skills/prosecheck/SKILL.md` | Bundled rewrite guidance for the host agent. |
| `hooks/prosecheck-activate.js` | Session start: welcome (first start only) and the writing contract. |
| `hooks/prosecheck-tracker.js` | Prompt submit: `/prosecheck` router, stop phrases, ordinary-prompt reminder. |
| `hooks/prosecheck-subagent.js` | Subagent start: contract in the subagent JSON envelope. |
| `hooks/prosecheck-guard.js` | Post-tool use: saved-file guard and session ledger. |
| `hooks/prosecheck-stats.js` | Stats (token figures, session prose score), used by the router. |
| `hooks/lib/prosecheck-core.js` | Shared code: levels, detector runs, contract text, ledger. |
| `hooks/hooks.json`, `.claude-plugin/plugin.json` | Host registration (Claude Code plugin layout). |
| `commands/prosecheck.md` | The `/` menu document; its body forwards `$ARGUMENTS` to the router. |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule, copied by `init`. |
| `tests/test_prosecheck.py` | Unit and integration tests (`python3 -m unittest discover -s tests`). |
| `tests/check_contract.js` | Assertions on the contract and export text (`node tests/check_contract.js`). |
| `TRACEABILITY.md` | One row per checklist id: status and the code location annotated with `# spec:`. |

## Verification done

- `python3 -m unittest discover -s tests`: 22 tests pass (Python 3.13, Linux).
- `node tests/check_contract.js`: contract and export assertions pass.
- Detector timing on Linux: about 0.6 s for a 512 KB plain-text file, about 0.7 s for 200k zero-width characters plus spaces, well inside the 8 s budget.
- End-to-end runs of each hook with JSON on stdin, in a scratch `CLAUDE_CONFIG_DIR`: session start (welcome once), every router subcommand, stop phrases, guard (Write, Edit-style path, apply_patch, NotebookEdit, skipped and failed files), `show`, `check`, `doctor` (healthy, no Python on PATH, mode off), `init` (fresh, repeated, off, lite), `stats` (with a transcript and missing), subagent envelope.
- Archives: docx, pptx, xlsx, odt, epub, ipynb extracted and cleaned; a non-zip `.docx` and a `.pdf` give the specified errors.

Not verified:
- Python 3.9 (the stated floor). Only Python 3.13 is installed here. The code uses no 3.10+ syntax, but this was not run.
- Windows and macOS. Only Linux was run.
- Real host integration: the hooks were run as standalone processes with the host's JSON. Loading the plugin in Claude Code, or in another agent, was not tested.
- The score is a heuristic. Its calibration is not checked against any corpus.

## Spec conflicts and the reading built

Each entry gives the two sides with their location (pack, claim id), then what was built. Where the spec's own text names a claim id, the id is given. The 23 items marked CF are the export's unsettled contradictions (`spec/MAP.md`); the rest I found while reading.

1. **Ledger size (CF-000011).** FP-05 (pack 14, N-000436): "At most the newest 20 records are kept." Global observables (pack 20, N-000729): "Each ledger keeps its newest 50 records." Built: **20**, because the interface defers ledger rules to the PRD.
2. **No-break space (CF-000080).** Pack 05 (N-000037): "Every no-break space becomes an ordinary space." FP-03 (pack 12, N-000307): a no-break or narrow no-break space holding digits or punctuation together is kept. Built: **kept** when it has a digit on either side, or precedes `: ; ! ? » › % €`, or follows `« ‹`; every other space separator becomes U+0020.
3. **Usage stream for `--help` (CF-000081, -082, -083).** Pack 10 (N-000098): "The usage message goes to the error stream." Pack 10 (N-000232), pack 18 (N-000640), pack 21 (N-000740): `--help` and `-h` write the usage to standard output and exit 0. Built: **standard output**, exit 0, nothing on standard error.
4. **Decisive 45 floor (CF-000086, CF-000114).** Pack 10 (N-000134): a decisive finding "always lifts the score to at least 45, whatever the confidence." Pack 10 (N-000136, N-000137): a single decisive family reaches 45 only when confidence is above `low`. Built: **the second**. Two distinct decisive families give 65 regardless of confidence.
5. **Stop phrases (CF-000168).** Pack 13 (N-000383): a prompt that contains `stop prosecheck` "anywhere" switches the tool off. Pack 15 (N-000475) and pack 31: the entire prompt, letter case ignored; anything else around it is an ordinary prompt. Built: **entire prompt** (trimmed, case-insensitive).
6. **Trailing whitespace and hard breaks (CF-000195, CF-000196).** Pack 12 (N-000314): two trailing spaces that end a prose line are a hard break and are kept. Pack 12 (N-000330): trailing whitespace "is removed even when two spaces were meant as a markdown hard break. That collapse is required." Built: **removed** (N-000330 is the more specific rule).
7. **`utm_source` (CF-000210, CF-000235).** Pack 10 (N-000174): "Any `utm_source` parameter ... is an AI tracking parameter." Pack 10 (N-000175, N-000176): only when the whole host is one of seven AI sites. Built: **the host list**.
8. **Which file is scanned for several operands (CF-000211, CF-000214).** Pack 10 (N-000234) and pack 20 (N-000719): "the first file is scanned." Pack 21 (N-000739): "the last one is the file scanned." Pack 21 (N-000783 to N-000787) also says the notice names the first operand. Built: **the first file**, with the notice naming it. Two of the three sources agree on this.
9. **Transition clusters (CF-000219).** Pack 10 (N-000157): a single sentence opening with a transition "already fires transition clusters." Pack 10 (N-000158): two or more openers in one paragraph. Built: **two or more** in one paragraph.
10. **Hedge stacking weight (CF-000234).** Pack 10 (N-000119): hedge stacking (54) is writing advice with weight zero. Pack 10 (N-000170): "Each sentence with stacked hedges adds to the score." Built: **weight zero**, as the FP-01 list says.
11. **Catalogue 17 (CF-000240).** Pack 10 (N-000126): the tailing-negation form is score-moving. Pack 21 (N-000750): both forms are writing advice with weight zero. The FP-01 writing-advice list (12 numbers) does not include 17, and 50 score-moving numbers only add up if 17 is one of them. Built: **tailing negation is score-moving; the parallelism form is weight-zero advice** (reported under `17_negative_parallelism`).
12. **Named transcript vs newest (CF-000179, CF-000221).** Pack 15 (N-000544): "a named transcript wins over a newer one." Pack 39 (N-001113): "the newer transcript is read." Built: **the host-named `transcript_path` wins**; the newest `.jsonl` under `projects` is used only when none is named.
13. **Ledger deletion age (CF-000237).** Pack 07 (N-000069): a ledger more than seven days old "is gone." Pack 20 (N-000702): "untouched for more than one day is deleted." Built: **seven days**, for both deletion at session start and the `show` listing.
14. **Environment default (CF-000238).** Pack 13 (N-000390, N-000391): with nothing valid stored, the level is `full` unless the environment supplies a word. Pack 19 and 20 (N-000701): `PROSECHECK_DEFAULT_MODE` "takes precedence over the stored level." Built: **the environment word is only the fallback** when no valid stored word exists (the name says "default").
15. **Apply-patch path cap (CF-000236).** Pack 14 (N-000429): at most **16** distinct paths. Pack 22 (N-000834): "At most ten paths of one payload are scored." Built: **16**.
16. **Stats prose-score threshold (not in CF list).** Pack 15 (FP-06, stats bullet): the session-prose score is printed only when the slice is "longer than 200 characters." Pack 39 (reply rule, N-001115 to N-001119): "longer than 500 characters." Built: **200** (the PRD's behavior rule).

## Unstated in the spec: assumptions made

Scoring
- The spec gives the caps, floors, bands, and confidence rules but no base formula. Built: each score-moving family contributes 10 points, plus 2 per extra hit (up to 3 extra hits); decisive families contribute 16 plus the same extra. The sum is capped at 100, then the caps (single family, rhythm-only) and floors (decisive, word-count) apply.
- Family 2 (model-dialect vocabulary) fires only when it has at least two hits in total. The spec gives "two hits" for the dialect words; I applied it to the whole family.
- Family 56 (boldface overuse) fires at three or more bold spans. The spec says "bold spans in prose" with no threshold.
- Family 66 (homoglyphs): a fixed confusable map (Cyrillic, Greek, and Armenian letters that look like Latin a, c, d, e, h, i, j, n, o, p, s, u, v, x, y, B, C, E, H, I, J, K, M, N, O, P, S, T, X, Y, Z). The spec does not list the map.
- Family 4 (stock hyphenated compounds), family 69 (canonical marketing phrases), and the stock evaluative adjectives for family 6 are implementer's choice; the lists used are in `scripts/detect.py`.
- Family 3: the spec's word list includes the bare word "leading"; I did not match it because the spec gives no context for it. This is the one partial item (N-000154, see TRACEABILITY.md).
- Emoji (family 57): code points U+1F000 to U+1FAFF, U+2600 to U+27BF, and characters in Unicode category So.
- Sentences split on `. ! ?` and line breaks; paragraphs are separated by blank lines. Word tokens: runs of letters, digits, apostrophes, and hyphens.
- Exclusions (code fences, inline code, quote runs, table rows, badge lines, YAML front matter) are applied by blanking those characters to spaces (newlines kept), so positions match the original text.
- Question-answer (25), sentence rhythm (40, 41, 44), and opener repetition (42) use the closest reading of the spec's wording.
- Confidence reason strings and the `score_ci_note` text are free wording.
- `--ci`: 200 bootstrap draws over sentences, seed 20260506, interval at the 2.5th and 97.5th percentiles. Needs at least four sentences; otherwise `score_ci` is `null` with a note.
- Samples: the matched text, newlines replaced by spaces, cut to 90 characters.
- Report key for each finding: `<number>_<slug of the label>`; the label is the catalogue title.

Input and extraction
- Invalid UTF-8 bytes in plain text are replaced (not an error).
- Cleanup works on the whole extracted text, not only the window. The window limits findings, as the spec says.
- Cleanup output normalizes CRLF to LF, removes leading blank lines, strips trailing spaces and tabs on every line, and restores one final newline if the input had one.
- Zip-based files: `.docx` reads `word/document.xml`; `.pptx` reads `ppt/slides/slide<N>.xml` in numeric order (notes are not read); `.xlsx` reads sheets in file-number order, with shared strings, inline strings, and string-typed cells; `.odt`, `.odp`, `.ods` read `content.xml`; `.epub` reads XHTML files in name order, skipping nav and toc files.
- Archive limit: the spec leaves the member size cutoff to the implementer. Built: total uncompressed size of an archive must be at most 256 MB, else "cannot read input".
- A file with a source-code extension given to the detector is read as plain text. The guard never scores it.
- An unknown extension given to `/prosecheck check` is read as plain text (512 KB cap).

Plugin and hooks
- The spec does not give the host manifest format. `.claude-plugin/plugin.json` and `hooks/hooks.json` follow the Claude Code plugin layout. `${CLAUDE_PLUGIN_ROOT}` is used in the hook commands.
- Plugin root: `CLAUDE_PLUGIN_ROOT` if set, otherwise the parent of `hooks/` (here, `/app`).
- The first session start writes the effective level to `.prosecheck-active` (only when that level is not `off`). The welcome is shown on that first start only.
- Ledger files: `.prosecheck-ledger-<session id with only letters, digits, underscores>`; `.prosecheck-ledger` when there is no session id. Each record has base name, status, score, band, phrase, up to five labels, flagged and truncated flags, and a timestamp.
- Settings writability (doctor): a probe file is created and removed in the config folder.
- Doctor's Python check runs the detector on a short sentence from standard input.
- Guard: skip rules use path segments (`node_modules`, `.git`) and the plugin root; instruction names and stems are as the spec lists. Relative paths resolve against the payload `cwd`, else the hook's working directory.
- Guard: when `file_path` is missing for a `NotebookEdit`, `notebook_path` is used. The `content` field is ignored.
- `stats`: assistant messages are counted by message `id` (streamed duplicates count once); token totals use the last usage record per id. The prose slice is the last 40,000 characters after removing fenced code.
- `init`: the export is appended to `AGENTS.md` between `<!-- prosecheck:writing-contract begin/end -->` markers; the second run is recognized by the begin marker. The Cursor rule's globs are one comma-separated line.
- Writing contract, welcome text, help text, reply wording, and the Cursor rule body are written for this build. The spec fixes their required parts (listed in pack 13, 22, 31 to 38), and `tests/check_contract.js` checks those parts.
- Live contract names `scripts/detect.py` relative to the plugin root, plus `CLAUDE_PLUGIN_ROOT` in the post-write step at full and strict. It never contains the machine's absolute path.
- `skills/prosecheck/SKILL.md` is named `SKILL.md`; the guard skips it as an instruction file.

## Items not done

- N-000154 (catalogue 3, promotional language): the bare word "leading" is not matched (partial).
- Non-goals and out-of-surface items (website, hosted service, rewriting documents in place, authorship proof, third-party detectors) are not implemented, as the spec says.
- The 9 catalogue numbers with no detector (7, 9, 28, 29, 43, 45, 49, 52, 53) are never reported, as the spec says.

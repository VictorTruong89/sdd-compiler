# prosecheck 0.9.3: build notes

Built from `spec/` (MAP.md, CHECKLIST.md and the 40 packs). `spec/` is unchanged.

## What is here

| Path | Purpose |
| --- | --- |
| `scripts/detect.py` | The detector: extraction (20 formats), character layer, 71-pattern catalogue, score, bands, report, `--clean`, `--ci`. Python 3 standard library only. |
| `hooks/prosecheck-activate.js` | Session-start hook: welcome (first run only) and writing contract. |
| `hooks/prosecheck-tracker.js` | Prompt-submit hook: the `/prosecheck` and `/prosecheck:prosecheck` router, stop phrases, per-prompt reminder. |
| `hooks/prosecheck-subagent.js` | Subagent-start hook: the same contract inside the subagent envelope. |
| `hooks/prosecheck-guard.js` | Post-tool-use hook: scores saved prose files for Write, Edit, MultiEdit, NotebookEdit, apply_patch. |
| `hooks/prosecheck-stats.js` | Stats: transcript turns, tokens, own-prose score. |
| `hooks/lib/common.js` | Config folder, level flag, ledgers, detector runs, Python lookup (`python3`, `python`, `py`). |
| `hooks/lib/contract.js` | Writing contract text per level, welcome text. |
| `hooks/lib/commands.js` | Replies for check, doctor, show, init, help, unknown words. |
| `hooks/hooks.json`, `.claude-plugin/plugin.json`, `commands/prosecheck.md` | Host wiring and the `/` menu document. Not required by the spec; added so the plugin can be loaded. |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule, copied by `init`. |
| `tests/test_detect.py`, `tests/test_plugin.py`, `tests/fixtures_memo.txt` | Unit tests (53 in total). |

Run the tests with `python3 -m unittest discover -s /app/tests -v` (needs `node`). Nothing needs installing or building.

Detector: `python3 scripts/detect.py [--clean] [--ci] [--] [FILE]`.

## Spec disagreements and what was built

Sixteen are listed as UNSETTLED in `MAP.md` and the packs. The other items were found while reading the packs.

| # | Disagreement (where) | Built |
| --- | --- | --- |
| 1 | CF-000011 / ledger size: PRD FP-05 "At most the newest 20 records are kept" (pack 14) vs Interface "Each ledger keeps its newest 50 records" (pack 20). | 20. The PRD is the rule for what a ledger keeps. `LEDGER_KEEP` in `hooks/lib/common.js`. |
| 2 | CF-000080 / no-break space: PRD "Every no-break space becomes an ordinary space" (pack 05) vs "except a no-break space (U+00A0) or narrow no-break space (U+202F) that holds something together" (pack 12). | The exception. A no-break space or U+202F with a digit on either side, or before `:;!?»›%€`, or after `«‹`, is kept. Other no-break spaces become U+0020. |
| 3 | CF-000081, 082, 083 / usage stream: PRD "The usage message goes to the error stream" (pack 10) vs `--help` prints usage to standard output and exits 0 (packs 18, 21). | Standard output, exit 0. Errors go to stderr as JSON. |
| 4 | CF-000086, 114 / decisive 45 floor: "a decisive finding always lifts the score to at least 45, whatever the confidence" vs "a single decisive family raises it to at least 45 only when confidence is above `low`". | The confidence rule. One decisive family gives a 45 floor only at `moderate` or `high`. Two or more distinct decisive families give a 65 floor at any confidence. |
| 5 | CF-000168 / stop phrase: "a prompt that contains `stop prosecheck` anywhere switches the tool off" (pack 13) vs "the same words with anything else before or after them are an ordinary prompt" (pack 15). | Only the entire prompt (case-insensitive) is a stop phrase. Packs 15 and 31 state the entire-prompt rule explicitly. |
| 6 | CF-000179, CF-000221 / stats transcript: "the transcript is the host-named `transcript_path`" vs "when the projects folder holds a newer transcript, the newer one is read". | The named transcript wins whenever `transcript_path` is supplied. The newest `.jsonl` under `projects` is used only when none is named (pack 40 says this). |
| 7 | CF-000195, 196 / trailing spaces: "spaces and tabs at the end of every line" removed (pack 12) vs "two trailing spaces ... are a markdown hard break and are kept". | Removed. Pack 12 says the collapse "is required, not optional". Hard breaks are not preserved. |
| 8 | CF-000210 / UTM tracking: "any `utm_source` parameter ... is an AI tracking parameter" vs "a `utm_source` whose value is exactly one of" seven hosts. | Only the seven hosts count (rule 65 spells them out). |
| 9 | CF-000211, 214 / multiple operands: "the first file is scanned" vs "the last one is the file scanned" (pack 21). | The first file is scanned, with a stderr notice that names it. The first-file rule is the one stated in packs 10, 20 and 21 (N-000719). |
| 10 | CF-000219 / transition clusters: "already fires transition clusters" for one sentence vs "two or more sentence-opening transitions in one paragraph". | Two or more in one paragraph. |
| 11 | Not in the unsettled list: ledger age. Pack 19 N-000702: "a ledger untouched for more than one day is deleted at the next session start". Pack 07 and pack 15: a ledger "more than seven days old" is gone or not listed. | Seven days, for both listing and deletion. The PRD privacy rule governs. |
| 12 | Not in the unsettled list: `PROSECHECK_DEFAULT_MODE`. Pack 19 N-000701: "when it is set, it takes precedence over the stored level". Pack 13 N-000390-391: the variable matters only when nothing valid is stored. | Precedence. A valid environment word wins over the stored flag. Invalid environment values are ignored. |
| 13 | Not in the unsettled list: apply_patch paths. PRD FP-05: "at most 16 distinct paths". Pack 24: "at most ten paths of one payload are scored". | Ten. Pack 24 is the more specific rule for the post-tool-use reply. |
| 14 | Not in the unsettled list: session-prose score threshold. PRD FP-06: printed only when the slice is "longer than 200 characters". Pack 39: "longer than 500 characters". | 200 (PRD). |
| 15 | Not in the unsettled list: `/prosecheck check` lists. Pack 35 says "at most the check label cap the PRD gives", which is eight in FP-06. The guard lists up to five. | Check shows up to eight. Guard and show use five. |
| 16 | Not in the unsettled list: the cleanup switch and the `help` "contract" wording do not conflict, but the PRD calls the cleanup switch "cleanup" and the interface calls it `--clean`. | `--clean`, the spelling in the interface contract. |

## Assumptions and things the spec does not state

- **Score arithmetic.** The spec fixes families, floors, caps and bands but not the weights. The build gives each distinct score-moving family 10 points (15 for decisive families), plus 2 per extra hit up to 3 extra hits, capped at 100. Floors and caps then apply as stated in FP-01.
- **Decisive families.** The decisive set is 13, 47, 48, 50, 62, 63, 64, 65 and 66.
- **Writing advice.** The 12 advice numbers and the parallelism form of 17 score zero. They are still reported.
- **Model-dialect family.** FP-04 says the dialect words "need two hits". The build applies that to the whole family 2.
- **Bold overuse (56).** The spec gives no threshold. The build fires at two or more bold spans.
- **Degenerate repetition (71).** "On the order of a fifth or more" is built as at least 20% of six-word runs occurring more than once.
- **Headings and rhythm.** Sentences are split on `.!?` followed by whitespace, and on line breaks. Paragraphs are split on blank lines. Monotony uses a coefficient of variation below 0.35 (sentences) and 0.4 (paragraphs).
- **Scan-text exclusions.** Front matter, fenced code, inline code, blockquote runs of two or more lines, table rows and badge lines are removed before the text-based families run. The character-layer findings (62, 66, 67, 68) are computed on the window as the spec says.
- **Cleanup scope.** `--clean` scrubs the whole extracted text, not only the window. The spec says findings are measured on the window and does not say what cleanup covers.
- **Resampled interval (`--ci`).** The spec leaves the method to the implementer. The build splits the sentences into four contiguous blocks, scores each, and reports the lowest and highest score, including the point score. It needs at least four sentences.
- **Size caps.** The detector command does not refuse oversize files, because the spec puts the caps on the plugin and on `check`. The guard and `check` enforce 512 KB for plain text and 4 MB (4096 KB) for archives and notebooks.
- **Archive members.** The member size cutoff is unspecified, so none is applied. A hostile archive could still be large in memory.
- **Extraction details.** XLSX sheets are read in numeric file order. EPUB chapters are read in archive order, excluding names containing `nav`. ODF text comes from `content.xml`. Notebook markdown cells are joined with line breaks.
- **Stats.** Assistant messages are counted once per message `id`. Output and cache-read tokens are summed over those messages. A transcript is searched under `projects` up to six levels deep.
- **Ledger identity.** Ledger files are named `.prosecheck-ledger-<session>`, with the session id reduced to letters, digits, `_` and `-`. A missing session id uses `.prosecheck-ledger`.
- **Doctor.** The settings check writes and deletes a probe file in the config folder. The Python check runs the detector on a fixed sample sentence.
- **Init.** The section is recognised by the contract heading `## Prose writing contract`. The exported text has no machine path and no user name, and it is the same at every level apart from the level-specific lines.
- **Live contract.** It names `scripts/detect.py` relative to the plugin root, with no absolute path, so it is the same as the exported text.
- **Plugin root.** The guard skips files inside the plugin root, as FP-05 requires. With no `CLAUDE_PLUGIN_ROOT`, that root is the directory containing `hooks/`. In this repository that means files under `/app` are never scored by the guard.
- **Welcome.** It is written on the first session start, when no flag file exists. That start also writes the flag.

## Spec items not built, or built only in part

- **No-detector numbers.** 7, 9, 28, 29, 43, 45, 49, 52 and 53 have no detector, per FP-01. They never appear as findings, which is the spec's requirement.
- **Approximate rules.** The catalogue families are regex and heuristic approximations of the PRD wording. Some lists the spec leaves to the implementer are short: the hyphenated-compound list (4), the promotional-language list (3), the canonical marketing phrases (69) and the synonym clusters (8). Family 6 (stacked adjectives), family 11 (notability) and family 27 (intro hooks) are heuristics. Their exact firing conditions may differ from the PRD's.
- **Untested parts.** The PPTX, XLSX, ODT, ODP, ODS and EPUB extractors are implemented but have no automated test. `check`'s over-cap reply and its Python-missing reply are implemented but not tested. Stats and `transcript_path` are checked by hand only.
- **Bundled skill and install command.** The bundled skill file is a host-side document, not a feature point (PRD N-000050). It is not shipped. `install/prosecheck-command.md` is not shipped either. The shipped menu document is `commands/prosecheck.md`, which the spec allows.
- **Platforms.** Tested on Linux with Python 3.13 and Node 22. Python 3.9 compatibility was not run. The code uses only the standard library and no syntax newer than 3.9. Windows and macOS were not run.

## Coverage of the checklist

Every id in `spec/CHECKLIST.md` is accounted for below by pack, with its id range. The code is annotated with `# spec:` (Python) and `// spec:` (JavaScript) comments at module and function level, not per id. Status: **impl** means implemented. **test** means at least one automated test covers the behaviour. A row marked **impl** only has no automated test for that behaviour.

| Pack | Ids | Status | Where / notes |
| --- | --- | --- | --- |
| 01 hardware | none | n/a | No checklist items. Constraints carried by the rows below. |
| 02 hardware summary | N-000588–592 | impl | Standard library only; Node hooks; no build step. |
| 03 execution profiles | N-000593–602 | impl | `python3`/`python`/`py` lookup in `hooks/lib/common.js`. No build. |
| 04 product overview | N-000001–018 | impl, test | Local only, no network code, plugin and detector surfaces. |
| 05 terminology | N-000019–040 | impl, test | Bands, levels, catalogue numbers, `score` rules. Band test in `test_detect.py`. |
| 06 public surface | N-000041–051 | impl | Detector, guard, `/prosecheck`, contract. Skill not shipped (see above). |
| 07 non-functional | N-000052–077 | impl | Stdlib only; no network; ledger age; determinism. No automated determinism test. |
| 08 required substance | N-000078–081 | impl | Every feature point runs on the real detector or hooks. |
| 09 non-goals | N-000082–093 | impl | Excluded behaviour: no PDF or RTF reading, no in-place rewrite, no website. |
| 10 FP-01 detector scan | N-000094–242 | impl, test | Report, findings and metrics, bands, floors and caps, window, errors, `--ci`, `--`, help, multiple operands. Tests: window, errors, CI, fenced code, bands. |
| 11 FP-02 extraction | N-000243–298 | impl, test | Twenty formats, caps, window measured on extracted prose. Tests: DOCX, IPYNB, PDF, bad zip, UTF-16. Others untested (see above). |
| 12 FP-03 cleanup | N-000299–331 | impl, test | AC N-000305 and N-000309 tested by name. Folding, no-break space rule, trailing whitespace. |
| 13 FP-04 contract | N-000332–394 | impl, test | `hooks/lib/contract.js`, activate, subagent, tracker. Tests: per-level contract, banned words, source-code sentences, welcome once, portable export. |
| 14 FP-05 guard | N-000395–456 | impl, test | `hooks/prosecheck-guard.js`. Tests: flagged nudge, lite/off silence, strict 20 vs full 40, skips, apply_patch, ledger and `show`. |
| 15 FP-06 commands | N-000457–577 | impl, test | `hooks/lib/commands.js`, tracker. Tests: help, levels, stop phrases, unknown word, doctor shape, check, init. |
| 16 cross-cutting | N-000578–587 | impl | No network code; no narration; wording uses "reads". |
| 17 interface overview | N-000603–626 | impl | Layout, hooks, `python` lookup, prompt reminder. |
| 18 public surface shape | N-000627–673 | impl | Switches `--clean` and `--ci`, usage line, hook names, exported files. |
| 19 naming and env | N-000674–702 | impl | Band and phrase names, env variables, flag and ledger file names. Ledger age per conflict 11. |
| 20 global observables | N-000703–730 | impl, test | Exit 0, 1 and 2 paths; UTF-8; error objects; hooks exit 0 on malformed input. |
| 21 `detect.py` contract | N-000731–787 | impl, test | Signature, report keys, `17_negative_parallelism` and `17_tailing_negation`, errors, multiple operands. |
| 22 activate hook | N-000788–812 | impl, test | Plain text; welcome and contract by level; off is silent. |
| 23 subagent hook | N-000813–818 | impl, test | JSON envelope; off is silent. |
| 24 post-tool-use reply | N-000819–835 | impl, test | Envelope, `fix` wording, coverage clause, labels capped at five, up to ten paths. |
| 25 `content` | N-000836–840 | impl | Not used as a path; the guard reads `file_path`. |
| 26 `cwd` | N-000841–843 | impl | Relative `file_path` resolved against `cwd`. |
| 27 `file_path` | N-000844–846 | impl | Nested under `tool_input`. |
| 28 `prompt` and `session_id` | N-000847–856 | impl, test | Session-scoped ledger; the command comes from `prompt`. |
| 29 `tool_input` | N-000857–863 | impl | `file_path`, `notebook_path`, and `command` for apply_patch. |
| 30 `tool_name` | N-000864–869 | impl | Supported tool names only. |
| 31 `/prosecheck` | N-000870–908 | impl, test | Both forms; block decision; unknown word; stop phrases; ordinary prompt; menu document with `$ARGUMENTS`. |
| 32 help | N-000909–934 | impl, test | Live level first line; command lines; deep-rewrite phrases. |
| 33 status | N-000935–941 | impl, test | One line naming the stored level. |
| 34 level words | N-000942–951 | impl, test | Store, confirm, `on` stores `full`. |
| 35 check | N-000952–992 | impl, test | Scored reply lines; quote and `@` stripping; not-a-file, cannot-read, PDF, missing Python untested. |
| 36 doctor | N-000993–1028 | impl, test | Title, four check lines, closer by case; off case tested. |
| 37 show | N-001029–1060 | impl, test | Newest first; session isolation; empty ledger; binary and skip rows. |
| 38 init | N-001061–1102 | impl, test | Off writes nothing; already-present case; AGENTS.md appended; Cursor rule copied; cannot-write messages not tested. |
| 39 stats | N-001103–1121 | impl | Turns, tokens, level, own-prose score. Checked by hand only. |
| 40 `transcript_path` | N-001122–1126 | impl | Named transcript used when supplied. Checked by hand only. |

## Verification

- `python3 -m unittest discover -s tests`: 53 tests, all passing. Run with `-W error::ResourceWarning`: clean.
- Manual runs: guard on flagged and unflagged files, `apply_patch`, `show`, `check`, `init` in the off, lite and full modes, `stats`, and the first-run welcome.
- Performance: a 262 KB input with long invisible and space runs runs in under 1 s; pathological table and bold inputs were fixed during testing and now take under 1 s.
- Not verified: Windows, macOS, Python 3.9 and 3.10, and a live host agent.

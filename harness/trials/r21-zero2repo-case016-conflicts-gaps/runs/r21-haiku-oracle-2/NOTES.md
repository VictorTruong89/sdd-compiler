# NOTES

Implementation notes for the prosecheck spec in `spec/`. The spec was not edited.

## What was built

| Path | What it is | Spec |
|---|---|---|
| `scripts/detect.py` | Detector CLI: extraction of 20 formats, mask of code and quotes, 71-pattern catalogue, score, bands, `--clean`, `--ci` | Interface `scripts/detect.py`; FP-01, FP-02, FP-03 |
| `hooks/prosecheck-activate.js` | Session-start hook: welcome once, writing contract for the level | FP-04; interface `hooks/prosecheck-activate.js` |
| `hooks/prosecheck-tracker.js` | Prompt-submit hook and `/prosecheck` router (all twelve subcommands, stop phrases, reminder) | FP-04, FP-06; interface `/prosecheck` |
| `hooks/prosecheck-guard.js` | Post-tool-use saved-file guard (Write, Edit, MultiEdit, NotebookEdit, apply_patch) | FP-05; interface post-tool-use reply |
| `hooks/prosecheck-subagent.js` | Subagent-start hook: contract in the JSON envelope | FP-04; interface subagent |
| `hooks/prosecheck-stats.js` | `stats` reply: transcript totals and own-prose score | FP-06; interface `stats` |
| `hooks/lib/prosecheck-common.js` | Config, level resolution, detector runner, ledger, contract text | interface "Naming conventions", "Global observables" |
| `commands/prosecheck.md` | Slash-command menu document; body `/prosecheck $ARGUMENTS` | interface `/prosecheck` (shipped menu document) |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule (prose globs only, no detector step) | FP-06 `init`; interface `init` |
| `ETHICS.md` | Ethics text: not authorship, triage, not for accusing people | FP-cross-cutting, N-000581..N-000584 |
| `tests/test_spec.py` | unittest suite; AC tests named `test_N_000305_…`, `test_N_000309_…` | FP-03 acceptance criteria |

Run the tests from `/app`: `python3 -m unittest discover -s tests -v`. All 19 pass.

The detector and hooks use only the Python standard library and Node.js built-ins. Nothing is installed and nothing is built.

Plugin root is the directory that holds `hooks/` (that is `/app` here), unless `CLAUDE_PLUGIN_ROOT` is set.

## Spec conflicts and the choice made

The export marks 23 contradictions as unsettled (`spec/MAP.md`). Each is listed with the side chosen. A few further disagreements found while building are covered by the same items.

1. **CF-000011** ledger retention: FP-05 says "at most the newest 20 records" (N-000436); interface says "keeps its newest 50 records" (N-000729). **Chose 20.** A list of at most 20 meets the PRD's "at most" wording; the interface's "50" is not kept.
2. **CF-000080** no-break spaces: N-000037 "every no-break space becomes an ordinary space" vs N-000307 exceptions. **Chose N-000307.** A no-break space is kept when a digit is on either side, or before `: ; ! ? » › % €`, or after `« ‹`.
3. **CF-000081, CF-000082, CF-000083** usage message stream: N-000098 says error stream; N-000232 and N-000640 and N-000740 say standard output. **Chose standard output, exit 0.** It is the interface's explicit output contract, and `--help` output should not be an error.
4. **CF-000086, CF-000114** decisive floor: N-000134 "a decisive finding always lifts to 45 whatever the confidence" vs N-000136 "a single decisive family … only when confidence is above low". **Chose N-000136.** One decisive family lifts the score to 45 only at `moderate` or `high` confidence; two distinct decisive families lift it to 65.
5. **CF-000168** stop phrase: N-000383 "anywhere" vs N-000475 "entire prompt". **Chose the entire prompt** (`stop prosecheck` or `prosecheck off`, letter case ignored). The router and the interface say so too.
6. **CF-000179, CF-000221** stats transcript: N-001107 named transcript vs N-001113 newer transcript is read. **Chose the named transcript**; if it is not readable the reply says so, with no fallback. N-000544 says the same.
7. **CF-000195, CF-000196** trailing whitespace: N-000314 keeps two trailing spaces as a markdown hard break; N-000330 says remove them "even when two spaces were meant as a markdown hard break". **Chose removal** (N-000330 is the explicit rule; the detector also flags it as 68).
8. **CF-000210, CF-000235** `utm_source`: N-000174 "any utm_source is an AI tracking parameter" vs N-000175/N-000176 host-list rule. **Chose the host list**: a `utm_source` whose value is exactly one of the seven hosts.
9. **CF-000211, CF-000214** several file operands: N-000234, N-000719 and the "Several file operands" section (N-000783..787) say the first file is scanned; the signature line (N-000739) says the last one is. **Chose the first file**, which is what the spec's dedicated section and the PRD both say.
10. **CF-000219** transition clusters: N-000157 says one opener fires; N-000158 says two or more in one paragraph. **Chose two or more** (the family rule itself).
11. **CF-000234** hedge stacking: listed among the twelve writing-advice families (weight zero) vs "each sentence with stacked hedges adds to the score". **Chose weight zero** (the explicit list of twelve).
12. **CF-000236** apply_patch paths: N-000429 "at most 16" vs N-000834 "at most ten". **Chose ten.** Ten satisfies both "at most" statements.
13. **CF-000237** ledger deletion: NFR and FP-06 say a ledger more than seven days old is gone or not listed; N-000702 says deleted when untouched for more than one day. **Chose seven days** (two statements, and the privacy NFR).
14. **CF-000238** environment level: N-000390 says the environment is used only when nothing valid is stored; N-000701 says the environment takes precedence. **Chose environment precedence** when `PROSECHECK_DEFAULT_MODE` names one of the four words.
15. **CF-000239** session-prose score threshold: N-000554 "longer than 200 characters" vs N-001117 "longer than 500 characters". **Chose 500** (interface, output contract).
16. **CF-000240** catalogue 17: N-000126 tailing-negation form score-moving vs N-000750 "both forms are writing advice". **Chose:** tailing negation is score-moving; the parallelism form is weight-zero advice, reported as `17_negative_parallelism`. The tailing form is keyed `17_tailing_negation`.

## Gaps the spec does not state, and what was assumed

- **Score formula.** The spec gives family counting, caps, floors and bands, but no per-family points. Used: 12 points per distinct score-moving family, +8 for each decisive family (`compute_score` in `detect.py`). Caps: one family ≤ 40; monotony only ≤ 20; monotony and uniform paragraphs ≤ 40. Floors: as stated in FP-01, plus 65 for two decisive families and 45 for one decisive family at `moderate` or `high` confidence.
- **Family rules left open.** Stock compounds (family 4), list of marketing slop (69), and the cluster lists are the implementer's choice. The choices are in `detect.py`. Adjective chains (family 6) are approximate: a four-item list that has an adjectival or stock adjective word.
- **Homoglyph map.** The spec says "the Cyrillic, Greek, Armenian and Arabic-presentation lookalikes". The map covers the Cyrillic, Greek, and Armenian lookalikes that I could identify; Arabic-presentation forms are not in it.
- **Label caps.** Guard: 5 (FP-05 "up to five"). Check: 8 (FP-06). Show and ledger: 5. Labels are the fired families' titles.
- **Interval (`--ci`).** Resampled sentences: 100 draws, fixed seed, 5th to 95th percentile. Only sentence-located families are resampled; document-level rules are held fixed.
- **Timeouts.** Plain text 8 s, archive or notebook 15 s (FP-05 and FP-01). The detector itself has no timeout.
- **Caps.** Plain text 512 KB (524,288 bytes); archive and notebook 4 MB (4,194,304 bytes). Enforced by the guard and `check`, not by the detector command (as the spec says).
- **Archive members.** Members larger than 64 MB are read as empty. Only `word/document.xml` (docx), `ppt/slides/slideN.xml` (pptx), sheets and shared strings (xlsx), `content.xml` (odf), and chapter XHTML (epub, not `nav`) are read.
- **Ledger naming.** `.prosecheck-ledger-<first 16 hex of sha256(session_id)>`; no session id gives `.prosecheck-ledger`.
- **Stats.** Assistant turns and token totals are counted once per message `id` (assumed: streamed rows repeat an id). The transcript is searched recursively under `projects`, up to depth four, newest first. Fenced code is removed before scoring the prose slice.
- **Hook working directory.** The payload `cwd` is used when given; otherwise the process cwd.
- **Guard and plugin tree.** Files inside the plugin root are skipped (FP-05). Because this repository is both the plugin and the workspace, edits under `/app` are not guarded. That follows the spec's rule; a host that installs the plugin elsewhere does not hit this.
- **Dash in operands.** A lone `-` is treated as an unknown option (exit 2), following the spec's "any other argument that begins with `-`".
- **Unknown extensions** are read as plain text by the detector. The guard only scores the twenty formats.
- **Encodings.** Plain-text decoding is UTF-8 with `errors=replace`; a UTF-16 BOM selects UTF-16; a UTF-8 BOM is dropped.
- **`/prosecheck status`** reports the effective level (environment first, then stored).
- **Doctor and check.** The doctor's Python probe scores a built-in sample sentence. `check` uses the same detector call as the guard.
- **Exported contract.** At full and strict, one line names `CLAUDE_PLUGIN_ROOT` with `skills` and `plugins`. The export never names a machine path or a user name.
- **Live contract** names this machine's detector path (allowed by the spec).
- **Ethics and welcome text** are written by hand in `ETHICS.md` and `prosecheck-common.js`.
- **Host wiring.** The spec names the hook files and their events but does not specify a plugin manifest or hook registration file (for example `hooks.json`). None was written, so the plugin is not wired into a host by this repository alone.

## Not built, by design

- Non-goals (FP-09, `N-000082`..`N-000093`): no authorship classifier, no PDF or RTF reading, no in-place rewriting of docx, epub, odt or ipynb, no hosted service, no third-party detector integration.
- The bundled skill's rewrite instructions (`N-000050`, `N-000051`): a host-agent asset, not a detector obligation. Not shipped.
- The recorded-session demo, documentation checker, evaluation script, and status-line helper (`N-000668`..`N-000673`, `N-000093`).

## Checklist accounting

`spec/CHECKLIST.md` has 1126 ids. Each id is either implemented in the code for its pack, or listed under "Not done" below. "Implemented" is per pack, not verified id by id; the pack-level checks were smoke tests (see Verification). Pack 01 has no ids.

| Pack | Ids | Range | State |
|---|---|---|---|
| 02 | 5 | N-000588..592 | implemented (stdlib only, Python 3.9+, Node) |
| 03 | 10 | N-000593..602 | implemented (CPU baseline, no build step) |
| 04 | 18 | N-000001..018 | implemented; N-000016..018 are document-ordering statements, not applicable |
| 05 | 22 | N-000019..040 | implemented (bands, hook phrases, confidence, ledger base name) |
| 06 | 11 | N-000041..051 | implemented; N-000049..051 by omission (see Not built) |
| 07 | 26 | N-000052..077 | implemented; platforms tested on Linux only |
| 08 | 4 | N-000078..081 | implemented |
| 09 | 12 | N-000082..093 | not done by design (non-goals) |
| 10 | 149 | N-000094..242 | implemented (FP-01: report, families, metrics, errors) |
| 11 | 56 | N-000243..298 | implemented (FP-02: extraction, caps, window) |
| 12 | 33 | N-000299..331 | implemented (FP-03: cleanup); AC N-000305 and N-000309 tested |
| 13 | 63 | N-000332..394 | implemented (FP-04: contract, welcome, reminder, subagent) |
| 14 | 62 | N-000395..456 | implemented (FP-05: guard, ledger) |
| 15 | 121 | N-000457..577 | implemented (FP-06: router, check, doctor, show, init, stats) |
| 16 | 10 | N-000578..587 | implemented; N-000581..584 via `ETHICS.md` |
| 17 | 24 | N-000603..626 | implemented (product overview, layout) |
| 18 | 47 | N-000627..673 | implemented; N-000668..673 not built (see Not built) |
| 19 | 29 | N-000674..702 | implemented; retention conflict resolved (item 13) |
| 20 | 28 | N-000703..730 | implemented (exit codes, streams, config, ledger) |
| 21 | 57 | N-000731..787 | implemented (detect.py interface) |
| 22 | 25 | N-000788..812 | implemented (session-start hook) |
| 23 | 6 | N-000813..818 | implemented (subagent hook) |
| 24 | 17 | N-000819..835 | implemented (post-tool-use reply) |
| 25 | 5 | N-000836..840 | implemented (`content` field: not used for scoring) |
| 26 | 3 | N-000841..843 | implemented (`cwd`) |
| 27 | 3 | N-000844..846 | implemented (`file_path`) |
| 28 | 10 | N-000847..856 | implemented (`prompt`, `session_id`) |
| 29 | 7 | N-000857..863 | implemented (`tool_input`, `notebook_path`, `command`) |
| 30 | 6 | N-000864..869 | implemented (`tool_name`) |
| 31 | 39 | N-000870..908 | implemented (`/prosecheck` router, block decision, menu document) |
| 32 | 26 | N-000909..934 | implemented (`help`) |
| 33 | 7 | N-000935..941 | implemented (`status`) |
| 34 | 10 | N-000942..951 | implemented (`lite`, `full`, `strict`, `off`, `on`) |
| 35 | 41 | N-000952..992 | implemented (`check`) |
| 36 | 36 | N-000993..1028 | implemented (`doctor`) |
| 37 | 32 | N-001029..1060 | implemented (`show`) |
| 38 | 42 | N-001061..1102 | implemented (`init`) |
| 39 | 19 | N-001103..1121 | implemented (`stats`); transcript conflicts resolved (items 6 and 15) |
| 40 | 5 | N-001122..1126 | implemented (`transcript_path`) |

### Not done (with reasons)

- **N-000082..N-000093** (pack 09, non-goals): not built by design. Nothing in the spec asks for them.
- **N-000049, N-000050, N-000051** (pack 06): the inventory says the product adds no surfaces and that the bundled skill is not a feature. The skill is not shipped.
- **N-000668..N-000673** (pack 18, "not in this surface"): not built, by omission.
- **N-000016, N-000017, N-000018** (pack 04): document-ordering statements; no code applies.

## Verification

- `python3 -m unittest discover -s tests -v`: 19 tests pass (AC tests, CLI exit codes, cleanup, rescan, scoring rules).
- Smoke-run of every hook with an isolated `CLAUDE_CONFIG_DIR`:
  - session start (welcome once, then contract; off prints nothing; ledger prune);
  - `/prosecheck` `doctor` (four `[OK]` lines and the closer), `status`, `help`, `lite`, `full`, `off`, `on`, `init` (AGENTS.md written once, then reported as already present), `check` (report-only, truncation coverage line), `show`, `stats`, unknown subcommand, stop phrases;
  - guard: a flagged `.md` nudge, a clean file silent, a PDF recorded as binary, a CLAUDE.md skipped, apply_patch multi-file;
  - malformed stdin: every hook exits 0.
- Timing: 512 KB of zero-width spaces and spaces ~0.7 s; 262,144-character prose window ~0.5 s; `--ci` on a long text ~0.8 s. Limits are 8 s (plain) and 15 s (archive).
- Extraction checked on synthetic docx, pptx, xlsx, odt, epub, and ipynb fixtures; bad notebook and PDF give empty input.

## Not verified

- Windows and macOS (the spec lists them; only Linux was run).
- Python 3.9 (only 3.13 is installed here). The code avoids 3.10+ syntax, but this is not proven by a run.
- Real host integration (Claude Code or another agent loading the hooks and the menu document). Only the hook processes were run directly.
- Catalogue coverage is a judgement from the rule text. Regexes were smoke-tested with one trigger sentence per family, and a few lists are approximations (family 6, family 4, family 69, family 66's map). Expect some false positives and negatives against real prose.

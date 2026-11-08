# NOTES

Build notes for the prosecheck 0.9.3 spec in `spec/`. The spec was read in full (packs 01–40).
`spec/` was not modified. Nothing was installed or fetched from the network.

## What is in /app

| Path | What it is | Spec |
|---|---|---|
| `scripts/detect.py` | Detector CLI (standard library only, Python 3.9+): report, `--clean`, `--ci`, `--help`, errors | FP-01, FP-02, FP-03, Interface `scripts/detect.py` |
| `hooks/prosecheck-activate.js` | session-start hook: welcome (first start), writing contract | FP-04, Interface `hooks/prosecheck-activate.js` |
| `hooks/prosecheck-tracker.js` | prompt-submit hook and the `/prosecheck` router (all subcommands) | FP-04, FP-06, Interface `/prosecheck` and subcommands |
| `hooks/prosecheck-subagent.js` | subagent-start hook: contract in the JSON envelope | FP-04, Interface |
| `hooks/prosecheck-guard.js` | post-tool-use hook: saved-file guard and nudge | FP-05, Interface post-tool-use reply |
| `hooks/prosecheck-stats.js` | `stats` entry: transcript token totals and own-prose score | FP-06, Interface `stats` |
| `hooks/lib/prosecheck-core.js` | shared config, ledger, detector calls, contract text, reply texts | FP-04/05/06, Interface naming and config |
| `hooks/hooks.json` | hook registration (`${CLAUDE_PLUGIN_ROOT}` paths) | Interface plugin hooks |
| `commands/prosecheck.md` | menu document; body `/prosecheck $ARGUMENTS` | Interface shipped menu document |
| `.cursor/rules/prosecheck.mdc` | Cursor rule copied by `init`; prose globs only | FP-06 `init`, Interface |
| `.claude-plugin/plugin.json` | plugin manifest (my addition; the spec does not require one) | n/a |
| `tests/test_detect.py` | 35 unit tests for the detector (`python3 -m unittest discover -s tests -t tests`) | |
| `tests/hooks.test.js` | 15 hook tests, each hook run as a separate process (`node --test tests/hooks.test.js`) | |

Run from `/app`. No install or build step is needed: `python3 scripts/detect.py FILE`, and the hooks are
`node hooks/<name>.js` reading host JSON on standard input.

Verification done here: Python 3.13 and Node 22 only. The 35 Python tests and 15 Node tests pass. The
detector was fuzzed on 400 random inputs with no exceptions, and a 512 KB input scores in about 1 s
(cleanup in under 1 s). Python 3.9 and Windows were not run.

## Spec conflicts (23 unsettled contradictions, plus the others I found)

The export says the 23 contradictions in `MAP.md` have no human verdict. For each one I chose a side. Rule used:
the PRD (`Full_PRD.md` packs) governs behavior; the Interface Contract governs output shape. Where both sides are
explicit, I took the more specific statement. Each entry names both sides and the pack they are in.

1. **CF-000011 — ledger retention (20 or 50).** A: pack 14, N-000436 "At most the newest 20 records are kept."
   B: pack 20, N-000729 "Each ledger keeps its newest 50 records." Built: **20** (the PRD governs what a
   ledger keeps; N-000729 defers to the PRD for "how long it is kept").
2. **CF-000080 — no-break spaces.** A: pack 05, N-000037 "Every no-break space becomes an ordinary space."
   B: pack 12, N-000307 "except a no-break space (U+00A0) or narrow no-break space (U+202F) that holds something
   together". Built: **B's exception**. An NBSP or NNBSP is kept when a digit is on either side, when it comes
   before `: ; ! ? » › % €`, or when it comes after `« ‹`. Other space separators become U+0020.
3. **CF-000081 / CF-000082 / CF-000083 — where the usage message goes.** A: pack 10, N-000098 "The usage message
   goes to the error stream". B: pack 10, N-000232 "prints the usage message to standard output and succeeds";
   pack 10, N-000640 and pack 21, N-000740 "write the usage message to standard output and exit 0". Built:
   **standard output, exit 0** (three explicit statements against one).
4. **CF-000086 / CF-000114 — the 45 floor for a decisive family.** A: pack 10, N-000134 "A decisive finding always
   lifts the score to at least 45, whatever the confidence." B: pack 10, N-000136–N-000137 "A single decisive
   family raises it to at least 45 only when confidence is above low"; "does not take that 45 floor". Built:
   **B**. One decisive family gives 45 only at moderate or high confidence. At none or low, the single-family cap
   of 40 applies.
5. **CF-000168 — the stop phrase.** A: pack 13, N-000383 "A prompt that contains `stop prosecheck` anywhere
   switches the tool off." B: pack 15, N-000475 and pack 31, N-000885 "the same words with anything else before or
   after them are an ordinary prompt" (entire prompt). Built: **the entire prompt only** (case ignored, surrounding
   whitespace trimmed). `prosecheck off` works the same way.
6. **CF-000179 / CF-000221 — named transcript versus newer transcript.** A: pack 15, N-000544 "a named
   transcript wins over a newer one". B: pack 39, N-001113 "When the projects folder holds a transcript newer than
   the named one, the newer transcript is read." Built: **named wins**. The newest transcript under `projects` is
   used only when no `transcript_path` is given (pack 40, N-001123–N-001126).
7. **CF-000195 / CF-000196 — trailing spaces as a markdown hard break.** A: pack 12, N-000314 "Two trailing
   spaces that end a line of prose are a markdown hard break and are kept." B: pack 12, N-000330 "Trailing
   whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is
   required." Built: **removed** (the later, emphatic statement; N-000312 "spaces and tabs at the end of every
   line" also supports removal).
8. **CF-000210 / CF-000235 — `utm_source`.** A: pack 10, N-000174 "Any `utm_source` parameter left in a link
   is an AI tracking parameter." B: N-000175–N-000176 fires only when the value is one of seven hosts, and "only
   when that whole host name is one of those domains". Built: **the seven hosts only**.
9. **CF-000211 / CF-000214 / CF-000083 — several file operands.** A: pack 10 N-000234, pack 20 N-000719, pack 21
   N-000787 "the first file is scanned". B: pack 21 N-000739 "When several operands are given, the last one is the
   file scanned." Built: **first file** (three statements; the notice on stderr names it).
10. **CF-000219 — transition clusters.** A: pack 10, N-000157 "already fires transition clusters" for one opener.
    B: pack 10, N-000158 "two or more sentence-opening transitions ... in one paragraph." Built: **two or more in
    one paragraph**.
11. **CF-000234 — hedge stacking (54).** A: pack 10, N-000116–N-000122, the list of 12 writing-advice numbers
    (includes 54). B: pack 10, N-000170 "Each sentence with stacked hedges adds to the score." Built: **weight zero**
    (the explicit list; the PRD says which numbers are advice, as pack 19 N-000689 also says).
12. **CF-000236 — apply_patch paths scored.** A: pack 14, N-000429 "at most 16 distinct paths". B: pack 22,
    N-000834 "At most ten paths of one payload are scored." Built: **16 scored** (the PRD governs behavior); the
    hook reply lists each flagged file on its own line.
13. **CF-000237 — ledger age.** A: pack 07, N-000069 "more than seven days old is gone", repeated in pack 15 and
    pack 37. B: pack 19, N-000702 "A ledger untouched for more than one day is deleted at the next session start."
    Built: **seven days**. Ledgers older than seven days are deleted at session start and not listed.
14. **CF-000238 — `PROSECHECK_DEFAULT_MODE` versus the stored level.** A: pack 13, N-000390 the environment word is
    used "when nothing valid is stored". B: pack 19, N-000701 "when it is set, it takes precedence over the stored
    level". Built: **A**, because pack 19 N-000686 itself says the nothing-valid case is the PRD's rule.
15. **CF-000239 — when the session-prose score is printed.** A: pack 15, N-000554 "longer than 200 characters".
    B: pack 39, N-001117 "longer than 500 characters". Built: **200** (PRD behavior).
16. **CF-000240 — catalogue 17.** A: pack 10, N-000126 "The tailing-negation form is score-moving." B: pack 21,
    N-000750 "Both forms of catalogue 17 are writing advice and carry weight zero." Built: **tailing form is
    score-moving; the parallelism form is weight zero**. Report keys are exactly `17_negative_parallelism` and
    `17_tailing_negation`.

The 16 numbered entries above cover all 23 unsettled contradiction ids in `MAP.md`. Reading the packs turned up no others.

## Gaps the spec leaves open, and what I assumed

- **Base score.** The PRD gives caps and floors but no base formula. Built: 8 points per distinct score-moving
  family, plus 2 per extra hit (capped at 6 extra hits), clamped to 0–100; then the single-family cap, rhythm caps,
  decisive floors and the short/long-document floors are applied.
- **Decisive floor ordering.** The 65 floor for two decisive families and the 45 floor for one are applied after the caps.
- **Model-dialect family (2)** fires only on two or more hits. FP-04 says the dialect words "need two hits";
  applied to the whole family.
- **Lexical inflection.** Single words match their common inflections (`-s`, `-es`, `-ed`, `-ing`, `-ies`).
  Adjectives and phrases match literally.
- **Stacked adjectives (6).** Approximated without a part-of-speech tagger: four comma-joined words where one of the
  first three is a stock evaluative adjective or has an adjective ending, and the fourth does not.
- **Lists the spec leaves to the implementer:** notability outlets (family 11), marketing imperatives (3), stock
  hyphenated compounds (4), canonical marketing phrases (69), emoji ranges (57), the lookalike map for 66 (the
  Cyrillic, Greek and Armenian letters that look like the listed Latin letters), and the small-word list for title case (59).
- **Thresholds the spec does not state:** sentence-length monotony and paragraph variation use the stated
  coefficient-of-variation limits (0.35 and 0.4). Mechanical alternation (41) needs five consecutive sign changes,
  each step at least 4 words. Contraction absence (55) needs first-person words at 2% or more of the text, at least
  two written-out forms, and more written-out than contracted. Degenerate repetition (71) needs repeated six-word
  runs to be 20% or more of the runs. Decorative rules (70) need 24 or more lines and three rules. Boldface (56)
  counts every bold span; the spec gives no threshold.
- **Sentences and paragraphs.** Sentences end at `.`, `!`, `?`, `…` (with closing quotes) or a paragraph break.
  Paragraphs are split on blank lines. Words are runs of letters, digits, apostrophes and hyphens.
- **Exclusions** (no findings inside them): front matter, fenced code (CommonMark closing rule), runs of two or more
  blockquote lines, table rows, badge lines, inline code. The masked text keeps offsets, so samples come from the
  original window.
- **Interval (`--ci`).** 200 resamples of the scanned sentences with seed 0; findings tied to a sentence move with it;
  document-level findings (rhythm, semicolons, contractions) stay fixed; 2.5th and 97.5th percentiles. Fewer than
  four sentences gives `null` and a note.
- **Character cleanup** works on the whole extracted text, not just the window (the spec does not say which).
  Leading whitespace is removed along with leading blank lines, so the trim leaves a clean start. A single final line
  ending is restored only when the input had one; a CRLF input gets CRLF.
- **Invisible-character exceptions** are implemented for every case FP-03 lists. Some are approximations: tag
  characters are kept when the run is preceded by a black-flag base or an emoji; a zero-width joiner is kept beside a
  joining script or a symbol; a bidirectional control is kept when the text has right-to-left script.
- **Decoding.** UTF-8 (with an optional BOM) or UTF-16 with a BOM. Other bytes are decoded as UTF-8 with a fallback to
  cp1252. The spec only says UTF-8 and UTF-16 with a BOM.
- **Zip-based documents.** Paragraphs and cells are separated by a single line feed (the spec says "line breaks").
  Blank-line paragraph rules therefore see one paragraph per document. No per-member size cutoff is applied to
  archives (the spec leaves that to the implementer).
- **Ledger.** The session id is encoded in the ledger file name (`.prosecheck-ledger-<id>`; characters outside
  `[A-Za-z0-9_]` are hex-escaped). With no session id the file is `.prosecheck-ledger`.
- **Instruction files.** The exact names `claude.md`, `claude.local.md`, `agents.md`, `agents.local.md`, `skill.md`
  and `memory.md` are matched case-insensitively, and so are their stems with a non-prose extension. The spec says
  "exactly"; I read that as the file name, not the letter case.
- **Plugin root and skips.** The plugin root defaults to the directory above `hooks/` (`/app` here). Per FP-05 the
  guard skips every file under it, so a prose file saved inside `/app` is not scored. This follows the spec.
- **Stats.** `stats` is answered inside the prompt router, and `prosecheck-stats.js` also answers a stats prompt when
  run directly. It is not registered separately in `hooks.json`, so one host event does not produce two replies.
  Assistant messages are de-duplicated by `message.id` (the last usage wins). Fenced code is removed before scoring.
- **`check` and `doctor` run the detector** as `python3 -I`, then `python`, then `py`. With `py` the spec's
  `-3` is not passed; on Windows the first working interpreter is used.
- **Writing contract text.** I wrote the contract sentences myself, from the FP-04 rules and the Interface shell
  requirements. The banned list is the FP-04 list, using the spec's words (landscape and journey carry "(abstract)").
- **Welcome.** Shown once: when no `.prosecheck-active` flag exists at session start. The effective level is then
  stored, so later hooks see it.
- **Doctor closers.** The detector check is "bundled detector found in the plugin tree"; the Python check runs the
  detector on a fixed sample and requires a numeric score.

## Not built, and why

- **The nine catalogue numbers with no detector** (7, 9, 28, 29, 43, 45, 49, 52, 53). The PRD says they never
  appear as findings. Not built as checks; the detector never reports them.
- **Non-goals in pack 09** (no website, no PDF or RTF reading, no in-place rewrite of documents, no authorship
  classifier, no third-party detectors). Satisfied by not building them.
- **The bundled skill file** (pack 06, N-000050 and N-000051). The PRD says it is not a feature point. Not shipped.
  The doctor's detector check does look for `skills/prosecheck/scripts/detect.py` as a fallback location.
- **The recorded-session demo, documentation checker, evaluation script and status-line helper** (pack 09, N-000093).
  Not product surfaces.

## Checklist accounting

Every id in `spec/CHECKLIST.md` (1126 in total, in 40 packs) is accounted for below. The checklist lists ids in
contiguous runs per pack, so each row covers its whole run. "Implemented" means the behavior is in the files named.
Tests are noted where the suite exercises the pack's behavior directly.

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 | none | n/a (no node) | stdlib only; no install step (`scripts/detect.py`, `hooks/*.js`) |
| 02 | N-000588–N-000592 | implemented | stdlib only; no compiled parts; Python 3.9+, Node for hooks |
| 03 | N-000593–N-000602 | implemented | CPU baseline: scripts run from the source tree; no build |
| 04 | N-000001–N-000018 | implemented | local-only product (no network client, no telemetry, no upload) |
| 05 | N-000019–N-000040 | implemented | `LABELS`, bands, levels, hook phrases (`detect.py`, `prosecheck-core.js`) |
| 06 | N-000041–N-000051 | implemented; skill not built (see above) | CLI, hooks, `commands/prosecheck.md` |
| 07 | N-000052–N-000077 | implemented | no network; 8 s / 15 s budgets; deterministic scan (interval seeded) |
| 08 | N-000078–N-000081 | implemented | each feature is delivered by the real detector or hooks |
| 09 | N-000082–N-000093 | non-goals, not built | see "Not built" |
| 10 | N-000094–N-000242 | implemented; tested | `detect.py`: `Analysis`, `mask_excluded`, `compute_score`, `band_for`, `analyze`, `main`; `tests/test_detect.py` (ScoreRules, ReportShape, CommandLine, Window) |
| 11 | N-000243–N-000298 | implemented; tested | `detect.py`: `extract_bytes`, `extract_zip_document`, `_extract_*`; `tests/test_detect.py` (Extraction) |
| 12 | N-000299–N-000331 | implemented; tested | `detect.py`: `scrub`, `_invisible_removable`, `_nbsp_kept`, `fold`; `tests/test_detect.py` (CharacterLayer, N-000305, N-000309) |
| 13 | N-000332–N-000394 | implemented; tested | `prosecheck-activate.js`, `prosecheck-subagent.js`, `prosecheck-core.js` (`liveContract`, `contractCore`, `welcomeText`); `tests/hooks.test.js` |
| 14 | N-000395–N-000456 | implemented; tested | `prosecheck-guard.js`, `prosecheck-core.js` (`scoreFile`, ledger); `tests/hooks.test.js` (guard tests) |
| 15 | N-000457–N-000577 | implemented; tested | `prosecheck-tracker.js` (`route`, help, check, show, init), `prosecheck-stats.js`; `tests/hooks.test.js` |
| 16 | N-000578–N-000587 | implemented | local only; contract forbids narrating; no authorship words in replies |
| 17 | N-000603–N-000626 | implemented | product overview: CLI and hooks; Python and Node only |
| 18 | N-000627–N-000673 | implemented | CLI switches and exit codes; hook names; files under `hooks/`, `AGENTS.md`, `.cursor/rules/` |
| 19 | N-000674–N-000702 | implemented | constants: bands, hook phrases, confidence set, `CLAUDE_CONFIG_DIR`, `CLAUDE_PLUGIN_ROOT`, `PROSECHECK_DEFAULT_MODE`, flag and ledger names |
| 20 | N-000703–N-000730 | implemented; tested | exit codes 0 / 1 / 2 and error objects in `detect.py`; hooks exit 0; ledger; `tests/test_detect.py`, `tests/hooks.test.js` |
| 21 | N-000731–N-000787 | implemented; tested | `detect.py` `main` and report shape (`_metrics` members); `tests/test_detect.py` |
| 22 | N-000788–N-000812 | implemented; tested | `prosecheck-activate.js`: off prints nothing; welcome then contract; contract shell parts (banned list, source-code wording, level targets) |
| 23 | N-000813–N-000818 | implemented; tested | `prosecheck-subagent.js`: JSON envelope with `SubagentStart`; `tests/hooks.test.js` |
| 24 | N-000819–N-000835 | implemented; tested | `prosecheck-guard.js` reply line format; `tests/hooks.test.js` |
| 25–30 | N-000836–N-000869 | implemented | payload fields read by the hooks (`content`, `cwd`, `file_path`, `prompt`, `tool_input`, `tool_name`, `session_id`) |
| 31 | N-000870–N-000908 | implemented; tested | `prosecheck-tracker.js` `route`: block decision, unknown word, stop phrases, ordinary prompts, `commands/prosecheck.md` |
| 32 | N-000909–N-000934 | implemented; tested | `helpReply` in `prosecheck-tracker.js`; `tests/hooks.test.js` (router test) |
| 33 | N-000935–N-000941 | implemented | `status` reply: one line |
| 34 | N-000942–N-000951 | implemented; tested | `lite`, `full`, `strict`, `off`, `on` store and reply; `tests/hooks.test.js` |
| 35 | N-000952–N-000992 | implemented; tested | `checkReply`; `tests/hooks.test.js` (check test) |
| 36 | N-000993–N-001028 | implemented; tested | `doctorReply`; `tests/hooks.test.js` (doctor tests, including python not found) |
| 37 | N-001029–N-001060 | implemented; tested | `showReply`; `tests/hooks.test.js` (guard and show test) |
| 38 | N-001061–N-001102 | implemented; tested | `initReply`, `exportContract`, `exportBlock`, `.cursor/rules/prosecheck.mdc`; `tests/hooks.test.js` (init tests) |
| 39 | N-001103–N-001121 | implemented; tested | `statsReply` in `prosecheck-stats.js`; `tests/hooks.test.js` (stats test) |
| 40 | N-001122–N-001126 | implemented; tested | `statsReply` reads `transcript_path` first; `tests/hooks.test.js` (stats test) |

Ids that are "implemented" but where the spec leaves the wording or thresholds to the implementer (for example,
the lists in the Gaps section) are implemented with the choices above, not verified against any other reading.

## Limits and what I did not check

- Python 3.9 and Windows were not run; only Python 3.13 and Node 22 were available. The code avoids 3.10+ syntax, but
  this is not proven.
- Pattern thresholds that the spec leaves to the implementer (see Gaps) are my choices. A hidden test that expects
  different thresholds would fail on those points.
- The hooks were run as separate processes with a sandbox config directory. They were not run inside a real Claude
  Code, Cursor or other host session.
- The contract text is my wording, checked for the shell requirements in the Interface Contract (banned list present,
  "source code" only with `never`/`not` earlier in its sentence, level targets, `--clean` only at strict, no detector
  path in the export).
- No commit was made. The directory is not a git repository.

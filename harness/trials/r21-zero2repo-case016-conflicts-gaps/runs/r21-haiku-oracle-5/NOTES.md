# prosecheck — implementation notes

Built from `spec/` (export of the prosecheck PRD and interface contract, 40 packs, 1126 checklist ids).
`spec/` is unchanged. `COVERAGE.md` maps every checklist id to where it is implemented.

## Layout

| Path | What it is |
|---|---|
| `scripts/detect.py` | The detector (Python 3, standard library only). `python3 scripts/detect.py [--clean] [--ci] [--] [FILE]`. |
| `hooks/prosecheck-activate.js` | Session-start hook: writing contract, one-time welcome, creates the default level flag. |
| `hooks/prosecheck-tracker.js` | Prompt-submit hook: `/prosecheck` router, stop phrases, per-prompt reminder. |
| `hooks/prosecheck-subagent.js` | Subagent-start hook: same contract in the SubagentStart envelope. |
| `hooks/prosecheck-guard.js` | Post-tool-use hook: scores saved prose files and nudges when flagged. |
| `hooks/prosecheck-stats.js` | Stand-alone entry for `stats` (the router calls the same code). |
| `hooks/lib/core.js`, `hooks/lib/commands.js`, `hooks/lib/stats.js` | Shared plumbing, command replies, stats. Node.js built-ins only. |
| `hooks/hooks.json`, `.claude-plugin/plugin.json` | Plugin wiring (hook events and matchers). |
| `commands/prosecheck.md` | Host `/` menu document; `$ARGUMENTS` forwards to the router. |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule that `init` copies. |
| `tests/test_detect.py`, `tests/hooks.test.js` | Tests. Run `python3 -m unittest discover -s tests` and `node --test tests/hooks.test.js`. |

Nothing needs installing or building. The judge can run the detector from `/app` with `python3 scripts/detect.py`.

## Verification status

- Python suite: `python3 -m unittest discover -s tests` (30 tests) — passing.
- Node suite: `node --test tests/hooks.test.js` (17 tests) — passing.
- Ran by hand: every hook, every `/prosecheck` subcommand, stop phrases, guard on Write and apply_patch,
  check/show/stats/init/doctor (including the off branch and the no-Python branch), extraction for
  docx, xlsx, odt, epub, ipynb, bad zip, pdf, and pathological inputs (262 KB of spaces, zero-width runs,
  punctuation soup), which all finish in under 1 s.
- Not tested: Python 3.9 specifically (the code uses only 3.9-compatible features, but the local interpreter is 3.13).
  Windows paths and CRLF on disk were not exercised beyond line-ending normalization.

## Conflicts in the specification and what was built

Each item names the two sides (node ids, PRD = `Full_PRD.md` FP number, IC = Interface_Contract pack).
Unsettled contradictions listed by the export (`CF-…`) are marked.

1. **Usage message stream.** FP-01 N-000098 says "the usage message goes to the error stream";
   FP-01 N-000232, IC N-000640 and N-000740 say `--help`/`-h` print usage to standard output and exit 0.
   *Built:* `--help`/`-h` print usage on stdout, exit 0. Errors go to stderr as JSON. (CF-000081/82/83.)
2. **Several file operands.** FP-01 N-000234 and IC pack 20 N-000719 say the first file is scanned;
   IC pack 21 Signature N-000739 says the last one is. *Built:* the first is scanned, with a notice on stderr. (CF-000211, CF-000214.)
3. **Ledger record cap.** FP-05 N-000436 says newest 20; IC pack 20 N-000729 says newest 50. *Built:* 20. (CF-000011.)
4. **Ledger retention.** Non-functional constraints N-000069 say a ledger is gone when last modified more than seven days ago;
   IC pack 19 N-000702 says it is deleted when untouched for more than one day at session start.
   *Built:* seven days, for both pruning at session start and hiding in `show`. (CF-000237.)
5. **apply_patch file cap.** FP-05 N-000429 says at most 16 distinct paths; IC pack 24 N-000834 says ten.
   *Built:* 16. (CF-000236.)
6. **Session-prose score threshold.** FP-06 N-000554 says the score is printed when the slice is longer than 200
   characters; IC pack 39 N-001117 says 500. *Built:* 200. (CF-000239.)
7. **Named transcript vs newer one.** FP-06 N-000544 says a named transcript wins over a newer one; IC pack 39
   N-001113 says the newer one is read. *Built:* the named `transcript_path` wins. (CF-000179, CF-000221.)
8. **Stop phrase scope.** FP-04 N-000383 says "stop prosecheck" anywhere in a prompt switches off; FP-06 N-000475
   and IC pack 31 say only as the entire prompt. *Built:* entire prompt only, case-insensitive. (CF-000168.)
9. **Environment default vs stored level.** FP-04 N-000390 says the environment supplies a level only when nothing
   valid is stored; IC pack 19 N-000701 says `PROSECHECK_DEFAULT_MODE` takes precedence over the stored level.
   *Built:* the environment wins when it holds a valid word. Consequence: `/prosecheck off` has no effect while
   that variable is set. (CF-000238.)
10. **Decisive floor vs confidence.** FP-01 N-000134 says a decisive finding always lifts the score to at least 45;
    FP-01 N-000136/137 say a single decisive family reaches 45 only at confidence above `low`.
    *Built:* the 45 floor applies to a single decisive family only at `moderate` or `high` confidence; two or more
    decisive families always floor at 65 (N-000137 is clear on that). (CF-000086, CF-000114.)
11. **AI tracking parameter.** FP-01 N-000174 says any `utm_source` parameter counts; N-000175/176 limit it to seven
    named hosts. *Built:* only the seven named hosts. (CF-000210, CF-000235.)
12. **Catalogue 17, tailing negation.** FP-01 N-000126 says the tailing-negation form is score-moving; N-000750 says
    both forms are writing advice. *Built:* the tailing-negation form is score-moving; the parallelism form is weight
    zero. This matches the PRD's count of 50 score-moving numbers. (CF-000240.)
13. **Hedge stacking (54).** Listed as writing advice (weight zero) in N-000119, but N-000170 says each sentence with
    stacked hedges "adds to the score". *Built:* weight zero, matching the PRD's list of 12 advice numbers.
14. **Transition clusters (37) vs the family-36 note.** N-000157 says one transition opener "already fires transition
    clusters"; N-000158 (family 37) requires two or more in one paragraph. *Built:* the family-37 rule. (CF-000219.)
15. **No-break space.** N-000037 says every no-break space becomes an ordinary space; N-000307 keeps a no-break space
    that holds digits or punctuation together. *Built:* the N-000307 exceptions. (CF-000080.)
16. **Trailing spaces at the end of a line.** FP-03 N-000312 and N-000314 keep a two-space markdown hard break;
    N-000330 says trailing whitespace is removed even when it was meant as a hard break and calls that collapse
    "required, not optional". *Built:* the collapse (N-000330). (CF-000195, CF-000196.)
17. **Section marker in `init`.** FP-06 (N-000529–N-000542, the `init` entry) says the contract is wrapped in a prose-contract section with a section marker; IC N-001069–74
    says the section is recognised by the single copy of the contract, not by a required marker spelling.
    *Built:* recognised by the contract heading `## prosecheck writing contract`; no separate marker is written. (Not an unsettled contradiction; it is a wording choice the interface contract allows.)

## Not stated in the spec: what was assumed

- **Score formula.** The PRD gives bands, caps, floors, the score-moving / advice split and the confidence rules, but no
  per-family weight. *Built:* each score-moving family contributes `weight × (1 + 0.25 × min(hits−1, 4))`, with weight 7
  (decisive families 12, rhythm families 3), summed and capped at 100, then the caps and floors from the PRD. Writing
  advice has weight zero. The numbers are this implementation's choice; they are documented in `scripts/detect.py`.
- **Detector heuristics.** Several families are approximations of the prose rule: the stacked-adjective chain (no part-of-speech
  tagger), synonym clusters (threshold three distinct members, as stated), the stock lists (hyphenated pairs, promotional
  phrases, marketing slop, and the homoglyph table, which covers the common Cyrillic, Greek and Armenian lookalikes but not
  every Arabic-presentation form), bold-span overuse (threshold: three or more spans, not stated), decorative rules
  (three or more, in a document of at least 24 non-blank lines), degenerate repetition (20% or more of six-word runs repeated),
  contraction absence and semicolon underuse (threshold choices), and fragmented headers (a following line of four words or fewer).
- **Invisible-character exceptions.** FP-03 lists the kept positions. Those rules are implemented, but the neighbour tests
  (for example, a zero-width space beside a character from a script written without spaces) are approximations.
- **Cleanup window.** Scoring uses the first 262,144 characters. `--clean` scrubs the whole text, since the window governs
  findings and not the output text. Nothing in the spec says otherwise.
- **Plain-text decoding.** UTF-8 (with or without BOM), UTF-16 with BOM, and otherwise UTF-8 with replacement characters.
  A leading U+FEFF is removed as a byte-order mark. CRLF and CR line endings are normalized to LF before scoring.
- **Archive members.** The spec leaves the member size cutoff open. None is applied beyond the file caps.
- **`--ci` interval.** Resampled over sentences (200 rounds, fixed seed 20240601, 5th and 95th percentiles) using sentence-level
  family counts, so it is an approximation of rescoring. It needs at least four sentences.
- **Failure wording.** The five distinguishable failure reasons (Python not found, timed out, not a structured report,
  no numeric score, exited without a usable result) are implemented with distinct text. The unreadable-file case uses its own reason.
- **Plugin root.** When `CLAUDE_PLUGIN_ROOT` is unset, the plugin root is the parent of `hooks/`. In this repository that is `/app`.
  **Consequence:** the guard skips any file under the plugin root, so prose saved inside `/app` is not scored unless
  `CLAUDE_PLUGIN_ROOT` points elsewhere. This follows FP-05's "files inside the plugin's own install tree are skipped".
- **Hook entry points.** `hooks/hooks.json` and `.claude-plugin/plugin.json` are not described in the spec; they are written
  to match the event names and file names the interface contract lists.
- **Ledger file names.** `.prosecheck-ledger-<session_id>` (sanitized); `.prosecheck-ledger` when no session id is supplied.
  Each record has a `at` timestamp in addition to the fields the spec names.
- **Doctor sample text.** The Python check runs the detector on one short built-in sentence.
- **Default level.** The stored flag is written as `full` on the first session start, so later starts know it exists.
- **Live contract.** The session-start and subagent contract names this machine's detector path (permitted by FP-04 N-000392).
  The exported `AGENTS.md` uses the portable `scripts/detect.py` and the `CLAUDE_PLUGIN_ROOT` line; it has no user name or absolute path.

## Known limitations

- The detector is a triage heuristic. Its rule set follows the PRD; the exact thresholds for the heuristic families above are mine.
- `guard` and `doctor` depend on `python3`, `python` or `py` being on `PATH`; without any of them the guard records "Python not found" and emits nothing.
- The `show` label list and `check` label list are capped at five and eight as specified; labels are not sorted by weight.
- Annotations (`# spec:` in code, plus test names) cover 607 of the 1126 checklist ids directly, and 39 more are duplicates of annotated ids. 468 are covered at pack level, meaning the named files implement that pack but the id is not individually cited, and 12 are non-goals with nothing to build. `COVERAGE.md` lists each id and its status. Annotation was matched by topic, so a few ids may point at a neighbouring rule.

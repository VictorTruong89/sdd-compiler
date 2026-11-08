# NOTES

Implementation notes for the prosecheck build in `/app`. The spec under `spec/` is unchanged.
Spec pack files are cited as `pack NN` (`spec/packs/NN-*.md`); claim ids as `N-000000`.

## What was built

| Path | Role |
| --- | --- |
| `scripts/detect.py` | Detector command: extraction (20 formats), 62 machine-checked catalogue families, character layer, `--clean`, `--ci`, JSON report. Standard library only. |
| `hooks/prosecheck-lib.js` | Shared Node logic: config and mode flag, detector runner, ledgers, contract text, stats. |
| `hooks/prosecheck-commands.js` | `/prosecheck` router: every subcommand, stop phrases, check, doctor, show, init, help. |
| `hooks/prosecheck-activate.js` | session-start hook (welcome on first start, then the contract). |
| `hooks/prosecheck-tracker.js` | prompt-submit hook and command router (block replies; reminder for ordinary prompts). |
| `hooks/prosecheck-subagent.js` | subagent-start hook (contract in the JSON envelope). |
| `hooks/prosecheck-guard.js` | post-tool-use hook (saved-file guard; Write, Edit, MultiEdit, NotebookEdit, apply_patch). |
| `hooks/prosecheck-stats.js` | stats hook (token figures and session-prose score). |
| `hooks/hooks.json`, `.claude-plugin/plugin.json` | Event registration and manifest. |
| `commands/prosecheck.md` | Slash-command menu document; body forwards `$ARGUMENTS` to the router. |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule copied by `init` (prose globs only). |
| `tests/test_detect.py` | 27 unit tests for the detector. Run: `python3 -I -m unittest discover -s tests -v` |
| `README.md` | Short user-facing description, including the not-authorship statement. |

No build step. Hooks run with `node hooks/<file>.js`; the detector runs with `python3 scripts/detect.py`.

Verified by running: detector CLI exit codes and error objects; every zip-based format and the notebook path; cleanup and its rescan; `--ci`; the size caps (`over 512 KB`, `over 4096 KB`); every hook's JSON envelope; all `/prosecheck` subcommands and both spellings; stop phrases; off-mode silence; init idempotence; guard flagged and unflagged paths; show rows. Hooks were also exercised with malformed stdin (exit 0, no output).

Not verified: Windows and macOS, Python 3.9 (only Python 3.13 and Node 22 were available here), and a real host agent invoking the hooks.

## Spec disagreements

Each item says what each side claims, where it is, and what was built. Where the export marks a conflict as unsettled, the export's id is given.

### Unsettled in the export (16 ids)

1. **CF-000011: ledger retention, 20 or 50 records.**
   - Side A: `pack 14` claim N-000436 "At most the newest 20 records are kept."
   - Side B: `pack 19`/`pack 20` claim N-000729 "Each ledger keeps its newest 50 records."
   - Built: 50 (the interface contract's "global observables an implementer must reproduce").

2. **CF-000080: no-break space.**
   - Side A: `pack 05` claim N-000037 "Every no-break space becomes an ordinary space."
   - Side B: `pack 12` claim N-000307 "except a no-break space (U+00A0) or narrow no-break space (U+202F) that holds something together".
   - Built: B's exception. U+00A0 and U+202F are kept when a digit is on either side, or before `: ; ! ? » › % €`, or after `« ‹`. Other no-break spaces become U+0020. Counted as non-standard only when normalised.

3. **CF-000081, CF-000082, CF-000083: where the usage message goes.**
   - Side A: `pack 10` claim N-000098 "The usage message goes to the error stream."
   - Side B: `pack 10` N-000232 and `pack 21` N-000640 / N-000740: `--help` "prints the usage message to standard output and exits 0".
   - Built: standard output (B, three claims against one). Stderr carries nothing for help.

4. **CF-000086 and CF-000114: decisive families and the 45 floor.**
   - Side A: `pack 10` N-000134 "A decisive finding always lifts the score to at least 45, whatever the confidence."
   - Side B: `pack 10` N-000136/N-000137 "A single decisive family raises it to at least 45 only when confidence is above low."
   - Built: B. One decisive family gives 45 only at moderate or high confidence. Two or more distinct decisive families give 65 regardless of confidence.

5. **CF-000168: the stop phrase.**
   - Side A: `pack 14` N-000383 "A prompt that contains `stop prosecheck` anywhere switches the tool off."
   - Side B: `pack 15` N-000475 and `pack 31`/`pack 34` "The entire prompt ... the same words with anything else before or after them are an ordinary prompt."
   - Built: B (entire prompt only, case-insensitive, trimmed).

6. **CF-000179 and CF-000221: named transcript or newer transcript.**
   - Side A: `pack 39` N-001107 and `pack 15` N-000544 "a named transcript wins over a newer one" (interface: `transcript_path` is read).
   - Side B: `pack 39` N-001113 "When the projects folder holds a transcript newer than the named one, the newer transcript is read."
   - Built: named transcript wins when it is a readable file. The projects-folder search is used only when none is named.

7. **CF-000195 and CF-000196: trailing spaces and hard breaks.**
   - Side A: `pack 12` N-000314 "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
   - Side B: `pack 12` N-000312 "spaces and tabs at the end of every line", and N-000330 "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break."
   - Built: B (trimmed). Two-space hard breaks are removed, as N-000330 requires.

8. **CF-000210: which `utm_source` values count.**
   - Side A: `pack 10` N-000174 "Any `utm_source` parameter left in a link is an AI tracking parameter."
   - Side B: `pack 10` N-000175 "a `utm_source` whose value is exactly one of chatgpt.com, chat.openai.com, perplexity.ai, claude.ai, gemini.google.com, copilot.microsoft.com, or poe.com."
   - Built: B (the seven-host list). Other utm values do not fire family 65.

9. **CF-000211 and CF-000214: which file of several operands is scanned.**
   - Side A: `pack 10` N-000234 and `pack 21` N-000719 "the first file is scanned".
   - Side B: `pack 21` N-000739 "When several operands are given, the last one is the file scanned."
   - Built: the first operand. A stderr notice names it. The detector's `signature` section in `pack 21` states both rules in one place, so the conflict is inside the interface contract itself.

10. **CF-000219: transition clusters versus formulaic challenges.**
    - Side A: `pack 10` N-000157 "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
    - Side B: `pack 10` N-000158 "two or more sentence-opening transitions ... in one paragraph."
    - Built: B. Family 37 needs two or more sentence-opening transitions in one paragraph. A single opener does not fire 37.

### Disagreements the export did not list

11. **Ledger age: 7 days or 1 day.**
    - Side A: `pack 07` N-000068..70 "A ledger whose last modification is more than seven days old is gone by the time a later session is in use; a ledger seven days old or younger is kept." Also `pack 15` `show` rule (7 days).
    - Side B: `pack 19` config filenames "A ledger untouched for more than one day is deleted at the next session start."
    - Built: 7 days, for pruning at session start and for `show`. A 1-day deletion would break the seven-day keep rule in side A.

12. **apply_patch paths scored per payload: 16 or 10.**
    - Side A: `pack 14` "at most 16 distinct paths".
    - Side B: `pack 24` "At most ten paths of one payload are scored."
    - Built: 10 (the post-tool-use reply contract).

13. **Session-prose score line in `stats`: over 200 or over 500 characters.**
    - Side A: `pack 15` "the session-prose score is printed only when that slice ... is longer than 200 characters."
    - Side B: `pack 39` "When the scored slice is longer than 500 characters, the reply contains `session prose ai_tell_score: <score>`."
    - Built: 200 (the PRD rule). The printed line is the same either way; only the threshold differs.

14. **Decisive floor wording inside one sentence.** Covered by item 4.

15. **Heavy hedging and the score.**
    - Side A: `pack 10` N-000170 "Each sentence with stacked hedges adds to the score."
    - Side B: `pack 10` N-000116 and N-000119: hedge stacking (54) is writing advice, weight zero.
    - Built: 54 is writing advice and does not move the score. It is still reported. Per-sentence contribution is not implemented, because it contradicts the weight-zero rule.

16. **Counting rule for families versus hits.**
    - Side A: `pack 10` N-000131 "Scoring counts distinct catalogue families, not hits."
    - Side B: `pack 10` N-000170 (hedge stacking adds per sentence).
    - Built: families only (item 15 above).

## Items the spec does not state (assumptions)

- **Score formula.** The PRD fixes the floors, caps, bands, and the family rule, but not a base formula. Built: `base = min(100, 14 × distinct score-moving families)`, then single-family cap 40 (20 for sentence-length monotony alone), then decisive and short/long-document floors (`score_of` in `scripts/detect.py`).
- **Confidence wording and reasons.** Thresholds are from the PRD. Reason text is free.
- **Sentence and paragraph splitting.** Sentences end at `. ! ?` followed by space, or at line breaks. Paragraphs are split at blank lines. Used for the rhythm families and the opener and transition checks.
- **Word definition.** Runs of letters, digits, apostrophes (straight or curly), and hyphens, starting with a letter or digit.
- **Boldface overuse (56).** The PRD does not give a count. Built: three or more bold spans in prose.
- **Rule of three (7).** No detector (in the PRD's no-detector list), so not implemented.
- **Hyphenated compound list (4), promotional list (3), canonical slop list (69), persuasive tropes (22), synonym clusters (8), stock adjectives (6).** The PRD leaves lists to the implementer. The lists are in `scripts/detect.py`. Family 3 includes single words such as "leading" and "premier" because the PRD names them; this can over-fire on ordinary prose.
- **Family 1 inflections.** Simple English inflection (plural, -ed, -ing, -y→-ies) is applied to listed words.
- **Family 33 (inline-header lists).** Recognises `**Label:**` and `**Label**:` at the start of a line or list item.
- **Family 34 and 35.** Mid-essay bullets fire only when there is no markdown heading in the document. Fragmented header: next non-blank line has four or fewer words and shares a word of length three or more with the heading.
- **Family 41 (mechanical alternation).** Five consecutive alternating sentence-length differences of six or more words each, covering six sentences.
- **Family 46 (semicolon underuse).** Long documents only (300 words or more) with no semicolon and at most one open parenthesis.
- **Family 55 (contraction absence).** Needs 20 or more words, first-person share of at least 3%, and expanded forms outnumbering contractions by more than two to one.
- **Family 71 (degenerate repetition).** Six-word runs, lower-cased. Fires when at least 20% of six-word positions occur more than once.
- **Family 59 (title case).** Heading of three or more words; major words (not articles, short prepositions, or conjunctions) at least two and all capitalised; not all caps; not starting with a digit or symbol.
- **Character layer on masked text.** Pattern families run on text with code, front matter, blockquote runs, table rows, and badge lines masked (`mask_text`). Character-layer counts (62, 66, 67, 68) use the whole scan window, because the PRD does not exempt code from invisible characters in those counts. This is a choice, so the two can differ inside code blocks.
- **Invisible-character keep rules.** Implemented as the PRD lists them (`kept_invisible`). Approximate for TAG sequences and joiners beside scripts; the exact sets are the implementer's.
- **Homoglyphs.** The lookalike table covers the Cyrillic, Greek, and Armenian letters listed in the PRD. Arabic-presentation lookalikes are not included; the PRD says "Arabic-presentation lookalikes" but gives no code points.
- **Trailing-whitespace finding (68).** Fires on trailing spaces or tabs, on leading whitespace, on two or more newlines at the end, and on trailing spaces at the end of the text. A single final newline does not fire.
- **Notability (11).** Named-outlet detection is approximated as a credit verb followed by "in" or "by" and at least two capitalised names in one sentence.
- **Degenerate repetition and dash and year rules.** Implemented as the PRD states them.
- **Archive member size cap.** 64 MB uncompressed per member, to limit zip bombs (PRD: implementer's choice).
- **`--ci` interval.** Bootstrap over sentences, 200 resamples, fixed seed `20240101`. Sentence-level families only. The point score is never changed.
- **Empty-input rule for document formats.** Any extraction that yields only whitespace is empty input, and so is a PDF or RTF file.
- **Plain-text decoding.** UTF-8 with optional BOM; UTF-16 only with a BOM; undecodable bytes are replaced rather than failing.
- **Hook plugin root.** Defaults to the parent of `hooks/` (`/app`). A file under the plugin root is skipped by the guard, as the PRD says. Consequence: files saved under `/app` itself are not scored unless `CLAUDE_PLUGIN_ROOT` points elsewhere.
- **Instruction-file match.** Case-insensitive, to catch `CLAUDE.md`. The PRD says "exactly"; the lower-case list is treated as the name set.
- **Guard path forms.** Write, Edit, MultiEdit use `tool_input.file_path`; NotebookEdit uses `notebook_path` (falls back to `file_path`); apply_patch uses `command`, and lines `*** Add File:`, `*** Update File:`, `*** Move to:` name paths. A line with the same verb but no colon is not a path.
- **Failure reasons (guard and check).** Five distinct reasons: Python not found; detector timed out; output was not a report; report had no numeric score; no output or no usable result; plus a detector exit failure with its error text.
- **`check` on a non-prose extension** (for example `.py`) is scored as plain text. The guard ignores such files.
- **Stats.** Assistant rows are de-duplicated by `message.id`. The prose slice is the last 40,000 characters after removing fenced code.
- **`init` section recognition.** The section is recognised by the start marker `<!-- prosecheck-contract:start -->`. The export is portable: no machine path and no user name.
- **`status` reports the effective level** (environment word if valid, otherwise stored).
- **Default mode on first start.** The effective level is written to the flag file, so the welcome is shown once.
- **`stop prosecheck` when the level is already off.** Still stores `off` and replies. The reply names `off`.
- **Welcome and doctor text.** Wording is free where the spec allows it; the required words and numbers are present.

## Checklist accounting

`spec/CHECKLIST.md` lists 1126 ids. `spec/` is left untouched, so the accounting lives here. Every id is either implemented (the behaviour is in the file named) or listed as not done with a reason. The exceptions are listed below the table.

| Pack | Ids | Status | Where |
| --- | --- | --- | --- |
| 01 hardware requirements (no claims) | none | no node | — |
| 02 hardware summary | N-000588–592 | implemented | stdlib-only detector; Node hooks; no package |
| 03 execution profiles | N-000593–602 | implemented | `cpu_baseline`; `scripts/detect.py` run from the tree |
| 04 product overview | N-000001–018 | implemented | detector, hooks, no network code |
| 05 terminology | N-000019–040 | implemented | definitions in code; bands, hook phrases, confidence, level, scan window |
| 06 surface inventory | N-000041–051 | implemented, except N-000050–051 | detector, hooks, `commands/`, see exceptions |
| 07 non-functional constraints | N-000052–077 | implemented | stdlib; 512 KB / 4 MB; ledger age; determinism |
| 08 required substance | N-000078–081 | implemented | guard and doctor use the bundled detector |
| 09 non-goals | N-000082–093 | not done (non-goals) | see exceptions |
| 10 FP-01 detector scan | N-000094–242 | implemented | `scripts/detect.py`: report, families, bands, floors, caps, window, errors, `--ci` |
| 11 FP-02 extraction and caps | N-000243–298 | implemented | `extract_path`, zip and notebook readers, caps in guard and check |
| 12 FP-03 cleanup | N-000299–331 | implemented | `clean_text`; N-000305 and N-000309 tested in `tests/test_detect.py` |
| 13 FP-04 contract at start, prompt, subagent | N-000332–394 | implemented | `contractText`, `welcomeText`, `prosecheck-activate.js`, `prosecheck-tracker.js`, `prosecheck-subagent.js` |
| 14 FP-05 saved-file guard | N-000395–456 | implemented | `prosecheck-guard.js`, ledger |
| 15 FP-06 `/prosecheck` commands | N-000457–577 | implemented | `prosecheck-commands.js`, `commands/prosecheck.md` |
| 16 cross-cutting obligations | N-000578–587 | implemented | no network code; `README.md` not-authorship text |
| 17 interface overview | N-000603–626 | implemented | product overview, layout (detector by path, hooks by Node) |
| 18 public surface shape | N-000627–673 | implemented | `hooks/hooks.json` events; detector switches; `commands/`; `.cursor/rules/` |
| 19 naming conventions | N-000674–702 | implemented | file names, bands, level words, env vars, config filenames |
| 20 global observables | N-000703–730 | implemented | exit codes 0/1/2; error objects; report shape; ledger; hooks exit 0 |
| 21 `scripts/detect.py` | N-000731–787 | implemented | signature, report, metrics, cleanup output, errors, several operands |
| 22 `prosecheck-activate.js` | N-000788–812 | implemented | welcome, contract, off silence |
| 23 `prosecheck-subagent.js` | N-000813–818 | implemented | SubagentStart envelope |
| 24 post-tool-use reply | N-000819–835 | implemented | `prosecheck-guard.js` envelope and line format |
| 25 `content` | N-000836–840 | implemented | `tool_input.content` is accepted beside `file_path`; the guard scores the saved file at the path, not the string |
| 26 `cwd` | N-000841–843 | implemented | top-level `cwd` resolves relative `file_path` |
| 27 `file_path` | N-000844–846 | implemented | `tool_input.file_path` |
| 28 `prompt` and `session_id` | N-000847–856 | implemented | tracker reads both; ledgers per session |
| 29 `tool_input` | N-000857–863 | implemented | `command` for apply_patch, `notebook_path` for NotebookEdit |
| 30 `tool_name` | N-000864–869 | implemented | Write, apply_patch, and the others in `hooks.json` matcher |
| 31 `/prosecheck` router | N-000870–908 | implemented | `prosecheck-commands.js` `route` |
| 32 `help` | N-000909–934 | implemented | `helpReply` |
| 33 `status` | N-000935–941 | implemented | `Current level:` one line |
| 34 level words and `on` | N-000942–951 | implemented | `writeMode`, `on` stores `full` |
| 35 `check` | N-000952–992 | implemented | `checkReply`, quotes and `@` stripped, reply lines |
| 36 `doctor` | N-000993–1028 | implemented | `doctorReply`, four check lines and closers |
| 37 `show` | N-001029–1060 | implemented | `showReply`, row shapes, empty ledger |
| 38 `init` | N-001061–1102 | implemented | `initReply`, AGENTS.md section, Cursor rule, off-mode |
| 39 `stats` | N-001103–1121 | implemented | `statsReply`, `prosecheck-stats.js` |
| 40 `transcript_path` | N-001122–1126 | implemented | named transcript read by stats |

Decision-type ids (N-000130, N-000183, N-000213, N-000225) are choices the spec leaves open; they are recorded under "Items the spec does not state" above (label wording, compound list, full list, resampling).

Exceptions (listed as not done, with reasons):

- **Pack 09, N-000082–093 (non-goals).** These are exclusions, so nothing is built for them: no authorship classifier, no PDF or RTF reading, no shell-written file scoring, no website, no third-party detector use, no in-place rewrite of documents, no rewrite instructions in the detector, and no demo, documentation checker, evaluation script, or status-line helper.
- **Pack 06, N-000050–051 (bundled skill file).** The PRD says the skill's rewrite instructions are the host agent's job and not a feature point. No skill file is shipped. The detector path fallback to `skills/prosecheck/scripts/detect.py` is implemented, so a shipped skill would be found.
- **Pack 19 and 20, the 1-day ledger rule.** Not implemented, because it conflicts with the seven-day rule (item 11 above).
- **Pack 10, the Arabic-presentation homoglyph list.** Partial: the PRD gives no code points; see the homoglyph assumption above.
- **Pack 10 and 15, the family rule for "comprehensive" and "boast".** Kept on the banned list in the contract. Per the PRD they are enforced only in context (self-thoroughness, copula avoidance), which those families already cover.
- **Pack 12 and 16, no-break space in the user-visible wording.** Implemented as the exception in item 2.
- **Pack 40 and 39, `show` label cap and check cap.** Implemented at 5 (show, guard) and 8 (check), as the PRD says; no unstated cap is added.

## Other notes

- The guard skips any file under the plugin root. In this checkout the plugin root is `/app`, so files saved under `/app` (outside `node_modules` and `.git`) are not scored. Set `CLAUDE_PLUGIN_ROOT` to move the root, or save prose elsewhere.
- The Node hooks use only `fs`, `os`, `path`, and `child_process`. The detector uses only the standard library.
- Score ranges have not been calibrated against any corpus. The PRD says the score is a triage heuristic; the numbers here are the ones the rules produce.

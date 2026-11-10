# prosecheck: implementation notes

Layout built from the spec (`spec/` is unchanged):

- `scripts/detect.py`: the detector (Python 3.9+, standard library only).
- `hooks/prosecheck-activate.js` (session start), `hooks/prosecheck-tracker.js` (prompt submit and `/prosecheck` router),
  `hooks/prosecheck-subagent.js` (subagent start), `hooks/prosecheck-guard.js` (post tool use),
  `hooks/prosecheck-stats.js` (stats; also called by the router). Shared code: `hooks/lib/prosecheck-common.js`.
- `hooks/hooks.json`: host registration for the four events. `commands/prosecheck.md`: the menu document
  (body `/prosecheck $ARGUMENTS`). `.cursor/rules/prosecheck.mdc`: the shipped Cursor rule.
  `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`: manifest and rewrite guidance for the host.

Plugin root is the repository root (the directory that contains `hooks/`), unless `CLAUDE_PLUGIN_ROOT` is set.

Spec conflicts are listed in the order of `spec/RULINGS.md`. Every ruling was followed. Where a
ruling settles a conflict, the other side is quoted too.

## Spec conflicts and what was built

1. **Where the usage message goes.** PRD FP-01 "Public entry" (lines 82–83) says the usage message goes to the error
   stream; PRD FP-01 "Boundary / error behavior" (line 167) says help prints usage to standard output and succeeds.
   *Built:* `--help`/`-h` print usage to stdout and exit 0 (ruling 1). Usage errors (unknown option) go to stderr.

2. **Floor for a single decisive finding.** PRD FP-01 "Normal behavior" line 93 says a decisive finding always lifts the
   score to at least 45. Line 94 says a single decisive family at `none` or `low` confidence does not take that floor.
   *Built:* 45 always (ruling 2). Two or more distinct decisive families give 65.

3. **Hedge stacking changes the score?** PRD line 90 (writing advice, weight zero) against line 128 ("Each sentence with
   stacked hedges adds to the score"). *Built:* weight zero (ruling 3). Catalogue 54 is reported but never scores.

4. **Tailing-negation form of catalogue 17.** PRD line 91 says it is score-moving; IC `scripts/detect.py` > Findings
   (line 148) says both forms are weight zero. *Built:* both forms weight zero (ruling 4). Keys are
   `17_negative_parallelism` and `17_tailing_negation`. Consequence: the PRD's "50 score-moving numbers" becomes 49
   in practice, because 17 no longer moves the score.

5. **No-break spaces.** PRD Terminology line 30 says every no-break space becomes an ordinary space; FP-03 line 212
   keeps a no-break space that holds something together. *Built:* kept when a digit is on either side, before
   `:` `;` `!` `?` `»` `›` `%` `€`, or after `«` `‹` (ruling 5). Other spaces of category Zs become U+0020.
   The rule is shared by counting and cleanup.

6. **Markdown hard break.** PRD FP-03 line 214 keeps two trailing spaces that end a line of prose; line 223 says
   removing them is required. *Built:* kept (ruling 6). Such lines are not flagged under 68 either, so detection and
   cleanup agree.

7. **Catalogue 65 and `utm_source`.** PRD line 131 (any `utm_source` value) against line 132 (only the whole listed
   host). *Built:* only the whole host (ruling 7).

8. **`stop prosecheck` anywhere.** PRD FP-04 line 240 (anywhere) against FP-06 line 285 and IC line 411 (entire prompt).
   *Built:* `stop prosecheck` anywhere in a prompt stores `off` (ruling 8). The entire prompt `stop prosecheck` or
   `prosecheck off` also gets a block reply that names `off`. When the phrase is inside a longer prompt, the
   prompt is not blocked; the level is now off, so the hook emits nothing for it.

9. **`PROSECHECK_DEFAULT_MODE` precedence.** PRD FP-04 line 246 applies the environment level only when nothing valid is
   stored; IC line 63 says the variable takes precedence. *Built:* a valid stored level wins (ruling 9).

10. **`.pdf` as a prose file.** PRD line 27 and line 195 say `.pdf` is not a prose file; line 290 and IC line 582 name
    `.pdf` deliverables in the wording. *Built:* `.pdf` is not prose; the wording stays as written (ruling 10).

11. **How many file operands.** IC line 21 ("at most one file operand") against IC line 180 and PRD line 168 (two or
    more succeed). *Built:* two or more succeed (ruling 11).

12. **Which operand is scanned.** IC line 106 says the last; IC line 180 and PRD line 168 say the first.
    *Built:* the last operand is scanned (ruling 12). The stderr notice names the scanned file and also contains the first
    operand exactly as given, which satisfies IC line 180's notice requirement.

13. **Maximum `apply_patch` paths.** PRD FP-05 line 264 says 16; IC line 260 says ten. *Built:* 16 (ruling 13).

14. **Records per ledger.** PRD FP-05 line 265 says the newest 20; IC line 91 says 50. *Built:* 50 (ruling 14).

15. **How long a ledger is kept.** PRD line 57 says seven days; IC line 65 says one day. *Built:* seven days
    (ruling 15). Session start deletes ledgers whose last modification is over seven days old. `show` also ignores them.

16. **Which transcript `stats` reads.** PRD FP-06 line 292 says a named transcript wins; IC line 650 says the newer one
    is read when `projects` holds one. *Built:* the newer transcript is read when it is newer than the named one
    (ruling 16). A named transcript that cannot be read gives the no-counts reply; there is no fallback.

17. **Minimum slice length for the session-prose score.** PRD FP-06 line 292 says 200 characters; IC line 662 says 500.
    *Built:* 200 (ruling 17).

Two conflicts were not in `RULINGS.md`:

18. **Family 2 threshold.** PRD FP-01 lists the model-dialect words with no count, but FP-04 line 236 says that family
    "needs two hits". *Built:* family 2 fires only with two or more hits.

19. **`ai_tell_score` cap rules and `score_ci` language.** The PRD gives the floors and caps, but no scoring formula,
    and IC line 160 talks about "a resampled interval" while PRD line 160 leaves the method to the implementer. *Built:*
    see "Choices" below.

## Choices and assumptions the spec does not state

Scoring:
- Score = sum of family weights, one weight per distinct score-moving family (10 normally, 16 for a decisive family,
  6 for the rhythm kinds 40 and 44). Hit counts do not change the score, following "scoring counts distinct catalogue
  families, not hits". Then the caps (single family or rhythm-only, and the clean-only case for 40 alone) and the
  floors (decisive, short-document, long-document) are applied, as PRD FP-01 lines 93–96 describe.
- Confidence: `none` under 40 words, `low` under 120 words or under 300 with one family, `moderate` under 300, `high`
  otherwise. The reason text is free.
- `--ci`: the interval is the score plus or minus a spread set by confidence (15, 12, 8, or 5). It is not a resampling
  and is labelled as a rough guide in `score_ci_note`. It is `null` with fewer than four sentences.
- Words are runs of letters, digits, apostrophes, and hyphens. Sentences are split at `.`, `!`, `?`, `…`, and line breaks.

Catalogue:
- Families are regular expressions over lists that the PRD leaves open ("the full list is the implementer's choice"):
  the hyphenated-compound list (4), the stock-adjective list (6), the synonym clusters beyond the eight given,
  the canonical marketing phrases (69), and the placeholder rules (63). Where the PRD lists a family's examples,
  those examples are included.
- Family 3 uses a narrow form for "leading" ("leading provider/brand/company/firm/platform/name"). Bare "leading" is
  common English.
- Family 37 needs two or more sentence-opening transitions in one paragraph (the definition), even though the family-36
  note says a single transition opener "already fires" it.
- Family 40 (sentence-length monotony) and 44 (uniform paragraph length) fire once, with the whole document or
  all paragraphs as their spans.
- Family 55 needs at least three first-person words and at least 3% first-person share, and at least three full
  forms with at least 80% of the contractible forms written out.
- Family 71 fires when at least 20% of six-word runs repeat within the document.
- Homoglyphs: the lookalike table covers Cyrillic, Greek, and Armenian letters for the letters the PRD names. The PRD
  also mentions Arabic-presentation lookalikes but gives no list, so none are mapped.
- Masked regions (fenced code, inline code, blockquote runs of two or more lines, table rows, badge lines, YAML front
  matter) generate no findings and are excluded from the pattern families and from the character-layer findings
  (62, 66, 67, 68). Metrics and confidence use the masked text, too.
- Character-layer counts (`invisible_chars`, `nonstandard_spaces`, `homoglyphs`) follow the same exclusions.

Character cleanup:
- Positions kept for invisible characters follow the list in PRD FP-03 line 211. A TAG character is kept only inside a
  black-flag sequence. The bidi controls are kept only when the document contains right-to-left script.
- Cleanup works on the whole extracted text, not just the scan window. Invisible characters inside code blocks are
  removed too, as the scrub is not a finding. Line ends are kept as they are (CR is not invisible).

Extraction:
- Archive members are read up to 64 MB uncompressed. Larger members are skipped.
- Notebook: a markdown cell with a source that is not a string or list of strings makes the whole notebook empty.
- EPUB: the spine order from the OPF is used, with nav documents excluded. Head, script, style, and nav content is dropped.
- XLSX: sheets are read in numeric file order (not the workbook's sheet order), and cells are joined with line breaks.

Hooks and commands:
- Session start writes the effective level to `.prosecheck-active` when no flag exists. The welcome is shown on that same
  start, so it is shown once.
- The effective level is the stored level if valid, otherwise `PROSECHECK_DEFAULT_MODE` if valid, otherwise `full`.
- Ledger file: `.prosecheck-ledger-<session id>` when the id is a safe token, otherwise a hash of it. Records hold base
  names, scores, bands, labels, and flags. They never hold document text or paths.
- Guard: `off` or `lite` emits nothing and records nothing. `.pdf` and `.rtf` are recorded as binary. Files under
  `node_modules`, `.git`, the plugin install tree, or with an instruction-file name (case-insensitive) are skipped
  without a record. A missing path is recorded as an unreadable failure only when its extension is eligible.
- Guard labels: score-moving labels come first, then the weight-zero ones, both in the nudge and in `check`.
- Doctor: the Python check runs the detector on a short fixed sentence. A numeric score is the success condition.
- Stats: turns and tokens are counted per message `id` (rows that repeat a message id count once; their usage is taken
  once). Text from every assistant row is used. The session-prose score is printed only above 200 characters.
- Init: `AGENTS.md` is recognised by the start marker `<!-- prosecheck:contract:start -->`, or by the heading
  `## Prose contract (prosecheck)`. The Cursor rule is copied from `<plugin root>/.cursor/rules/prosecheck.mdc`.
- Show: the reply is newest first. Size-skip rows say `over 512 KB` for plain text and `over 4096 KB` for archives and
  notebooks.

## Behaviour to be aware of

- Files inside the plugin install tree are never scored (spec FP-05, and `CLAUDE_PLUGIN_ROOT`). When the repository
  root is `/app`, a file saved under `/app` gets no nudge.
- `check` treats an unknown extension as plain text, as the detector does.
- The guard's per-file detector timeout is 8 seconds for plain text and 15 seconds for archives and notebooks.

## What is not verified

- No real host (Claude Code, Codex, Cursor) was run. The hooks were run directly with JSON on standard input,
  with `CLAUDE_CONFIG_DIR` pointed at a temporary folder.
- Only Linux with Python 3.13 and Node 22 was tested. macOS and Windows were not tested.
- The pattern lists are a good-faith reading of the PRD, not a reference implementation. The exact list membership
  of the implementer-chosen families (see "Catalogue") is a choice and may differ from any reference.
- The `--ci` interval is a heuristic, not a resampling.
- The bundled skill is a short placeholder for the host agent's rewrite instructions.

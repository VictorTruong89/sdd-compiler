# NOTES

Layout: `scripts/detect.py` (detector), `hooks/*.js` (Node hooks, shared code in `hooks/prosecheck-lib.js`),
`install/prosecheck-command.md` and `commands/prosecheck.md` (menu document, body `/prosecheck $ARGUMENTS`),
`.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`.

## Conflicts in the specification and what I built

1. **Usage message stream.** PRD FP-01 "Public entry" says usage goes to the error stream; PRD FP-01 "Boundary" and
   IC `scripts/detect.py` > Usage say `--help`/`-h` print it to standard output, exit 0. Built: stdout, exit 0.
2. **Single decisive floor.** PRD FP-01 says a decisive finding "always lifts the score to at least 45, whatever the
   confidence"; the next bullet says a single decisive family at `none`/`low` confidence "does not take that 45 floor".
   Built: single decisive family gets the 45 floor only above `low` confidence; two distinct decisive families get 65.
3. **Hedge stacking (54).** PRD lists it as weight-zero writing advice; the family rule says each stacked-hedge sentence
   "adds to the score". Built: weight zero (reported, never moves the score).
4. **Tailing negation (17).** PRD FP-01: tailing-negation form is score-moving; IC: both forms weight zero. Built: PRD
   (tailing form `17_tailing_negation` moves the score; `17_negative_parallelism` is weight zero).
5. **No-break spaces.** Terminology says every NBSP becomes a space; FP-03 keeps the load-bearing ones (digit neighbour,
   before `: ; ! ? » › % €`, after `« ‹`). Built: FP-03 rule; kept ones are not counted.
6. **Hard-break trailing spaces.** FP-03 "What is trimmed" keeps two trailing spaces; FP-03 "Boundary" says removal is
   required. Built: trailing spaces/tabs are always removed.
7. **Zero-width characters.** FP-01 says any zero-width char in text is invisible; FP-03 keeps some in position and says
   kept ones are not counted. Built: FP-03 positional rules, detection and cleanup share one function.
8. **`utm_source`.** FP-01 line "Any utm_source ... is an AI tracking parameter" vs the 65 rule (only the seven listed
   hosts). Built: only the listed hosts fire 65.
9. **`stop prosecheck`.** FP-04 says "contains ... anywhere"; FP-06 and IC say the entire prompt only. Built: entire
   prompt (case-insensitive) for `stop prosecheck` and `prosecheck off`.
10. **`PROSECHECK_DEFAULT_MODE`.** PRD FP-04: environment used only when nothing valid is stored; IC: environment takes
    precedence over the stored level. Built: stored valid level wins; env applies when nothing valid is stored.
11. **`.pdf`.** Empty-ledger text mentions `.pdf` deliverables although `.pdf` is not a prose format. Built: `.pdf`/`.rtf`
    are not scored, get a "binary ... not re-scored" ledger row; the empty-ledger reply still mentions `.docx` and `.pdf`.
12. **How many operands.** IC "at most one file operand" vs "two or more still succeed". Built: two or more succeed.
13. **Which operand.** IC Signature "the last one is scanned" vs IC Several-operands/PRD "the first". Built: first, with a
    stderr notice line naming it.
14. **apply_patch path cap.** PRD 16, IC ten. Built: 16.
15. **Ledger records.** PRD 20, IC 50. Built: 20.
16. **Ledger age.** PRD seven days, IC one day. Built: seven days (pruned at session start, ignored by `show` when older).
17. **`stats` transcript.** PRD "named transcript wins over a newer one"; IC "newer one is read". Built: named wins.
18. **Session-prose slice.** PRD longer than 200 characters; IC 500. Built: 200.
19. **Model-dialect "needs two hits".** Said only in PRD FP-04; the FP-01 family rule has no such condition. Built: one
    hit fires family 2 (a single hit never decides a band: a single family caps at 40).
20. **Welcome vs "never name prosecheck".** Built: the welcome (first start only) names prosecheck; the contract itself
    tells the agent never to name it.
21. **Transition words (36/37).** The 36 entry ends "A single sentence that opens with one of the transition words
    already fires transition clusters", while 37 requires two or more in one paragraph. Built: two or more per paragraph.
22. **False ranges (15) vs numeric spans.** 61 says "from 9 to 5" is a false range (15) but 15's rule says "only the
    rhetorical sweep". Built: rhetorical sweep only; numeric spans in words do not fire.

## Not stated; assumptions

- **Score formula, band weights.** Not given. Each score-moving family adds 14 (decisive 22, rhythm kinds 8) plus 3 per
  extra hit (max +12); capped at 100, then caps/floors from the PRD are applied (single family <= 40; monotony alone <= 20;
  rhythm-only <= 40; decisive floors 45/65; short-doc floors 25/45; long-doc floors 25/45).
- **Lists the PRD leaves to the implementer** (hyphenated pairs 4, marketing slop 69) use my own lists.
- **Heuristic thresholds** where the PRD says "short", "almost no", "noticeable", "on the order of": fragmented header tail
  <= 5 words; 46 fires with at most one parenthetical; 55 needs first-person share >= 2% and >= 3 full forms outnumbering
  contractions; 71 needs >= 20% of six-word runs repeated and >= 6 of them; 41 needs 6+ strictly alternating sentences with
  mean step >= 5 and min step >= 3; 70 needs >= 24 lines.
- **Homoglyph count** is the number of lookalike characters; the Arabic-presentation lookalikes are not mapped.
- **Zl/Zp** (U+2028/2029) count as non-standard spaces and become line feeds.
- **Paragraph separators in extracted documents**: docx/odt/odp paragraphs and epub blocks are joined with a blank line,
  xlsx/ods cells with a single newline, so a document scores like its plain-text version.
- **Masking** of code/quote/table/badge/front-matter regions also applies to the character-layer findings (they are
  ignored there); `--clean` operates on the whole text regardless.
- **`check` on an unsupported extension** is scored as plain text (512 KB cap).
- **Doctor with python present but detector missing** reports the Python check as faulty without "python not found".
- **NotebookEdit with only `file_path`** is scored. A patch line without a colon names no path. `Delete File` is ignored.
- **Stats** de-duplicates assistant rows by message `id` (last usage wins) and counts rows without an id individually.
- **Ledger file**: `.prosecheck-ledger-<sanitized session id>`, or `.prosecheck-ledger` when no session id is given.
- Level flag is written at the first session start (resolved level, including env or default), which ends the welcome.

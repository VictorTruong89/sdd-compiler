# NOTES

Layout: `scripts/detect.py` (detector), `hooks/prosecheck-*.js` (self-contained generated hooks; sources and
`build.sh` in `hooksrc/`), `commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents, body
`/prosecheck $ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`,
`.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`. No build step is needed; `hooksrc/build.sh` only regenerates the hooks.

## Disagreements in the specification and what I built

1. **Where usage goes.** PRD FP-01 "Public entry": "The usage message goes to the error stream". PRD FP-01 "Boundary": help "prints the usage message to standard output and succeeds" (IC `--help` agrees). Built: `--help`/`-h` print usage to stdout, exit 0.
2. **Floor for one decisive finding.** PRD FP-01 says a decisive finding "always lifts the score to at least 45, whatever the confidence", and the next bullet says a single decisive family at `none`/`low` confidence "does not take that 45 floor". Built the specific rule: one decisive family gets the 45 floor only at `moderate`/`high` confidence (and is capped at 40 below that); two decisive families give at least 65.
3. **Hedge stacking (54).** Writing-advice list says weight zero; the family rule says "adds to the score". Built: weight zero (reported only).
4. **Tailing negation of 17.** PRD: score-moving; IC detect.py Findings: "Both forms ... weight zero". Built the PRD: `17_tailing_negation` moves the score, `17_negative_parallelism` is weight zero.
5. **No-break space.** Terminology says every no-break space becomes U+0020; FP-03 keeps some (digit neighbour, before `: ; ! ? » › % €`, after `« ‹`). Built the FP-03 exceptions.
6. **Markdown hard break.** FP-03 "trimmed" keeps two trailing spaces; FP-03 "Boundary" says the collapse is required. Built: trailing spaces/tabs are always removed.
7. **Zero-width characters.** FP-01 says every zero-width character inside text is invisible; FP-03/62 keep some in position. Built: positional exceptions of FP-03 apply to both detection and cleanup.
8. **`utm_source`.** FP-01 (64) says any `utm_source` is a tracking parameter; (65) says only the listed hosts. Built (65): only the seven listed hosts, whole host name.
9. **`stop prosecheck`.** FP-04 says "anywhere in the prompt"; FP-06 and IC say the entire prompt. Built: entire prompt only (case-insensitive), also `prosecheck off`.
10. **`PROSECHECK_DEFAULT_MODE`.** FP-04: used only when nothing valid is stored; IC Naming: "takes precedence over the stored level". Built the PRD: a valid stored level wins, the variable fills in when nothing valid is stored.
11. **`.pdf` as a prose file.** `show`'s empty-ledger text mentions ".docx and .pdf deliverables" although `.pdf` is not one of the twenty formats. Built: the text is kept verbatim (IC requires `.pdf` in it); `.pdf`/`.rtf` are logged as binary and never scored.
12. **Number of file operands.** IC says "at most one file operand"; IC/PRD also say two or more still succeed. Built: extra operands are accepted.
13. **Which operand.** IC Signature says the last; IC "Several file operands" and PRD say the first. Built: the first is scanned, stderr notes it.
14. **apply_patch path cap.** PRD 16, IC ten. Built 16.
15. **Ledger size.** PRD 20, IC 50. Built 20 newest.
16. **Ledger age.** PRD seven days, IC one day. Built seven days (deleted at session start and ignored by `show`/the guard when older).
17. **Named vs newer transcript in `stats`.** PRD: the named one wins; IC `stats` Transcript rows: a newer one under `projects` is read. Built: the named `transcript_path` wins.
18. **Session-prose score slice length.** PRD longer than 200 characters; IC 500. Built 200.
19. **Model-dialect words.** FP-04 says "needs two hits"; FP-01 (2) has no such condition while FP-04 also says every banned word fires. Built: one hit fires family 2.
20. **Welcome vs "never name prosecheck".** The contract tells the agent to stay silent; the welcome names the product. Built: the welcome is a separate block (printed first, once); the contract text itself never names the product.

## Things the specification does not state, and what I assumed

- **Score arithmetic.** No weights are given. Each score-moving family adds 10 points (25 if decisive, 8 for 40/44) plus 2 per extra hit (max +16); caps and floors from FP-01 are applied after. Bands from the score.
- **Transition clusters (37) vs the sentence in 36** ("a single sentence that opens with a transition ... already fires"): I used the explicit rule, two or more sentence-opening transitions in one paragraph.
- **Extraction separators.** docx/pptx/xlsx/odf/epub paragraphs, slides, cells and chapters are joined with a single newline; notebook markdown cells with a blank line. Ends are stripped.
- **Homoglyph counts** count lookalike characters; the homoglyph test is applied per letter run. Lookalike table covers the Cyrillic, Greek, Armenian and a few Arabic letters.
- **Character-layer findings (62, 66, 67, 68)** are computed on the raw window, not on text masked for code/quotes/tables; all other families use the masked text.
- **Word-count source** for confidence and floors is the masked text (prose, not code).
- **Resampled interval**: 5th–95th percentile of up to 40 sentence resamples (fixed seed), widened to contain the point score.
- **Stock lists left to the implementer** (hyphenated compounds, marketing-slop phrases, stock adjectives) are my own lists.
- **Guard**: tool names are compared loosely (case, underscores); unknown tools are ignored. A `NotebookEdit` with only `file_path` is scored. A patch line without a colon names no path. Failed-check reasons: "Python not found", "detector output was not a structured report", "report had no numeric score", "detector timed out", "detector produced no usable result", and "the file could not be read" for unreadable files.
- **Ledger file** is `.prosecheck-ledger-<sanitised session id>` (or `.prosecheck-ledger` with no id), a JSON array; records carry base names only.
- **Help/other reply wording** is mine except where the Interface Contract fixes it. `stats` de-duplicates assistant rows by message id (last row wins) so streaming rows are not double counted.
- **`init`** treats `<!-- prosecheck:begin -->` as the section marker. If the shipped Cursor rule is missing under the plugin root, an embedded copy of the same rule is written.
- **Detector read errors** for directories and missing files use `cannot read input:`; `.pdf`/`.rtf` give `empty input` once the file has been read.

# NOTES

Layout: `scripts/detect.py` (Python 3.9+ stdlib detector), `hooks/*.js` (Node, stdlib only; `prosecheck-lib.js` is shared),
`commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents, body `/prosecheck $ARGUMENTS`),
`.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`.
No tests are shipped; I exercised the hooks and detector by hand.

## Disagreements in the specification, and what I built

| Topic | Side A | Side B | Built |
|---|---|---|---|
| Usage stream (CF-000081/82/83) | FP-01 (pack 10, N-000098): "The usage message goes to the error stream" | Interface Contract `scripts/detect.py` and FP-01 help bullet: `--help`/`-h` "write the usage message to standard output and exit 0" | stdout, exit 0. First line exactly `usage: detect.py [--clean] [--ci] [--] [FILE]`. |
| Several file operands (CF-000211/214) | FP-01 and contract "Several file operands": "the first file is scanned" and stderr notice names the first operand | Contract Signature paragraph (N-000739): "the last one is the file scanned" | First operand scanned; stderr notice line names it (not JSON). |
| Single decisive family at none/low confidence (CF-000086/114) | N-000134: a decisive finding "always lifts the score to at least 45, whatever the confidence" | N-000136/137: a single decisive family reaches 45 only when confidence is above `low` | B: single decisive family gets the 45 floor only at `moderate`/`high`; two decisive families get at least 65 at any confidence. |
| `utm_source` (CF-000210) | N-000174: "Any `utm_source` parameter left in a link is an AI tracking parameter" | N-000175: only the seven listed hosts | B: only the seven listed hosts, whole host name. |
| Transition clusters (CF-000219) | N-000157: one sentence opening with a transition "already fires" 37 | N-000158: two or more sentence-opening transitions in one paragraph | B: two or more in one paragraph. |
| Non-breaking spaces (CF-000080) | Terminology: "Every no-break space becomes an ordinary space" | FP-03: NBSP/NNBSP kept beside digits, before `: ; ! ? » › % €`, after `« ‹` | FP-03 exceptions apply (kept, not counted). All other non-standard spaces become U+0020. |
| Trailing double space (CF-000195/196) | FP-03 N-000314: two trailing spaces that end prose are a hard break and are kept | N-000312 "spaces and tabs at the end of every line" and N-000330 "removed even when two spaces were meant as a hard break … required" | Removed on every line. |
| Stop phrase (CF-000168) | FP-04 N-000383: a prompt containing `stop prosecheck` anywhere switches off | FP-06 N-000475 and contract: only the entire prompt (`stop prosecheck` / `prosecheck off`, any case) | Entire prompt only; otherwise an ordinary prompt. |
| Ledger length (CF-000011) | FP-05: newest 20 records | Contract global observables: newest 50 | 20. |
| Named vs newer transcript (CF-000179/221) | FP-06: a named transcript wins over a newer one | Contract `stats`: "the newer transcript is read" | Named `transcript_path` wins. If it is absent, the newest `.jsonl` under `<config>/projects` is used. A named path that cannot be read gives the no-transcript reply (no fallback). |
| Ledger age | Non-functional constraints / FP-06: >7 days old is gone, ≤7 kept | Contract Config filenames: "untouched for more than one day is deleted at the next session start" | 7 days (delete at session start; `show` ignores older ledgers too). |
| Patch paths per payload | FP-05: at most 16 distinct paths | Contract post-tool-use reply: at most ten paths scored | 10 (satisfies both as an upper bound). |
| Stats prose threshold | FP-06: slice longer than 200 characters | Contract `stats`: longer than 500 | 500. |
| Catalogue 17 weight | FP-01: tailing-negation form is score-moving (and "50 score-moving" counts 17) | Contract `detect.py`: "Both forms of catalogue 17 are writing advice and carry weight zero" | Weight zero for both forms; keys `17_negative_parallelism` and `17_tailing_negation`. |
| `PROSECHECK_DEFAULT_MODE` | Contract Host environment: when set it "takes precedence over the stored level" | FP-04: env is used only when nothing valid is stored | FP-04: a valid stored level wins; env is the default when nothing valid is stored. Invalid env values are ignored. |
| Label caps | Not conflicting | – | guard nudge 5, `check` 8, `show` 5 (PRD figures). |

## Unstated details and my assumptions

- **Score formula.** Not given. Each score-moving family adds 9 plus up to 6 for hit count; then the stated caps and floors apply (single family at most 40, monotony alone at most 20, rhythm-only at most 40, decisive floors, short and long document family-count floors). Writing-advice numbers (4, 17, 19, 22, 41, 42, 46, 54, 55, 58, 60, 61, 68) never move it.
- **Family 2 (model-dialect)** fires only on two or more hits (FP-04). A lone dialect word therefore does not fire.
- **Confidence** with zero fired families at 120–299 words is `moderate` (the "low" rule says "only one family").
- **Lists left to the implementer** (hyphenated compounds 4, marketing slop 69, homoglyph map, stock adjectives) are my own short lists.
- **Interval (`--ci`).** 40 bootstrap resamples of sentences (10 for very long texts), fixed seed 1234; the interval is widened to include the point score.
- **Docx/pptx/xlsx/odf/epub/ipynb** join paragraphs, slides, cells and chapters with a single `\n`; result is stripped. Paragraph-level rules (44, 42, 37, 58) therefore see one paragraph for such files unless the source holds blank lines.
- **Window.** Character-layer findings (62, 66, 67, 68) are counted on the raw window including code regions; lexical rules run on the window with code, quotes, tables, badges and front matter blanked.
- **Cleanup** runs on the whole input (not just the window). Restores a single trailing line ending (CRLF if the input ended in CRLF). Leading blank lines are removed; leading spaces on the first text line are kept.
- **Guard.** Instruction-file names are matched case-insensitively (`CLAUDE.md` is skipped). A line `*** Add File` with no colon names no path. A NotebookEdit carrying only `file_path` is scored. The guard skips unsupported tools. Failure reasons: `python not found`, `detector printed text that is not a structured report`, `report had no numeric score`, `detector timed out`, `detector produced no output or no usable result` (also used for a non-zero exit and for empty prose). An unreadable path is `file not readable`.
- **Plugin install tree skip** uses the plugin root (`CLAUDE_PLUGIN_ROOT` or the directory above `hooks/`); with the variable unset, files under `/app` are skipped by the guard.
- **`check`** on an extension outside the twenty formats (and not pdf/rtf) is scored as plain text under the 512 KB cap. Relative paths resolve against the payload `cwd` if present, else the process directory.
- **Welcome.** Shown when `.prosecheck-active` does not exist; session start then stores the effective level (not when that level is `off`).
- **`init`.** Section is recognised by the heading line `## Prose contract (prosecheck)`; it is wrapped in HTML comment markers that are not required for recognition. Uses the process working directory.
- **Exit codes.** Detector internal errors map to exit 1 with `cannot read input:` JSON; hooks always exit 0.
- **Help text** of `--help` after the first line is mine.

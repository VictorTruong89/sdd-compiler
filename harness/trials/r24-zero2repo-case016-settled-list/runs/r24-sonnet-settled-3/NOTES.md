# NOTES

Layout: `scripts/detect.py` (Python stdlib detector), `hooks/*.js` (Node hooks, shared `hooks/lib.js`),
`commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents forwarding `$ARGUMENTS`),
`.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`.

## Spec disagreements and what was built
All 17 entries of `spec/RULINGS.md` were followed as ruled:

1. Usage: PRD FP-01 line 82 says usage goes to the error stream; line 167 says help goes to stdout. Built: `--help`/`-h` print to stdout, exit 0; usage errors go to stderr.
2. Decisive floor: PRD line 93 "always at least 45" vs line 94 "no floor at none/low confidence". Built: always at least 45.
3. Hedge stacking (54): PRD line 90 weight zero vs line 128 "adds to the score". Built: weight zero.
4. Catalogue 17 tailing-negation: PRD line 91 score-moving vs IC line 148 weight zero. Built: both forms weight zero (`17_negative_parallelism`, `17_tailing_negation`).
5. No-break spaces: Terminology "every NBSP becomes a space" vs FP-03 keep rules. Built: keep the FP-03 positions (digit either side, before `: ; ! ? » › % €`, after `« ‹`); others become U+0020.
6. Hard break: FP-03 line 214 keeps two trailing spaces vs line 223 removes. Built: exactly two trailing spaces on a prose line are kept (not on the final line of the text).
7. `utm_source`: PRD line 131 any value vs line 132 listed hosts. Built: only the listed AI hosts.
8. `stop prosecheck`: FP-04 anywhere vs FP-06/IC entire prompt. Built: anywhere in a non-command prompt switches off. `prosecheck off` only as the entire prompt.
9. `PROSECHECK_DEFAULT_MODE`: PRD line 246 only when nothing valid is stored vs IC line 63 takes precedence. Built: a valid stored level wins; env used only otherwise.
10. `.pdf`: FP-06 line 290 / IC empty-ledger wording mention `.pdf` deliverables vs FP-02 not prose. Built: `.pdf`/`.rtf` are not prose (guard records them as binary, detector gives empty input); the empty-ledger reply keeps the ".docx and .pdf" wording.
11. File operand count: IC line 21 "at most one" vs line 180 / PRD line 168 accept more. Built: any number accepted.
12. Which operand: IC line 106 last vs line 180 / PRD first. Built: the last is scanned. The stderr notice names the last (scanned) file and also the first operand exactly as given.
13. apply_patch paths: PRD 16 vs IC ten. Built: 16.
14. Ledger records: PRD 20 vs IC 50. Built: 50.
15. Ledger age: PRD seven days vs IC one day. Built: seven days (purged at session start, and ignored/removed on read).
16. `stats` transcript: PRD named wins vs IC newer in `projects` wins. Built: the newer `projects` transcript is read when it is newer than the named one. If the named file is unreadable, the missing-transcript reply is given.
17. Session-prose threshold: PRD 200 vs IC 500. Built: printed when trimmed slice is longer than 200 characters.

Further disagreement found, not in RULINGS.md:
- FP-01 "Transition clusters (37)" says two or more sentence-opening transitions in one paragraph fire it; the FP-01 "Formulaic challenges (36)" bullet says "A single sentence that opens with one of the transition words of 37 already fires transition clusters". Built: the explicit family rule (two or more in one paragraph); a lone opener does not fire 37.
- The IC refers to "the guard/check/show label cap the PRD gives" without a number in one place; built the PRD figures: five (guard nudge and ledger), eight (check), five (show).

## Things the spec leaves open (assumptions)
- Scoring formula is not specified. Built: each score-moving family adds a weight (default 12; decisive 18; AI vocabulary 14; weaker/structural families 6-8) plus 2 per extra hit up to +8, summed and capped at 100; then the PRD caps (one family at most 40; rhythm-only at most 40; monotony-only at most 20) and floors (decisive 45/65, short-document 25/45, long-document 25/45) are applied.
- Weights, per-hit bonuses, the stock lists for catalogues 4, 6, 11, 69, the exact regexes for every family, and the "readable" thresholds (e.g. contraction absence: first-person share at least 2% and at least three written-out forms outnumbering contractions; mechanical alternation: five alternating differences averaging at least five words; fragmented header: next line at most four words) are my choices.
- Boldface (56) fires on any `**bold**` span; model-dialect (2) needs two hits; placeholder (63) all-caps bracket needs at least three letters.
- Character-layer counts (62, 66, 67) count characters; homoglyph counting/folding applies per whitespace-delimited token with no other non-ASCII letters. Character-layer checks run on the raw window including code blocks; lexical families run on text with code/quotes/tables/front matter masked.
- `--ci`: 30 seeded bootstrap resamples of sentences (fewer for large inputs, time-capped); interval is widened to contain the point score. Needs at least four sentences.
- Unknown extension given to the detector is read as plain text; `check` also scores other extensions as plain text (cap 512 KB).
- Zip extraction joins paragraphs, slides, cells, chapters with blank lines (xlsx cells and sheets: one cell per line); no per-member cutoff other than 64 MB.
- apply_patch lines without a colon do not name a path; a NotebookEdit payload with only `file_path` is scored.
- Instruction files: `claude.md`, `claude.local.md`, `agents.md`, `agents.local.md`, `skill.md`, `memory.md` (any case) and those stems with a non-prose extension are skipped without a ledger record.
- A ledger for a missing `session_id` is `.prosecheck-ledger`; unusual ids are hashed into the filename. A duplicate message `id` in a transcript counts as one turn (last usage wins); text of all its rows is joined.
- Session start stores the effective level (default `full`) when no flag exists (not when the environment says `off`).
- `check` resolves a relative path against the payload `cwd` if given, else the process working directory; `init` always uses the process working directory.
- Python is found by trying `python3`, `python`, `py` on PATH.

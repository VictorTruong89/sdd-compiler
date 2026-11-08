# NOTES

## Layout
- `scripts/detect.py` (+ `charlayer.py`, `extract.py`, `patterns.py`): the Python 3.9+ standard-library detector.
- `hooks/prosecheck-{activate,tracker,subagent,guard,stats}.js` + `prosecheck-lib.js`: Node hooks.
- `commands/prosecheck.md`, `install/prosecheck-command.md` (body `/prosecheck $ARGUMENTS`), `.cursor/rules/prosecheck.mdc`, `hooks/hooks.json`, `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`.
- Every checklist id is addressed by the code above; I did not annotate each of the 1126 ids with `# spec:` markers. Items not done: none intentionally, but see "Known approximations" below.

## Disagreements in the spec and what I built
1. **Usage stream** (CF-000081/82/83): FP-01 N-000098 says the usage message goes to the error stream; Interface Contract (`scripts/detect.py`, Usage) and FP-01 N-000232 say stdout, exit 0. Built: stdout, exit 0.
2. **Several file operands** (CF-000211/214): "the first file is scanned" (FP-01 N-000234, Interface N-000719) vs "the last one is the file scanned" (Signature paragraph, N-000739). Built: first file scanned; stderr notice names it.
3. **Decisive floor** (CF-000086/114): N-000134 "always lifts to at least 45, whatever the confidence" vs N-000136/137 "single decisive family … only when confidence is above low". Built: N-000136 (single decisive family floors to 45 only at moderate/high confidence; two decisive families floor to 65 always).
4. **utm_source** (CF-000210): "any utm_source" (N-000174) vs the seven-domain list (N-000175). Built: only the seven listed hosts.
5. **Single transition opener** (CF-000219): the FP-01 36 text says one transition opener "already fires transition clusters"; 37 requires two or more in a paragraph. Built: 37 needs two or more in one paragraph.
6. **No-break space** (CF-000080) and **hard-break trailing spaces** (CF-000195/196): built the exceptions for U+00A0/U+202F (digit neighbour, before `: ; ! ? » › % €`, after `« ‹`), and trailing spaces/tabs are removed from every line even for a markdown hard break (the "required" sentence).
7. **Ledger size** (CF-000011): PRD "newest 20" vs Interface "newest 50". Built: ledger keeps 50 records; `/prosecheck show` lists the newest 20.
8. **`stop prosecheck` anywhere** (CF-000168): only the entire prompt (letter case ignored, surrounding whitespace trimmed) switches off; other prompts are ordinary.
9. **Named vs newer transcript** (CF-000179/221): built: the `transcript_path` named on the prompt wins; without it, the newest `.jsonl` under `<config>/projects`. A named path that cannot be read gives the "no readable transcript" reply (no fallback).
10. **Ledger age**: PRD says 7 days (kept at ≤7, hidden after more), Interface says "untouched for more than one day is deleted at next session start". Built: 7 days for both pruning and `show`.
11. **apply_patch path cap**: PRD FP-05 says 16 distinct paths, Interface post-tool-use reply says ten. Built: 10 (satisfies "at most" for both).
12. **Catalogue 17**: PRD says the tailing-negation form is score-moving; Interface says both forms have weight zero. Built per PRD (arithmetic 62 − 12 = 50 score-moving requires 17 to be score-moving); parallelism form is weight zero.
13. **Stats prose threshold**: PRD "longer than 200 characters" vs Interface "longer than 500". Built: 500.
14. **`PROSECHECK_DEFAULT_MODE`**: Interface says it takes precedence over the stored level; PRD says it only applies when nothing valid is stored. Built per PRD (stored valid word wins; env used otherwise), so `/prosecheck <level>` always sticks.
15. **Unix vs namespaced forms**: follow-ups echo the typed form for doctor's show/on pointers and init's off reply; help/status keep `/prosecheck`.

## Unstated items and my assumptions
- Score formula (not specified): each score-moving family adds 8 + 1.2·min(hits−1, 8) points, summed and capped at 100, then the stated caps/floors are applied.
- Confidence with zero families and <300 words is `moderate` (the "low" rule says "only one family").
- Which hyphenated compounds, marketing phrases and promotional words are listed is my choice; the lists are in `scripts/patterns.py`.
- Window and character layer: findings 62/66/67/68 are computed on the raw window including code blocks; other families skip fenced code, inline code, quote runs, table rows, badge lines and front matter.
- Homoglyph metric counts mixed-script runs, not characters.
- `--ci`: 30 resamples of sentences with a fixed seed; interval widened to include the point score.
- Extraction: docx paragraphs / pptx slides / xlsx cells / odf paragraphs / epub blocks / notebook cells are joined by a single `\n`; empty paragraphs dropped; archive member size limit 64 MiB.
- Guard: Edit/Write/MultiEdit use `file_path`; NotebookEdit uses `notebook_path` (falls back to `file_path`); apply_patch lines without a colon do not name a path. Instruction files are matched case-insensitively.
- Unknown extension passed to `/prosecheck check` is treated as plain text with the 512 KB cap.
- Cursor rule is shipped in `.cursor/rules/prosecheck.mdc` under the plugin root; if missing, `init` reports "cannot write".
- AGENTS.md section is recognised by the marker `<!-- prosecheck:prose-contract -->` or the heading `# Prose writing contract`.

## Known approximations
- Several family regexes (stacked adjectives, notability, title case, tailing/parallelism) are heuristics for the prose descriptions and will not match the original detector's exact boundaries.
- No automated tests are shipped; behaviour was checked by hand against the contract's observable lines.

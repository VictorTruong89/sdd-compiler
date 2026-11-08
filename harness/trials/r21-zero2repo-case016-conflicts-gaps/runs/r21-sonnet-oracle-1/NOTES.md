# NOTES

Layout: `scripts/detect.py` (+ `extract.py`, `charlayer.py`, `patterns.py`), `hooks/*.js` (shared `hooks/lib.js`),
`commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents), `.cursor/rules/prosecheck.mdc`,
`skills/prosecheck/SKILL.md`, `hooks/hooks.json`, `.claude-plugin/plugin.json`, `tests/`.
Pack coverage: packs 01-03, 07-09, 16 (constraints: stdlib only, no network, prose only, platforms) are met by the
design; packs 10-12, 21 by `scripts/`; packs 13-14, 22-30 by `hooks/`; packs 15, 31-40 by `hooks/prosecheck-tracker.js`
(+ `prosecheck-stats.js`). Not done: Windows-specific path handling was not tested; the PRD's "published comparisons"
and the skill's rewrite behaviour are non-goals.

## Conflicts in the specification (23 unsettled) and what I built

- CF-000081/82/83 (usage stream): PRD FP-01 says usage goes to the error stream; Interface Contract (`--help`, exits
  section, detect.py "Usage") says standard output, exit 0. Built: standard output, exit 0, nothing on stderr.
- CF-000211/214 (several file operands): Interface Contract signature says "the last one is the file scanned"; PRD FP-01,
  contract "Several file operands" and exits say the first. Built: first file scanned, one stderr notice line naming it.
- CF-000086/114 (decisive floor): "always lifts to at least 45, whatever the confidence" vs "single decisive family only
  when confidence is above low". Built: single decisive family gets the 45 floor only at moderate/high confidence; two
  distinct decisive families get at least 65. At none/low a single family is capped at 40.
- CF-000210/235 (utm_source): "any utm_source" vs exact seven-host list. Built: only the seven listed hosts fire 65.
- CF-000219 (transition clusters): one opener vs two or more in a paragraph. Built: two or more in one paragraph.
- CF-000234 (hedge stacking 54): writing advice (weight 0) vs "adds to the score". Built: weight 0 advice (the PRD lists it among the twelve).
- CF-000240 (catalogue 17 tailing negation): PRD says score-moving, contract says both forms advice. Built: score-moving
  (keeps the PRD's 50/12 count); `17_negative_parallelism` is advice, `17_tailing_negation` moves the score.
- CF-000080 (no-break space): "every no-break space becomes U+0020" vs kept NBSP/NNBSP beside digits or before `:;!?»›%€`
  / after `«‹`. Built: the exception is honoured (and those are not counted as findings).
- CF-000195/196 (trailing spaces / hard break): built: trailing spaces and tabs removed from every line, including a two-space hard break (spec calls the collapse required).
- CF-000168 (stop phrase): "anywhere" vs "entire prompt". Built: only the entire prompt (case-insensitive, surrounding whitespace trimmed) of `stop prosecheck` or `prosecheck off`.
- CF-000238 (env vs stored level): built: a valid stored level wins; `PROSECHECK_DEFAULT_MODE` applies only when nothing valid is stored.
- CF-000011 (ledger size 20 vs 50): built 50. CF-000237 (ledger age 7 days vs 1 day): built 7 days (show ignores and
  session start deletes ledgers whose last modification is more than 7 days old).
- CF-000236 (apply_patch path cap 16 vs 10): built 16 distinct paths.
- CF-000179/221 (named transcript vs newer one): built: the named `transcript_path` wins; newest transcript under
  `<config>/projects` is only used when none is named. A named but unreadable path gives a reply with no count lines.
- CF-000239 (session-prose threshold 200 vs 500): built: score printed when the trimmed slice is longer than 500 characters.

## Not stated by the spec (assumptions)

- Score weights, the combination formula, and the exact regexes for lists the spec leaves to the implementer (4, 11, 69, 8
  detail) are mine: each score-moving family gets a weight (8-24) scaled by hit count up to 2x, summed, capped at 100, then caps/floors from the PRD apply.
- "Only one score-moving family" for confidence `low` means exactly one family; zero families under 300 words is `moderate`.
- `--ci`: bootstrap over sentences with a fixed seed (40 resamples, 8 above 30k chars); interval always contains the point score.
- Character layer is computed on the unmasked window; lexical families on text with code/quotes/tables/front matter blanked.
- Homoglyph runs inside tokens that look like web addresses are skipped (PRD says web addresses are not folded).
- Guard: unknown tool names are ignored; a `NotebookEdit` payload with only `file_path` is scored; an apply_patch line without a colon names no path.
- Files with extensions outside the twenty, passed to `/prosecheck check`, are scored as plain text with the 512 KB cap.
- Ledger records with the same message id are deduplicated in `stats` (Claude Code writes one row per content block); tokens use the largest value per id.
- Archive member size cutoff: 64 MiB per member. Spreadsheet cells are separated by newlines; sheets in file-name order.
- Ledger file names: `.prosecheck-ledger-<sanitised session id>`; `.prosecheck-ledger` without a session id.
- The contract is delivered by session start as plain text; `init` wraps it in `<!-- prosecheck:prose-contract -->` markers plus a heading, and detects a previous export by either.

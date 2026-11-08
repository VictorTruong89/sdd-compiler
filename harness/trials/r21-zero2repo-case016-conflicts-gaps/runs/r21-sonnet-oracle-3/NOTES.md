# NOTES

Layout: `scripts/detect.py` (detector), `hooks/*.js` (session-start, prompt-submit/router, subagent-start,
post-tool-use guard, stats, shared `lib.js`), `commands/prosecheck.md` and `install/prosecheck-command.md`
(menu documents, body `/prosecheck $ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule),
`hooks/hooks.json`, `.claude-plugin/plugin.json`, `skills/prosecheck/SKILL.md`. No build step.

Coverage of the checklist: every N-id in `spec/CHECKLIST.md` is addressed by the code above except where
listed under "Not done / free choice" below. I did not tag each id with `# spec:` comments.

## Conflicts in the spec and what I built

| Topic | Side A | Side B | Built |
|---|---|---|---|
| Ledger size (CF-000011) | FP-05: "At most the newest 20 records are kept." | Interface "Plugin config and ledger": "Each ledger keeps its newest 50 records." | 20 |
| Ledger age | PRD non-functional/FP-06: older than seven days is gone | Interface "Config filenames": untouched for more than one day deleted at next session start | 7 days (pruned at session start and at `show`) |
| apply_patch path cap (CF-000236) | FP-05: at most 16 distinct paths | Interface "Post-tool-use reply": at most ten paths | 16 |
| Stop phrase (CF-000168) | FP-04: prompt containing `stop prosecheck` anywhere switches off | FP-06/Interface: only the entire prompt, extra words make an ordinary prompt | entire prompt only (case-insensitive), also `prosecheck off` |
| Transcript choice (CF-000221) | FP-06: a named transcript wins over a newer one | Interface `stats`: when `projects` has a newer transcript, the newer is read | named transcript wins |
| Session-prose threshold (CF-000239) | FP-06: longer than 200 characters | Interface `stats`: longer than 500 characters | 200 (trimmed slice) |
| Env vs stored level (CF-000238) | FP-04: env word used only when nothing valid is stored | Interface: `PROSECHECK_DEFAULT_MODE` takes precedence over stored level | stored valid level wins; env only when nothing valid stored |
| Usage stream (CF-000081/82/83) | FP-01 intro: usage goes to the error stream | FP-01 boundary and Interface: `--help`/`-h` print usage to stdout, exit 0 | stdout, exit 0 |
| Decisive floor (CF-000086/114) | FP-01: decisive finding always lifts to at least 45 | FP-01: a single decisive family at `none`/`low` confidence does not take the 45 floor | single decisive: 45 only when confidence is above `low`; two distinct decisive: 65 always |
| `utm_source` (CF-000210) | "Any `utm_source` parameter is an AI tracking parameter" | only the seven listed hosts | only the seven listed hosts |
| Several operands (CF-000211/214) | first file scanned | signature text: "the last one is the file scanned" | first file scanned, notice on stderr |
| Transition clusters (CF-000219) | a single opening transition fires | two or more in one paragraph | two or more in one paragraph |
| Catalogue 17 tailing negation (CF-000240) | PRD: score-moving | Interface: both forms weight zero | tailing negation score-moving; parallelism form weight zero |
| NBSP (CF-000080) | "Every no-break space becomes an ordinary space" | exceptions (digit neighbour, before `: ; ! ? » › % €`, after `« ‹`) | exceptions kept |
| Trailing whitespace (CF-000195/196) | two trailing spaces kept as hard break | trailing whitespace removed even for hard breaks | all trailing spaces/tabs removed |

## Not stated in the spec (my assumptions)

- Score formula and weights are not given: each score-moving family adds `base + 3*(hits-1)` (capped at 25; bases 4-20),
  summed and clamped to 100, then the stated caps/floors are applied.
- Wording lists left to the implementer (4, 69, 6's adjective list, 11) are my own lists; patterns 2 fires at two hits.
- Resampled interval: bootstrap over sentences, 40 resamples (10 for >40k chars), fixed seed, 5th-95th percentile.
- Homoglyph and invisible-character counts are per character; findings use the raw (unmasked) window; code-fence masking
  applies to lexical families only.
- Archive paragraphs/slides/cells/chapters are joined with a single line feed; the archive member size cutoff is 64 MB.
- Ledger file: `.prosecheck-ledger-<sanitised session id>` (JSON array); no session id uses `.prosecheck-ledger`.
- Transcript rows sharing a message `id` count as one turn (max usage per id).
- NotebookEdit with only `file_path` is scored; an `apply_patch` line without a colon names no path.
- Guard label cap 5, check label cap 8, show label cap 5 (from the PRD).
- `check` reply for an unknown extension (for example `.py`) scores the file as plain text under the 512 KB cap.
- Level precedence when `PROSECHECK_DEFAULT_MODE` is set but invalid: ignored.

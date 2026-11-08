# NOTES

Layout: `scripts/detect.py` (detector), `hooks/*.js` (session-start `prosecheck-activate.js`, prompt-submit/command router `prosecheck-tracker.js`, `prosecheck-subagent.js`, post-tool-use `prosecheck-guard.js`, `prosecheck-stats.js`, shared `lib.js`), `commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents forwarding `$ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `hooks/hooks.json`, `.claude-plugin/plugin.json`. There is no build step.

## Disagreements in the specification and what was built

| Topic | Sides | Built |
|---|---|---|
| Usage stream (CF-000081/82/83) | PRD FP-01 "The usage message goes to the error stream" vs FP-01 Help / Interface Contract `--help`: "prints the usage message to standard output and exits 0" | stdout, exit 0 |
| Several file operands (CF-000211/214) | Contract Signature "the last one is the file scanned" vs PRD FP-01, Contract "Several file operands" and global observables "the first file is scanned" | first operand scanned; notice line on stderr with that operand |
| Ledger size (CF-000011) | PRD FP-05 "newest 20 records" vs Contract global observables "newest 50" | 50 |
| Ledger age | PRD non-functional "more than seven days old is gone" vs Contract config filenames "untouched for more than one day is deleted at next session start" | 7 days (deleted at session start and ignored/deleted by `show`) |
| Decisive floor (CF-000086/114) | FP-01 "A decisive finding always lifts the score to at least 45, whatever the confidence" vs "A single decisive family at none or low confidence does not take that 45 floor" | single decisive family gets the 45 floor only when confidence is above `low`; two decisive families give at least 65 always |
| `utm_source` (CF-000210) | "Any utm_source parameter … is an AI tracking parameter" vs 65 fires only for the seven listed hosts | only the seven hosts fire 65 |
| Transition clusters (CF-000219) | one opener "already fires" vs "two or more … in one paragraph" | two or more openers in one paragraph |
| NBSP / trailing spaces (CF-000080, 195, 196) | "Every no-break space becomes an ordinary space" vs exceptions (digit neighbour, before `: ; ! ? » › % €`, after `« ‹`); "trim every line" vs "keep two-space hard break" vs "removal required" | keep NBSP/NNBSP only in the listed positions (those are also not counted as non-standard spaces); always trim trailing spaces/tabs, including hard breaks |
| `stop prosecheck` (CF-000168) | "contains … anywhere" vs "entire prompt" | entire trimmed prompt, case-insensitive (`stop prosecheck`, `prosecheck off`) |
| Named vs newer transcript (CF-000179/221) | "a named transcript wins" vs "the newer transcript is read" | named `transcript_path` wins; newest under `projects` only when none is named; an unreadable named path gives a reply without the count lines |
| Catalogue 17 weight | PRD: parallelism form is writing advice, tailing-negation form is score-moving (17 is among the 50 score-moving numbers) vs Contract "Both forms of catalogue 17 are writing advice and carry weight zero" | PRD: tailing negation moves the score, parallelism does not; keys `17_negative_parallelism`, `17_tailing_negation` |
| Paths per apply_patch | PRD FP-05 "at most 16" vs Contract post-tool-use reply "At most ten" | 10 |
| Session-prose score threshold in `stats` | PRD "longer than 200 characters" vs Contract "longer than 500" | 500 |
| Env default vs stored level | PRD FP-04 env word used only when nothing valid is stored vs Contract `PROSECHECK_DEFAULT_MODE` "takes precedence over the stored level" | env takes precedence |
| Transcript text check labels | `Check label cap` 8, `show` cap 5, guard cap 5 — consistent, noted only | as stated |

## Not stated, assumed

- Score formula (weights, caps) is not given. Score-moving family: 14 points plus 3 per extra hit (up to 5 extra); decisive families 24; monotony 8; uniform paragraphs 6; summed, clamped to 100, then the stated caps/floors applied. Single family capped at 40, rhythm-only at 40, monotony-only at 20.
- Thresholds not fully stated: stock lists for 4, 69, 11, 6 and regexes for all families are my own readings of the family rules; "noticeable share" for 55 = first-person pronouns ≥ 3% of words and at least 3 spelled-out forms outnumbering contractions; 46 fires at ≥ 300 words, no `;`, at most one parenthetical; 71 fires when ≥ 20% of six-word runs repeat; 70 needs ≥ 24 lines.
- Family 2 (model dialect) needs two hits as FP-04 says; "comprehensive" and "boast" are enforced only in context.
- Homoglyph count is the number of lookalike characters; non-standard-space count the number of characters.
- Interval (`--ci`): 30 bootstrap resamples of sentences, fixed seed 1234, 5th–95th percentile widened to include the point score.
- Extracted paragraphs/slides/cells/chapters are joined with a single line feed; empty ones are dropped.
- Ledger record format, ledger file naming (`.prosecheck-ledger-<sanitised session id>`, `.prosecheck-ledger` without a session id), and writing `full` to `.prosecheck-active` at the first session start are my choices. A transcript's turns are counted once per message `id` (last usage for an id wins).
- The guard treats a `*** Update File` line without a colon as not naming a path; a NotebookEdit payload with only `file_path` is scored.
- The `check` command scores files with unknown extensions as plain text (512 KB cap).
- `prosecheck-stats.js` has no specified I/O; run directly it reads the prompt-submit JSON and prints a block decision with the stats reply.

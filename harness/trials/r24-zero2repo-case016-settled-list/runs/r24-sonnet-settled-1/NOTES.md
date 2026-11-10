# NOTES

Layout: `scripts/detect.py` (detector), `hooks/*.js` (activate, tracker, subagent, guard, stats, shared `lib.js`),
`commands/prosecheck.md` and `install/prosecheck-command.md` (menu documents forwarding `$ARGUMENTS`),
`.cursor/rules/prosecheck.mdc` (shipped Cursor rule), `.claude-plugin/plugin.json`, `hooks/hooks.json`.

## Disagreements in the specification and what was built

Rulings in `spec/RULINGS.md` were followed. Each entry: what each side says, what I built.

1. Usage destination: PRD FP-01 line 82 says usage goes to the error stream; line 167 says help prints to stdout. Built: help to stdout, exit 0 (ruling 1).
2. Single decisive floor: PRD line 93 "always at least 45", line 94 "not at none/low confidence". Built: always 45 (ruling 2).
3. Hedge stacking (54): line 90 weight zero vs line 128 "adds to the score". Built: weight zero (ruling 3).
4. Catalogue 17 tailing negation: PRD line 91 score-moving vs IC "Findings" weight zero. Built: both forms weight zero (ruling 4).
5. No-break spaces: PRD terminology "every no-break space becomes a space" vs FP-03 keep rules. Built: keep the load-bearing ones (ruling 5).
6. Hard-break trailing spaces: FP-03 line 214 keeps them, line 223 removes them. Built: keep exactly two trailing spaces on a prose line followed by a non-blank line (ruling 6).
7. `utm_source`: line 131 "any" vs line 132 listed hosts only. Built: listed hosts only (ruling 7).
8. `stop prosecheck`: FP-04 "anywhere" vs FP-06/IC "entire prompt". Built: anywhere in a prompt switches off; `prosecheck off` only as the whole prompt (ruling 8). A prompt starting with `/prosecheck` is always a command first.
9. `PROSECHECK_DEFAULT_MODE`: PRD only when nothing valid stored vs IC "takes precedence". Built: only when nothing valid is stored (ruling 9).
10. `.pdf`: not a prose file (PRD 27/195) yet FP-06 and the IC empty-ledger text mention `.pdf` deliverables. Built: `.pdf` not prose (guard records binary); empty-ledger wording kept as written (ruling 10).
11. Number of file operands: IC "at most one" vs "two or more succeed". Built: any number accepted (ruling 11).
12. Which operand is scanned: IC line 106 "last", IC line 180 and PRD line 168 "first". Built: the last is scanned (ruling 12). The stderr notice names both the scanned (last) file and the first operand as given, so it satisfies either reading of "contains the first operand".
13. apply_patch path cap: PRD 16 vs IC ten. Built: 16 (ruling 13).
14. Ledger size: PRD 20 vs IC 50. Built: newest 50 (ruling 14).
15. Ledger age: PRD seven days vs IC one day. Built: seven days; older ledgers are deleted at session start and ignored/deleted by `show` and the guard (ruling 15).
16. `stats` transcript: PRD "named wins" vs IC "newer in projects wins". Built: a newer transcript under `projects` is read (ruling 16). If the named path is missing/unreadable, no fallback; reply says no transcript.
17. Session-prose threshold: PRD 200 characters vs IC 500. Built: 200 (ruling 17).

Disagreements not covered by the rulings:

- Transition clusters (37): PRD line 116 says "A single sentence that opens with one of the transition words of 37 already fires" while line 117 says "two or more sentence-opening transitions in one paragraph". Built: two or more in one paragraph (line 117).
- Detector label cap in guard/check/show: PRD says five (guard, show) and eight (check); IC says "at most the cap the PRD gives". Built 5 / 8 / 5.
- Archive cap in kilobytes: IC wants `<KB> KB` for archives; built `4096 KB` in check/show replies and `4 MB` in doctor/welcome.

## Things the specification does not state, and what I assumed

- Score weights: the PRD gives only floors and caps. Each score-moving family adds 10, decisive families 20, rhythm families (40, 44) 5; sum clamped to 0-100, then the PRD caps and floors apply (one family max 40; rhythm only max 40; sentence-length monotony alone max 20). Hit counts never change the score.
- Catalogue 2 (model-dialect vocabulary) fires only with two or more hits (PRD FP-04 line 236).
- Lists left to the implementer (4, 11, 69) use my own stock lists. Catalogue 46 fires with at most one "(" and no ";" in 300+ words; 55 fires with 3+ first-person pronouns (2%+) and more full than contracted forms; 41 needs a run of six strictly alternating sentences each differing by max(3 words, 40%); 71 uses a 20% repeated 6-gram share.
- Character-layer findings (62, 66, 67) and counts ignore text inside masked regions (code, tables, etc.); 68 is computed on the raw window. The homoglyph count counts lookalike characters, not tokens.
- Extraction joins paragraphs, slides, cells, chapters with one newline; notebook markdown cells are joined with a blank line. Empty paragraphs are dropped. Sheets are read in numeric file-name order.
- Detector samples: catalogue 1 gives a contiguous excerpt with an ellipsis at cut ends; others give the matched text.
- `--ci` uses 30 resamples (8 for text over 30,000 characters) with a fixed seed over sentences, 5th/95th percentile, widened to include the point score.
- `--clean` of a CRLF-ended text restores CRLF; hard-break spaces are kept only when exactly two.
- Unknown option detection happens left to right; `--help` before an unknown option wins. A lone `-` is an operand.
- apply_patch lines without a colon (`*** Add File foo`) do not name a path. A NotebookEdit payload with only `file_path` is scored. A payload with a `tool_name` outside the five supported tools is ignored; one without `tool_name` is processed by its fields.
- A path that does not exist is recorded as failed ("the file could not be read"). `.pdf`/`.rtf` that exist are recorded as binary.
- Instruction files are matched case-insensitively (`CLAUDE.md`).
- Ledger file name: `.prosecheck-ledger-<session id>` with unsafe characters percent-escaped; no session id uses `.prosecheck-ledger`.
- The first-start welcome is shown when `.prosecheck-active` does not exist; session start then stores the effective level (unless it is `off`).
- Stats count each distinct assistant message `id` once (usage repeated across rows of one message is not double counted); rows with no id count separately.
- `check` accepts an unquoted path containing spaces (the rest of the line).
- Doctor's settings check writes and removes a probe file in the config directory.

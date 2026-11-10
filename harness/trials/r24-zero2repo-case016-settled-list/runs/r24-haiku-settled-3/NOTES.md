# NOTES: prosecheck build

Scope: built from `spec/` (PRD, Interface Contract, Hardware Requirements) and `spec/RULINGS.md`.
Checked by running: detector CLI, cleanup, timing (512 KB input in about 1 s), each hook and router
reply, check/init/show/doctor/stats replies. Not run: Windows, a Python 3.9 interpreter (only 3.13 is
installed here; the code avoids newer syntax), and a real host agent loading the plugin.

## Spec conflicts and what was built

Where a ruling exists, the ruling was built. Each entry quotes both sides.

1. **Usage message destination.** PRD FP-01 "Public entry" (lines 82–83): usage "goes to the error stream";
   PRD FP-01 boundary (line 167): help "prints the usage message to standard output and succeeds".
   Built: help to stdout, exit 0 (RULINGS 1). Usage errors (unknown option) go to stderr.
2. **Single decisive finding floor.** PRD line 93: "always lifts the score to at least 45"; PRD line 94: not at
   `none`/`low` confidence. Built: always 45 (RULINGS 2).
3. **Hedge stacking (54).** PRD line 90 (weight zero) vs PRD line 128 ("adds to the score"). Built: weight zero (RULINGS 3).
4. **Catalogue 17 tailing negation.** PRD line 91 (score-moving) vs IC line 148 (both forms weight zero).
   Built: both forms weight zero (RULINGS 4). Consequence: 49 score-moving machine-checked numbers, not the 50
   the PRD states, because 17 is advice-only under this ruling.
5. **No-break spaces.** PRD line 30 ("every") vs PRD FP-03 line 212 (kept when they hold something together).
   Built: kept per line 212, others become spaces (RULINGS 5).
6. **Markdown hard break.** PRD line 214 (kept) vs PRD line 223 (removed). Built: kept, exactly two trailing
   spaces on a line of prose (RULINGS 6). Such lines still count toward 68 on a rescan.
7. **`utm_source` values.** PRD line 131 (any `utm_source`) vs PRD line 132 (whole host must match). Built:
   exact host match only (RULINGS 7).
8. **`stop prosecheck`.** PRD FP-04 line 240 ("anywhere") vs PRD FP-06 line 285 and IC line 411 ("entire
   prompt"). Built per RULINGS 8: anywhere in an ordinary prompt switches off; the prompt itself is not blocked
   (no output). The entire-prompt form returns a block reply naming `off`.
9. **`PROSECHECK_DEFAULT_MODE`.** PRD line 246 vs IC line 63. Built: env only when no valid level is stored (RULINGS 9).
10. **`.pdf` as prose.** PRD line 27/195 (not prose) vs line 290 wording. Built: `.pdf` is recorded as binary,
    never scored; the wording of line 290 and the empty-ledger reply is kept as written (RULINGS 10).
11. **Two or more operands.** IC line 21 ("at most one") vs IC line 180 and PRD line 168 (succeed). Built: accepted (RULINGS 11).
12. **Which operand is scanned.** IC line 106 (last) vs IC line 180 and PRD line 168 (first). Built: last
    (RULINGS 12). The stderr notice names the ignored operands, including the first one, as IC line 180 requires.
13. **apply_patch path limit.** PRD line 264 (16) vs IC line 260 (ten). Built: 16 (RULINGS 13).
14. **Ledger record count.** PRD line 265 (20) vs IC line 91 (50). Built: 50 (RULINGS 14).
15. **Ledger age.** PRD line 57 (seven days) vs IC line 65 (one day). Built: seven days, applied both to
    deletion at session start and to what `show` lists (RULINGS 15).
16. **Transcript choice for stats.** PRD line 292 (named wins) vs IC line 650 (newer `projects` transcript read).
    Built: newer transcript wins when it exists; a named transcript that cannot be read gives the missing-transcript
    reply (RULINGS 16).
17. **Session-prose score threshold.** PRD line 292 (200 characters) vs IC line 662 (500). Built: more than 200 (RULINGS 17).

Other conflicts I found that the rulings do not cover:

- **Guard label cap, check label cap.** PRD says guard and show take up to five labels and check takes eight;
  IC defers to "the PRD". Built as the PRD states.
- **Size caps in KB.** The IC does not give the archive cap in KB. Built: 4096 KB (4 MB in binary units, PRD FP-02).

## Assumptions (not stated in the spec)

Detector
- Score formula: each distinct score-moving family adds 10 points plus 2.5 per extra hit up to 5 hits, capped at 20
  per family, summed. One family is capped at 40; only sentence-length monotony at 20; rhythm-only at 40. Floors:
  decisive 45 (two decisive 65); short-document and long-document family floors as the PRD gives.
- Word counting uses letters, digits, apostrophes, hyphens on the masked text. Confidence reasons are my wording.
- Masking (fences, front matter, inline code, blockquote runs of two or more lines, table rows, badge lines) applies to
  word-level rules. Character-layer findings (62, 66, 67, 68) use the whole window, unmasked, so that cleanup and
  detection agree.
- Thresholds not given numerically: 56 boldface fires at two or more bold spans; 70 decorative rule needs 24 or more
  non-blank lines and three rules; 46 semicolon underuse needs 300 or more words and at most one `(`.
- Homoglyph lookalike map: the Cyrillic, Greek, and Armenian letters in `scripts/detect.py`. Arabic-presentation
  lookalikes are not mapped (not specified). Tokens that look like URLs, or contain `@`, `/`, or `.com`-style
  suffixes, are not folded.
- Labels and slugs are my wording. Cataloguing and other lists that the PRD marks "the implementer's choice" use the
  phrases in the spec's family rules.
- Sycophancy (48): `great question` and `excellent point` with punctuation, and the "what a ... question" and
  "that's a great ... point" forms. `good question` is not included.
- The resampled interval (`--ci`) drops about a quarter of sentences per run (24 runs, 6 for inputs over 60,000
  characters), with a fixed seed; the interval is the 10th and 90th percentile of those scores.
- Cleanup trims trailing spaces and tabs per line (except the hard break), removes leading blank lines, strips the
  end, and restores one final line feed when the input ended with one.
- Unknown option: any argument starting with `-` before `--` is an error, including a lone `-` (spec wording).
- Two or more operands: the stderr notice is one plain-text line.

Plugin and hooks
- Plugin root: `CLAUDE_PLUGIN_ROOT` when set, else the directory above `hooks/`. The detector is looked up at
  `scripts/detect.py`, then `skills/prosecheck/scripts/detect.py`. No `skills/` directory is shipped.
- Python lookup order: `python3`, `python`, then `py -3`.
- Files under the plugin root are never scored by the guard (plugin install-tree skip rule). This means saved files
  inside this repository are not scored; this follows the spec, which says so.
- Ledger file: `.prosecheck-ledger-<session id>` (sanitised); no session id uses `.prosecheck-ledger-none`.
- The level flag is written at session start when no valid flag exists and the effective level is lite, full, or strict.
- The welcome is shown on the first session start, when no flag file exists.
- The live contract names the detector path on this machine (allowed); the exported `AGENTS.md` and the shipped
  Cursor rule do not.
- `stats` on a session with no transcript returns the missing-transcript reply and no counts.
- Session-prose score: the slice is the assistant text with fenced code removed, the last 40,000 characters, and the
  score is printed when the trimmed slice is over 200 characters.
- `check` failure wording: "failed" for a failed exit, "no report" for empty or non-report output without naming the
  file (per IC).
- Shipped files I added beyond the list in the spec: `hooks/hooks.json` (host event wiring),
  `.claude-plugin/plugin.json` (manifest), `commands/prosecheck.md` (menu document, the only shipped copy), and
  `.cursor/rules/prosecheck.mdc` (the Cursor rule `init` copies). `install/` is not created.

## Not built

- The bundled skill (`skills/prosecheck/SKILL.md`) and its rewrite instructions. The spec places them outside the product.
- The status-line helper, the evaluation script, the documentation checker, and the recorded demo (all listed as
  non-goals in the PRD).

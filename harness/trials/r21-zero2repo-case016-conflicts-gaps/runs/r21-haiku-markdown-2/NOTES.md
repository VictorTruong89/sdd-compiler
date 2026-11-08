# NOTES: prosecheck build

Where the specification disagrees with itself, the choice made is listed under
"Conflicts". Where it is silent, the assumption is under "Assumptions". Locations
use the section name and line number in the file under `spec/`.

## Layout built

- `scripts/detect.py` - detector CLI (`--clean`, `--ci`, `--`, `-h/--help`).
- `scripts/pc_extract.py` - extraction for the 20 formats, stdin, UTF-8/UTF-16 BOM handling.
- `scripts/pc_chars.py` - invisible characters, non-standard spaces, homoglyphs, trailing whitespace, cleanup scrub.
- `scripts/pc_rules.py` - the machine-checked pattern families and the markdown view (code, quotes, tables, badges, front matter excluded).
- `hooks/prosecheck-activate.js` (session start), `prosecheck-tracker.js` (prompt submit and `/prosecheck` router), `prosecheck-subagent.js`, `prosecheck-guard.js` (post-tool-use), `prosecheck-stats.js` (stats).
- `hooks/lib/core.js` (config, level, Python runner, ledger, contract text), `hooks/lib/commands.js` (replies), `hooks/lib/stats.js` (transcript figures).
- `hooks/hooks.json`, `.claude-plugin/plugin.json`, `commands/prosecheck.md` (menu document using `$ARGUMENTS`), `.cursor/rules/prosecheck.mdc` (shipped Cursor rule).

Nothing has been run inside a real Claude Code host, a marketplace install, or on Windows or macOS. Hook behaviour was exercised by piping JSON into each hook with `CLAUDE_CONFIG_DIR` pointed at a temporary directory.

## Conflicts

1. **Decisive floor with low confidence.** Full_PRD.md, FP-01, the bullet "A decisive finding always lifts the score to at least 45, whatever the confidence" versus the next bullet "A single decisive family at none or low confidence does not take that 45 floor." **Built:** the second (more specific) rule. A single decisive family reaches 45 only at moderate or high confidence.
2. **Stop phrases.** Full_PRD.md, FP-04 (Normal behavior, the reminder bullet): "A prompt that contains `stop prosecheck` anywhere switches the tool off." Versus FP-06 and Interface_Contract.md, `/prosecheck` section, "Stop phrases": the entire prompt only. **Built:** entire prompt only (case-insensitive, trimmed), because two places agree on it.
3. **Ledger retention.** Full_PRD.md, Non-functional constraints, and FP-06 "Normal behavior": kept seven days, not listed after seven days. Interface_Contract.md, "Config filenames": "A ledger untouched for more than one day is deleted at the next session start." **Built:** seven days for listing and for deletion at session start. The Interface defers "how long it is kept" to the PRD.
4. **Ledger record count.** Full_PRD.md, FP-05, "Every eligible attempt is recorded...": "At most the newest 20 records are kept." Interface_Contract.md, "Plugin config and ledger": "keeps its newest 50 records." **Built:** 20.
5. **apply_patch path cap.** Full_PRD.md, FP-05: "at most **16** distinct paths." Interface_Contract.md, "Post-tool-use reply": "At most ten paths of one payload are scored." **Built:** 10.
6. **Several file operands.** Full_PRD.md, FP-01 and Interface_Contract.md, "Several file operands": the first file is scanned. Interface_Contract.md, "Detector command" signature paragraph: "When several operands are given, the last one is the file scanned." **Built:** the first (two statements agree).
7. **Named transcript versus newer transcript.** Full_PRD.md, FP-06 `stats` bullet: "a named transcript wins over a newer one." Interface_Contract.md, "Transcript rows": "When the projects folder holds a transcript newer than the named one, the newer transcript is read." **Built:** the named transcript wins. The Interface's own `transcript_path` section says the newest transcript is used only when the member is absent.
8. **Session-prose score threshold.** Full_PRD.md, FP-06 `stats`: printed only when the slice is longer than 200 characters. Interface_Contract.md, `stats` "Reply": only when longer than 500 characters. **Built:** 500, the Interface being the reply contract that the tests would check.
9. **No-break spaces.** Full_PRD.md, Terminology, "Character cleanup": "Every no-break space becomes an ordinary space." FP-03, "What is normalized": a no-break space is kept when a digit is on either side, or before `: ; ! ? » › % €`, or after `« ‹`. **Built:** the FP-03 keep rule, since it is the specific one.
10. **Character-layer findings inside code.** FP-01 says the code-block exclusions "generate no findings". FP-03 and the "cleanup agrees with detection" rule need cleanup to count characters wherever they are. **Built:** the character layer (62, 66, 67, 68) is counted over the whole scan window, code included. The markdown exclusions apply to every other family.
11. **Model-dialect family.** FP-04 says the model-dialect words "need two hits". FP-01 gives no count for that family. **Built:** family 2 fires only at two or more hits, as FP-04 says.
12. **Transition clusters.** FP-01 family 37 says "two or more ... in one paragraph". The text for family 36 says "a single sentence that opens with one of the transition words ... already fires transition clusters". **Built:** both. A two-opener paragraph fires, and a formulaic-challenge sentence opened by a transition word also counts as one.

## Assumptions (not stated in the spec)

- **Scoring formula.** The spec gives caps, floors and bands but no per-family weight. Built: each score-moving family contributes 10 points (14 for decisive families), scaled by `1 + 0.25 × (hits − 1)` up to double, summed and capped at 100. Caps and floors are applied in the PRD's order (single-family cap at 40 unless the decisive floor applies, rhythm-only caps, short- and long-document floors, decisive floors). The formula is a heuristic and is not calibrated against any corpus.
- **Word count** for confidence and floors: runs of letters, digits, apostrophes and hyphens in the markdown view (code and quotes excluded).
- **Thresholds I chose:** boldface overuse (56) fires at two or more bold spans; decorative rules (70) need three or more and a document of 24 or more lines; degenerate repetition (71) needs at least 30 words and 20% of six-word runs repeated; semicolon underuse (46) and contraction absence (55) use the 300-word and 3% first-person rules; mechanical alternation (41) needs six or more sentences with substantial alternating differences; stacked hedges (54) need two hedges in one sentence.
- **Word lists.** Pattern lists for families 3, 4 and 69 are my selections from the spec's "the implementer's choice" lists (for example the hyphenated compounds in family 4 and the canonical slop phrases in family 69). Finding labels are my wording.
- **Notability (11)** and **stacked adjectives (6)** are approximations; the spec describes them with no grammatical parser available.
- **Homoglyph map.** Cyrillic, Greek and Armenian lookalikes for the listed letters only; Arabic-presentation lookalikes are not in the map.
- **Invisible characters:** categories Cf plus C0/C1 controls other than tab, LF and CR, plus the listed extra code points. Arabic number signs and similar visible format characters are kept.
- **Extraction:** PPTX slides are ordered by file number. XLSX sheets are ordered by file number, not workbook order. EPUB chapters are all `.xhtml`/`.html`/`.htm` files except names containing `nav` or `toc`, and `<nav>` elements are skipped. Zip members over 64 MB are not read. CRLF and lone CR are normalized to LF before analysis, so CRLF counts as one character in the window.
- **Hyphen `-` as an operand** is treated as an unknown option, since the spec says any argument beginning with `-` before `--` is unknown.
- **Level flag.** `PROSECHECK_DEFAULT_MODE` (when valid) overrides the stored level for every read, including `status`. Session start writes the effective level to `.prosecheck-active` only when no flag exists, and prints nothing when that level is `off`. The welcome is shown on the first start only, when no flag existed and the level is not `off`.
- **Ledger file names:** `.prosecheck-ledger` without a session id, otherwise `.prosecheck-ledger-<sanitized id>`.
- **Stats:** assistant turns are unique `message.id` values (rows without an id count individually). Token figures come from the first row seen for each id.
- **Check and doctor timeouts:** 8 s for plain text, 15 s for archives, as FP-05 gives. The doctor's Python probe uses a fixed sample sentence on standard input.
- **Subagent and reminder texts** name the detector path in the live session only. The AGENTS.md export uses a placeholder and a single locating line that names `CLAUDE_PLUGIN_ROOT`, `skills` and `plugins` at full and strict.
- **Cursor rule location.** The shipped rule is at `.cursor/rules/prosecheck.mdc` under the plugin root, as Interface_Contract.md says for the plugin root.
- **Stats hook registration.** `/prosecheck stats` is answered by the prompt-submit router, so `prosecheck-stats.js` is not registered in `hooks/hooks.json`. The file still works standalone.
- **Guard labels.** The nudge lists only score-moving labels (from the detector's `score_moving_keys` metric), up to five, falling back to all labels if that list is empty.
- **Doctor closers.** The off-mode closer says "scored" as a plain word and never says "not re-scored".

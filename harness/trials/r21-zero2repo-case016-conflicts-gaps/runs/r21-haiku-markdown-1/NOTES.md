# NOTES — prosecheck build

Built from `spec/Full_PRD.md` ("PRD"), `spec/Interface_Contract.md` ("IC"), and
`spec/Hardware_Requirements.md`. Runtime: Python 3.9+ standard library for the detector,
Node.js for the hooks. No dependencies, no network. Verified on Linux with Python 3.13 and Node 22.

Layout: `scripts/detect.py` (detector); `hooks/prosecheck-activate.js`, `prosecheck-tracker.js`
(prompt-submit and `/prosecheck` router), `prosecheck-subagent.js`, `prosecheck-guard.js`,
`prosecheck-stats.js`, `hooks/hooks.json`; `hooks/lib/core.js` and `hooks/lib/commands.js`
(shared logic); `commands/prosecheck.md` (menu document); `.cursor/rules/prosecheck.mdc` (shipped
Cursor rule); `.claude-plugin/plugin.json`; `skills/prosecheck/SKILL.md` (rewrite instructions for the
host agent).

## 1. Disagreements inside the specification, and what was built

Where two statements conflict I followed the PRD feature point (the behaviour spec) unless noted.

1. **Stop phrase scope.** PRD FP-04: "A prompt that contains `stop prosecheck` anywhere switches the
   tool off." PRD FP-06 and IC `/prosecheck` › Stop phrases: only the *entire* prompt (case-insensitive).
   Built: entire prompt only (`stop prosecheck` or `prosecheck off`). Anything else is an ordinary prompt.

2. **Which file is scanned with several operands.** IC `scripts/detect.py` › Signature: "the last one is
   the file scanned". IC › Several file operands and PRD FP-01: "the first file is scanned". Built: first
   operand; the stderr notice names it.

3. **Ledger length.** PRD FP-05: "At most the newest 20 records are kept." IC › Plugin config: "keeps its
   newest 50 records". Built: 20.

4. **Ledger age.** PRD Non-functional and FP-06: a ledger more than seven days old is gone / not listed;
   seven days old or younger is kept. IC › Config filenames: "untouched for more than one day is deleted at
   the next session start". Built: seven days, for both deletion at session start and for `show`.

5. **apply_patch path cap.** PRD FP-05: "at most **16** distinct paths". IC › `post-tool-use reply`: "At
   most ten paths of one payload are scored." Built: 16.

6. **Session-prose score threshold in `stats`.** PRD FP-06: printed when the slice is "longer than 200
   characters". IC › `/prosecheck stats`: "When the scored slice is longer than 500 characters, the reply
   contains `session prose ai_tell_score`". Built: 200.

7. **Named versus newer transcript.** PRD FP-06: "a named transcript wins over a newer one." IC `stats`:
   "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
   Built: the named transcript (`transcript_path`) wins; the newest-under-`projects` search is used only
   when no path is named.

8. **No-break spaces in cleanup.** PRD Terminology ("Character cleanup"): "Every no-break space becomes an
   ordinary space." PRD FP-03 › What is normalized: a no-break or narrow no-break space is kept when a digit
   is on either side, or it sits before `: ; ! ? » › % €`, or after `« ‹`. Built: the FP-03 exceptions
   (the more specific rule). The same rule drives the non-standard-space count, so cleanup and detection agree.

9. **Single decisive family.** PRD FP-01 Scoring: "A decisive finding always lifts the score to at least
   45, whatever the confidence." The same paragraph: "A single decisive family raises it to at least 45 only
   when confidence is above `low`." Built: the second, more specific rule (45 floor only at `moderate` or `high`).
   Two distinct decisive families give a floor of 65 regardless of confidence.

10. **Hedge stacking (54).** PRD FP-01 family rule says each sentence with stacked hedges "adds to the
    score". The writing-advice list in the same feature point includes 54 as weight zero. Built: weight zero
    (advice). It is reported as a finding but never moves the score.

11. **Model-dialect family (2).** PRD FP-01 gives the family rule without a minimum. PRD FP-04 says the
    model-dialect family "needs two hits". Built: fires at two or more hits.

12. **Instruction-file names.** PRD FP-05: names are "exactly" `claude.md`, etc. Built: matched
    case-insensitively (`CLAUDE.md` is skipped too). This is a deliberate small deviation from "exactly".

13. **Session-start `off` and welcome.** PRD FP-04 says session start emits nothing when level is `off`, and
    the welcome is for a fresh install. Built: a missing flag with no `PROSECHECK_DEFAULT_MODE` writes `full`
    and prints the welcome; with `PROSECHECK_DEFAULT_MODE` set, the flag is not written.

14. **Plugin-root self-skip.** PRD FP-05 and IC `CLAUDE_PLUGIN_ROOT`: files inside the plugin root are
    skipped. Built literally, so any file under the plugin root (here `/app`) gets no guard nudge.

## 2. Gaps the specification leaves open, and what I assumed

**Detector scoring (not specified numerically).** Score = sum of per-family points, then caps and floors:
- Per score-moving family: `min(12, 6 + 2*(hits-1))`; decisive families `min(18, 10 + 2*(hits-1))`.
- One score-moving family caps at 40. Only rhythm kinds (40, 44) cap at 40; only sentence-length monotony
  (40) caps at 20.
- Short-document (<120 words) and long-document (≥400 words) floors and decisive floors per PRD.
- Bands by the PRD ranges. Confidence per PRD thresholds, with reason text of my own wording.

**Pattern lists the PRD leaves to the implementer.** Family 4 (stock compounds), 8 (clusters as listed),
69 (canonical phrases), 1/2/3/10–27 phrase lists follow the PRD examples. Family 3's "leading" is matched
only as "a leading" / "the leading" to avoid firing on "leading to". Family 6 (adjective chains) is a
heuristic: four or more comma/"and"-joined words with at least one stock adjective or adjective suffix.
Family 66 (homoglyphs) covers Cyrillic, Greek, and Armenian lookalikes of the listed letters only; Arabic
presentation forms are not in the map. Family 71 fires when at least 20% of six-word runs repeat.

**Markdown masking.** Front matter, CommonMark fenced code, inline code, two-or-more-line blockquote runs,
table rows, and badge lines are blanked to spaces (length and newlines preserved) before pattern scoring.
Character-layer counts (invisible, non-standard space, homoglyph, trailing whitespace) use the raw window.

**Words.** A word is a run starting with a letter or digit, containing letters, digits, apostrophes, and
hyphens (PRD definition).

**Line endings and whitespace.** CRLF and lone CR become LF before analysis and cleanup; U+2028/2029 become
LF. Cleanup also strips leading whitespace (not only leading blank lines) so the rescan reports no stray
whitespace at the start.

**Zero-width characters.** Each keep rule of FP-03 is implemented with its neighbour test (for example a
soft hyphen between two letters, a ZWJ beside a joining script or a symbol). Cleanup and counting share one
function so they always agree.

**`--ci` interval.** The PRD allows any resampling count and seed. Built as a heuristic (not a bootstrap):
half-width = clamp(30/√sentences, 2, 15) around the point score, reported with `score_ci_note` saying so.
Fewer than four sentences gives `null` with a note.

**Archives.** No archive-member size cutoff beyond the 4 MB file cap. EPUB chapter order comes from the
OPF spine (nav documents skipped); HTML is read with a lenient parser, so namespace irregularities do not
drop a chapter. XLSX cells are read in sheet-file order and then document order.

**Guard and hooks.**
- Eligible-file caps: 512 KB plain text, 4 MB for archives and notebooks (bytes, 1024-based). Timeouts 8 s
  and 15 s. Timeouts, a missing Python, no output, non-report output, and a missing numeric score are five
  distinct failure reasons in the ledger.
- Guard label list: first five fired labels (all fired findings, including advice). Ask text contains "fix".
- Ledger file names: `.prosecheck-ledger-<session>` with the session id sanitised to `[A-Za-z0-9_-]`,
  or `.prosecheck-ledger` when no session id is supplied. Stored as JSON, base names only.
- `apply_patch`: paths come from `*** Add File:`, `*** Update File:`, and `*** Move to:` lines (colon
  required). NotebookEdit falls back to `file_path` when `notebook_path` is absent.
- Stats: assistant rows are de-duplicated by `message.id` (streamed rows repeat usage); rows without an id
  count individually. Text fenced code is removed before scoring; the last 40,000 characters are scored.

**Contract content.** Live and exported contract text are identical. Full and strict add a detector step;
lite has none. The export's CLAUDE_PLUGIN_ROOT line is the one line naming that token together with the
words "skills" and "plugins". The exported section is wrapped in HTML-comment markers and a heading; a
second `init` finds it by either marker. The export does not contain this machine's path. It does contain the
token `CLAUDE_PLUGIN_ROOT`, which contains the letters "ROOT"; on this machine the user is `root`, so a
case-insensitive search for the user name will match that token.

**Cursor rule.** Shipped at `.cursor/rules/prosecheck.mdc`; front matter `globs` is one quoted,
comma-separated string of the eight prose globs. The body has no detector step and never uses the word
"detect". If the shipped file is missing, `init` writes a built-in copy.

**Doctor.** The Python check runs the bundled detector on one sample sentence and requires a numeric score.
The settings check creates the config folder if needed and tests write access.

**Unknown extensions.** The detector reads any other extension as plain text (the PRD says that is not a
plugin obligation). The guard ignores them.

## 3. Not done or not verified

- No Windows or macOS run. The code uses `path` APIs and `py` as a fallback interpreter name, but only
  Linux was exercised.
- Python 3.9 is the stated floor; I did not run the detector under 3.9.
- Score calibration against real corpora was not done (the PRD makes no calibration claim). The numeric
  formula above is my design and is only checked for the PRD's rules (bands, caps, floors, advice weight zero).
- The `skills/prosecheck/scripts/detect.py` fallback location is supported by the lookup code but no copy
  is shipped there.
- The bundled skill (`skills/prosecheck/SKILL.md`) is a host-agent instruction file; the detector does not
  rewrite text.

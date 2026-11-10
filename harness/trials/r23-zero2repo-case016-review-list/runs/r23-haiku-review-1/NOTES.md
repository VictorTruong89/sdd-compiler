# NOTES: prosecheck build

This file lists where the specification disagrees with itself, what the specification does not state, and what was built.
Spec files: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (IC), `spec/Hardware_Requirements.md` (HW).
`spec/CONFLICTS.md` was read as a reviewer's list only; every entry below was checked against the spec text itself.

Layout built:

- `scripts/detect.py`: the detector (Python standard library only).
- `hooks/prosecheck-activate.js`, `hooks/prosecheck-tracker.js`, `hooks/prosecheck-subagent.js`, `hooks/prosecheck-guard.js`, `hooks/prosecheck-stats.js`: the five plugin hooks named by the IC.
- `hooks/lib/prosecheck-core.js`: shared config, level, contract text, detector runner, and ledger helpers.
- `hooks/hooks.json`, `.claude-plugin/plugin.json`: plugin wiring.
- `commands/prosecheck.md`: the slash-command menu document (body `/prosecheck $ARGUMENTS`).
- `.cursor/rules/prosecheck.mdc`: the shipped Cursor rule that `init` copies.

The plugin root is the directory that holds `hooks/` (this repository), unless `CLAUDE_PLUGIN_ROOT` is set.

---

## 1. Conflicts and what was built

Each entry gives both sides with their location, then the choice. Where the IC defers a rule to the PRD (for example "which numbers are writing advice ... is the PRD's", IC line 57; "how long it is kept are the PRD's rules", IC line 91), the PRD wins. Where the IC states an interface or reply shape, the IC wins.

### 1.1 Where the usage message goes
- PRD FP-01 "Public entry" (lines 82-83): "The usage message goes to the error stream, so that standard output carries only reports."
- PRD FP-01 "Boundary / error behavior" (line 167) and IC `scripts/detect.py` > Usage (line 110): help "prints the usage message to standard output and exits 0."
- **Built:** `--help` / `-h` print usage on standard output and exit 0. Errors (unknown option, unreadable input, empty input) use the JSON error object on standard error only. Standard output stays empty on failure.

### 1.2 Floor for a single decisive finding
- PRD FP-01 "Normal behavior" (line 93): "A decisive finding always lifts the score to at least 45, whatever the confidence."
- PRD FP-01 "Normal behavior" (line 94): "A single decisive family at `none` or `low` confidence does not take that 45 floor."
- **Built:** the more specific rule (line 94). One decisive family lifts the score to 45 only at `moderate` or `high` confidence. Two or more distinct decisive families lift it to 65.

### 1.3 Hedge stacking
- PRD FP-01 "Normal behavior" (line 90): catalogue 54 is one of the twelve writing-advice numbers, "weight zero".
- PRD FP-01 "Family rules" (line 128): "Each sentence with stacked hedges adds to the score."
- **Built:** weight zero. Hedge stacking is reported as a finding and never moves the score (line 90 lists it explicitly).

### 1.4 Tailing-negation form of catalogue 17
- PRD FP-01 "Normal behavior" (line 91): "The tailing-negation form is score-moving."
- IC `scripts/detect.py` > Findings (line 148): "Both forms of catalogue 17 are writing advice and carry weight zero."
- **Built:** the PRD rule (IC line 57 defers this to the PRD). The tailing-negation form moves the score and is keyed `17_tailing_negation`. The parallelism form is weight zero and is keyed `17_negative_parallelism`. Only the PRD's count of fifty score-moving numbers is consistent with this.

### 1.5 No-break spaces
- PRD Terminology "Character cleanup" (line 30): "Every no-break space becomes an ordinary space."
- PRD FP-03 "What is normalized" (line 212): U+00A0 and U+202F are kept when they hold something together.
- **Built:** normalized everywhere except where line 212 keeps them (a digit on either side, before `: ; ! ? » › % €`, or after `« ‹`). Kept spaces are not counted (line 215).

### 1.6 Trailing spaces that form a markdown hard break
- PRD FP-03 "What is trimmed" (line 214): two trailing spaces "are a markdown hard break and are kept."
- PRD FP-03 "Boundary / error behavior" (line 223): the collapse "is required, not optional."
- **Built:** removed (line 223 is the explicit, more specific rule). Finding 68 counts them on the raw window, and cleanup removes them, so a rescan reports zero.

### 1.7 Zero-width characters
- PRD FP-01 "Normal behavior" (line 159): "A zero-width character inside the text is an invisible character."
- PRD FP-03 "What is removed" (line 211) and "Cleanup agrees with detection" (line 215): listed positions keep such characters, and kept characters are not counted.
- **Built:** the exceptions apply. A character is counted as invisible only where cleanup would remove it. The position rules are in `_invisible_removable` in `scripts/detect.py`.

### 1.8 `utm_source` values
- PRD FP-01 "Family rules," chat reference markup (line 131): "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
- PRD FP-01 "Family rules," tracking parameters (line 132): fires "only when that whole host name is one of those domains."
- **Built:** line 132 (the specific rule). Only the seven listed hosts fire 65. Other `utm_source` values do not.

### 1.9 Stop phrases
- PRD FP-04 "Normal behavior" (line 240): "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- PRD FP-06 "Normal behavior" (line 285) and IC `/prosecheck` > Stop phrases (line 411): the phrase must be the entire prompt.
- **Built:** the entire prompt only, case-insensitive. "please stop prosecheck, I want to keep it" is an ordinary prompt and leaves the level unchanged.

### 1.10 Precedence of `PROSECHECK_DEFAULT_MODE`
- IC "Host environment" (line 63): the variable "when it is set, it takes precedence over the stored level."
- IC "Naming conventions" (line 55): "Which level applies when nothing valid is stored is the PRD's rule (FP-04); the environment may supply one of those four words."
- PRD FP-04 "Boundary / error behavior" (line 246): the environment applies only "when nothing valid is stored."
- **Built:** the PRD rule (the IC defers to it at line 55). A valid stored level wins. The variable applies only when nothing valid is stored, and then `full` is the fallback.

### 1.11 Whether `.pdf` is a prose file
- PRD FP-06 "Normal behavior" (line 290): "rows appear after prose files, including `.docx` and `.pdf` deliverables, are saved."
- PRD Terminology (line 27), FP-02 "Boundary" (line 195), and non-goals (line 68): `.pdf` is not in the twenty formats and is logged as binary.
- **Built:** `.pdf` and `.rtf` are not prose. The guard records them as binary (not re-scored), and the detector treats them as empty input. The empty-ledger reply names `.docx` and `.pdf` as the spec requires.

### 1.12 How many file operands the detector accepts
- IC `scripts/detect.py` Signature (line 21): "at most one file operand."
- IC `scripts/detect.py` > Several file operands (line 180) and PRD FP-01 (line 168): two or more operands "still succeed."
- **Built:** two or more operands succeed. The detector reports on the first, and standard error gets one notice line that contains that operand.

### 1.13 Which operand is scanned
- IC `scripts/detect.py` Signature (line 106): "the last one is the file scanned."
- IC Several file operands (line 180) and PRD FP-01 (line 168): "the first is scanned."
- **Built:** the first operand (two of three statements agree, and the notice line in IC line 180 names it).

### 1.14 Paths scored from one `apply_patch` payload
- PRD FP-05 "Normal behavior" (line 264): "at most **16** distinct paths."
- IC "Post-tool-use reply" (line 260): "At most ten paths of one payload are scored."
- **Built:** sixteen, following the PRD. The IC defers which saves are scored to the PRD (line 234).

### 1.15 Records a session ledger keeps
- PRD FP-05 "Normal behavior" (line 265): "At most the newest **20** records are kept."
- IC "Plugin config and ledger" (line 91): "Each ledger keeps its newest **50** records."
- **Built:** twenty. The IC says what a ledger keeps is the PRD's rule.

### 1.16 How long a session ledger is kept
- PRD "Privacy" (line 57) and FP-06 (line 290): a ledger last modified more than seven days ago is gone.
- IC "Config filenames" (line 65): a ledger "untouched for more than one day is deleted at the next session start."
- **Built:** seven days, for both deletion at session start and omission from `show`. The IC says how long a ledger is kept is the PRD's rule (line 91).

### 1.17 Which transcript `stats` reads
- PRD FP-06 "Normal behavior" (line 292): "a named transcript wins over a newer one."
- IC `stats` > Transcript rows (line 650): "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
- **Built:** the named transcript (`transcript_path`) when it is supplied, as lines 646, 681 and PRD line 292 say. If it cannot be read, the reply has no count lines. The newest transcript under `projects` is used only when no path is named.

### 1.18 Minimum slice length for the session-prose score
- PRD FP-06 (line 292): printed "only when that slice ... is longer than **200** characters."
- IC `stats` > Reply (line 662): "longer than **500** characters."
- **Built:** 200 (PRD). The IC defers which rows count and how to the PRD (line 650 and FP-06).

### 1.19 Model-dialect vocabulary and the two-hit rule
- PRD FP-04 "Normal behavior" (line 236): each banned word "fires a machine-checked family ... (AI vocabulary; model-dialect vocabulary, which **needs two hits**, for its dialect words)."
- PRD FP-01 "Family rules" (line 101): model-dialect has no two-hit condition.
- **Built:** family 2 fires only at two or more hits in total, per the more specific FP-04 statement. So one standalone `genuinely` does not fire it, and the banned-word list is still enforced through family 1 for the words that belong there.

### 1.20 Whether the welcome may name prosecheck
- PRD FP-04 "Normal behavior" (line 235): the contract is "silent — never announce the contract, never name prosecheck."
- PRD FP-04 (line 238): the first-run welcome says "prosecheck is installed and on ... and that it is shown once."
- **Built:** the welcome names prosecheck, because it is a one-time user notice that the spec requires. The silence rule governs the host agent's replies, so the contract text itself never tells the agent to name prosecheck to the user.

---

## 2. Things the specification does not state (assumptions)

### 2.1 Scoring model
The PRD fixes the bands, the caps, the floors and the confidence labels, but not a base formula. Built:
- Each score-moving family fired contributes `weight * (1 + 0.1 * min(hits - 1, 6))`. Weight is 9 for ordinary families, 15 for decisive families (13, 47, 48, 50, 62-66), and 4 for rhythm kinds (40, 44). The sum is rounded and capped at 100.
- Caps and floors are applied in this order: single-family cap at 40 (lifted by a decisive floor); rhythm-only caps (40 at most, and 20 when only 40 fired); decisive floors (65 for two families, 45 for one at moderate or high confidence); short-document floors (under 120 words: 25 for two families, 45 for three or more, counted over the SHORT families 1-39, 47-51, 69); long-document floors (400 words or more: 25 for five families, 45 for six or more).
- Advice families (4, 19, 22, 41, 42, 46, 54, 55, 58, 60, 61, 68, and the parallelism form of 17) are reported and never counted.

### 2.2 Lexicons and regexes
The PRD lists words and shapes, and leaves some lists to the implementer. Built:
- Family 1 uses the listed words with common inflections (`delve`, `delves`, `delved`, `delving`, and so on), and matches whole words, case-insensitively.
- Family 3: `leading` fires only after `a`, `an` or `the` (a bare `leading` is common English). `premier` is matched as a whole word.
- Family 4 (hyphenated pairs) and family 69 (stock marketing phrases) use my own lists of common examples, since the PRD says the list is the implementer's choice.
- Family 6 (stacked adjectives): four or more comma-joined words, with at least one adjective (an adjective suffix or a stock adjective) and a non-adjectival last word.
- Family 8: each cluster fires when three or more distinct members occur. Hits are the occurrences of the members.
- Family 11: outlet names are capitalised words. A follower count is a number followed by `followers`.
- Family 47/48: the "praise then punctuation" patterns require one of `!`, `.`, `,` immediately after the praise phrase.
- Family 56 (boldface overuse) fires at two or more bold spans. The PRD does not give a number.
- Family 57 (emoji): the ranges U+1F000-U+1FAFF, U+2600-U+27BF, U+2B50 and U+2B55. Arrows are not included.
- Family 63 (placeholder): the listed slot words, a few common field names, an all-capitals bracket of three or more letters, `{{ }}`, a run of three or more `x`, and `lorem ipsum`.
- Family 71 (degenerate repetition) fires when at least 20% of the six-word runs occur more than once (the PRD says "on the order of a fifth or more").

### 2.3 Text segmentation and counting
- A word is a run of letters, digits, apostrophes and hyphens, with at least one letter or digit (PRD: "runs of letters, digits, apostrophes, and hyphens").
- A sentence ends at `.`, `!` or `?` followed by whitespace, and at line breaks.
- A paragraph is separated by a blank line.
- CRLF and lone CR are normalized to LF before anything else, and that normalized text is what `scanned_chars` counts.
- Rhythm (families 40, 41, 44) uses sentences and paragraphs as above.

### 2.4 Masking before analysis
The PRD says certain constructs produce no findings. Built as line-level masking before analysis: YAML front matter (first block only), CommonMark fenced code (including unclosed fences), runs of two or more blockquote lines, lines starting with `|` containing two or more pipes, separator rows, badge-only lines, and inline code spans.

### 2.5 Character layer
- The scrub order is: remove invisible characters, normalize spaces, fold lookalikes, then trim. Analysis runs on the scrubbed text. Counts (62, 66, 67, 68) are taken on the raw window, so a rescan of cleaned text reports zero.
- Homoglyph folding covers a set of Cyrillic, Greek and Armenian letters that look like Latin letters. Arabic presentation forms are not in the map, which is a gap. Tokens containing `://` or starting with `www.` are excluded from both counting and folding.
- A TAG-character run is kept only when it follows an emoji-like base (the emoji tag sequence). Variation selectors are kept after emoji, symbols, or CJK ideographs, or before U+20E3. Mongolian selectors are kept after Mongolian letters. Khmer inherent vowels are kept beside Khmer. ZWJ and ZWNJ are kept beside joining letters or symbols. ZWSP is kept beside CJK, Thai, Lao, Khmer, Myanmar or kana. Bidi controls are kept only when the document contains RTL script.
- Line and paragraph separators (U+2028, U+2029) become LF.
- Trimming removes leading whitespace from the start of the text, including first-line indentation, because finding 68 counts any whitespace before the first character.
- `--clean` cleans the whole extracted text, not just the window.

### 2.6 Window and truncation
- The window is the first 262,144 characters of extracted prose, after newline normalization. `truncated` means the extracted text is longer than that.
- Finding 62 and the other character-layer findings use the same window.

### 2.7 Resampled interval (`--ci`)
Not specified. Built: the sentences are split into four contiguous chunks, each chunk is scored, and the full text is scored too. `score_ci` is `[min, max]` over those five scores, bounded so it contains the point score. It is `null` with a note when there are fewer than four sentences. The scoring is deterministic.

### 2.8 Extraction details
- `.docx`: visible text of `w:p` paragraphs (`w:t`, tabs and breaks), in document order.
- `.pptx`: `a:p` paragraphs per slide, slides in numeric order.
- `.xlsx`: sheets in workbook order (through relationships), one line per non-empty cell; shared strings, inline strings, and `t="str"` cells are read.
- `.odt`, `.odp`, `.ods`: `text:p` and `text:h` blocks, with `text:s`, `text:tab`, `text:line-break` handled.
- `.epub`: spine order from the OPF (nav documents skipped), with script, style, head and nav content excluded and inline markup stripped.
- `.ipynb`: markdown cells joined with line breaks. A malformed notebook yields empty prose.
- Empty lines inside archive text are dropped.
- The detector does not enforce size caps. The plugin enforces them (PRD FP-05 and FP-06), with the sizes given in the spec.

### 2.9 Hooks and command behaviour
- **Plugin tree skip.** The guard skips files under the plugin root, per IC `CLAUDE_PLUGIN_ROOT`. In this repository the plugin root is `/app`, so a prose file saved under `/app` is not scored unless `CLAUDE_PLUGIN_ROOT` points elsewhere. This follows the spec literally and may surprise a user who keeps prose in the repo.
- Instruction-file names (`claude.md`, `agents.md`, `skill.md`, `memory.md`, and their `.local.md` forms) are matched case-insensitively. A stem match skips a non-prose extension (for example `claude.json`).
- `apply_patch` paths: `*** Add File:`, `*** Update File:`, and `*** Move to:` lines, with the path taken after the colon and trimmed. The body is read from `tool_input.command` (or `input`/`patch`).
- Ledger records hold the base name, kind (`scored`, `skip`, `binary`, `failed`), score, band, hook phrase, truncated flag, flagged flag, up to five labels, and a timestamp. The ledger file is `.prosecheck-ledger-<session_id>` (sanitized), or `.prosecheck-ledger` with no session id.
- Guard labels are capped at 5 per nudge. `check` lists up to 8 tells. `show` lists up to 5 labels per row.
- `check` and the guard resolve relative paths against the payload's `cwd`, or the process directory when no `cwd` is given. `check` strips one pair of surrounding quotes and one leading `@`, in either order.
- `init` runs in the process's current directory. The export is portable: it names no machine path and no user name. Its detector line is `scripts/detect.py` relative to the plugin, and at `strict` the cleanup line also uses the relative path.
- `stats`: assistant messages are deduplicated by `message.id` before tokens are summed, because a single message can appear in several transcript rows. Only `assistant` rows count (PRD FP-06). The prose slice removes fenced code and keeps the last 40,000 characters.
- `doctor`: the Python check runs the bundled detector on a short sample through standard input. It reports success only when a numeric score comes back.
- Levels: `off` makes the activate and subagent hooks print nothing; the prompt hook prints nothing for ordinary prompts while off; the guard does nothing at `off` or `lite`.
- The first-run welcome is printed when no `.prosecheck-active` flag exists. Session start then writes the effective level to the flag, so later hooks see it.

### 2.10 Things not built
- No bundled skill file (the rewrite instructions are an agent-side concern, and the PRD says they are not a feature point).
- No `install/prosecheck-command.md`. The command file is `commands/prosecheck.md`, which the spec allows.
- No status-line helper, demo, documentation checker, or evaluation script (all listed as non-goals).

---

## 3. How this was checked

- `scripts/detect.py`: help, unknown option (exit 2), empty input (exit 1), unreadable path (exit 1), corrupt zip (exit 1), multi-file notice, `--`, `--clean`, `--ci`, UTF-8 BOM, UTF-16 BOM, CRLF, all six zip-based formats and the notebook. Character-layer rescan after cleanup is zero. Clean prose scores 0; an AI-style sample scores into the heavy band. Determinism across `PYTHONHASHSEED` values. A 512 KB single-paragraph input runs in under a second.
- Hooks: first-run welcome and flag write; second start prints only the contract; router replies for `help`, `doctor` (namespaced and not), `status`, `lite`/`full`/`strict`/`off`/`on`, stop phrases, unknown words; `check` (quoted and `@` paths, directory, missing, PDF, oversize, no Python); `show` (empty, scored, binary, failed, size skip); guard (flagged nudge, unflagged silence, missing file, PDF, `.py`, `apply_patch`, lite and off silence, strict threshold); `init` (write, already present, off, Cursor rule); `stats` (named transcript, missing transcript); subagent envelope; malformed input and empty input to every hook (exit 0).
- Contract shell rules: a script checked all 238 rules from the spec (banned words, `source code` sentence rule, 40/20 targets, `--clean` placement, lite exclusions, export portability, CLAUDE_PLUGIN_ROOT line, Cursor rule front matter and body).

Not verified: the hidden tests. Only the spec and my own tests were used.

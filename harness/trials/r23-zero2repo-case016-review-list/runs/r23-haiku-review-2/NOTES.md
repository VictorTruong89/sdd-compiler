# NOTES: prosecheck 0.9.3 build notes

This file records (1) every disagreement between the specification files, with what each side says and where, and what was built; (2) what the specification does not state and the assumption made; and (3) the layout of the code.

References: `PRD` = `spec/Full_PRD.md`, `IC` = `spec/Interface_Contract.md`, `HW` = `spec/Hardware_Requirements.md`. Line numbers are those of the files as delivered. `spec/CONFLICTS.md` is the reviewer's list; every entry in it is covered below, plus a few disagreements it does not list.

---

## Part 1. Disagreements and what was built

### C1. Where the usage message is printed
- **PRD FP-01, "Public entry" (line 82–83):** "The usage message goes to the error stream, so that standard output carries only reports."
- **PRD FP-01, "Boundary / error behavior" (line 167):** "Help (the help switch or the short help alias) prints the usage message to standard output and succeeds."
- **IC `scripts/detect.py` > Usage (line 110):** `--help` and `-h` "write the usage message to standard output and exit 0".
- **Built:** `--help` and `-h` print usage to **standard output** and exit 0 (two statements against one; the PRD line 167 and IC agree). No usage text is written to the error stream.

### C2. Floor for a single decisive finding
- **PRD FP-01, "Normal behavior" (line 93):** "A decisive finding always lifts the score to at least 45, whatever the confidence."
- **PRD FP-01, "Normal behavior" (line 94):** "A single decisive family at `none` or `low` confidence does not take that 45 floor."
- **Built:** the line-94 rule. One decisive family raises the score to at least 45 only when confidence is `moderate` or `high`. (Line 94 is the more specific statement.)

### C3. Whether hedge stacking changes the score
- **PRD FP-01, "Normal behavior" (line 90):** catalogue 54 is one of the 12 writing-advice numbers, "weight zero".
- **PRD FP-01, "Family rules" (line 128):** "Each sentence with stacked hedges adds to the score."
- **Built:** 54 is writing advice (weight zero). It is reported as a finding with its count but never moves the score. Line 90 lists 54 explicitly; line 128 is the family description.

### C4. Whether the tailing-negation form of catalogue 17 moves the score
- **PRD FP-01, "Normal behavior" (line 91):** "The **tailing-negation form** is score-moving."
- **IC `scripts/detect.py` > Findings (line 148):** "Both forms of catalogue 17 are writing advice and carry weight zero."
- **Built:** the tailing-negation form (`17_tailing_negation`) is **score-moving**, and the parallelism form (`17_negative_parallelism`) is writing advice. The PRD defines the two forms and its list of 12 advice numbers (line 90) does not include 17, so the PRD is internally consistent and the IC statement is the outlier.

### C5. Whether every no-break space is turned into a space
- **PRD Terminology, "Character cleanup" (line 30):** "Every no-break space becomes an ordinary space."
- **PRD FP-03, "What is normalized" (line 212):** a no-break space (U+00A0) or narrow no-break space (U+202F) is kept when it holds something together: a digit on either side, before `:` `;` `!` `?` `»` `›` `%` `€`, or after `«` `‹`.
- **Built:** the specific keep rule of line 212 applies; every other no-break space becomes U+0020 in cleanup and is counted in `nonstandard_spaces`. The kept ones are neither counted nor changed.

### C6. Whether a markdown hard break's trailing spaces are kept
- **PRD FP-03, "What is trimmed" (line 214):** "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
- **PRD FP-03, "Boundary / error behavior" (line 223):** "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required, not optional."
- **Built:** line 223 (removed). It is the later and explicitly "required" statement. Cleanup strips spaces and tabs at the end of every line.

### C7. Whether every zero-width character in the text is invisible
- **PRD FP-01, "Normal behavior" (line 159):** "A zero-width character inside the text is an invisible character."
- **PRD FP-03, "What is removed" (line 211) and "Cleanup agrees with detection" (line 215):** some zero-width joiners, non-joiners, zero-width spaces, and variation selectors are kept in listed positions and "a character the scrub keeps is not counted as an invisible character."
- **Built:** the exceptions of line 211 apply. A zero-width character that cleanup keeps (for example a ZWJ between Hebrew letters or inside an emoji sequence) is neither removed nor counted. Line 129 already allows this exception.

### C8. Whether any `utm_source` value triggers catalogue 65
- **PRD FP-01, "Family rules," chat reference markup (line 131):** "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
- **PRD FP-01, "Family rules," AI tracking parameters (line 132):** it "fires only when that whole host name is one of those domains."
- **Built:** the domain list of line 132 (`chatgpt.com`, `chat.openai.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`, `poe.com`). Line 131 is a summary sentence; line 132 is the rule.

### C9. Whether `stop prosecheck` must be the whole prompt
- **PRD FP-04, "Normal behavior" (line 240):** "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- **PRD FP-06, "Normal behavior" (line 285):** the phrases store `off` "as the entire prompt"; "the same words with anything else before or after them are an ordinary prompt."
- **IC `/prosecheck` > Stop phrases (line 411):** "The entire prompt `stop prosecheck`, or the entire prompt `prosecheck off`" (agrees with FP-06).
- **Built:** the entire-prompt rule (FP-06 and IC agree, two against one). The prompt "please stop prosecheck, I want to keep it" is an ordinary prompt and does not change the level.

### C10. Precedence of the `PROSECHECK_DEFAULT_MODE` environment variable
- **PRD FP-04, "Boundary / error behavior" (line 246):** "When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words, in which case that word is used."
- **IC "Naming conventions" > Host environment (line 63):** `PROSECHECK_DEFAULT_MODE` "when it is set, it takes precedence over the stored level."
- **Built:** the PRD rule. A valid stored level wins; the environment variable is used only when nothing valid is stored; otherwise `full`. (The PRD is the product definition; the IC sentence is the outlier.) On the first session start with no flag file, the resolved level is written to the flag so later hooks see it.

### C11. Whether `.pdf` is a prose file
- **PRD FP-06, "Normal behavior" (line 290):** "rows appear after prose files, including `.docx` and `.pdf` deliverables, are saved."
- **PRD Terminology, "Prose file" (line 27) and FP-02 "Boundary" (line 195):** `.pdf` and `.rtf` are not among the twenty formats; they are "logged as binary".
- **IC `show` > Empty ledger (line 582):** the empty-ledger reply must contain `.docx` and `.pdf`.
- **Built:** `.pdf` and `.rtf` are not prose and are never scored. The guard records them as binary (`not re-scored`) on the ledger. The empty-ledger message names `.pdf` as an example only because the IC requires it. `check` on a `.pdf` says there is no readable text.

### C12. How many file operands the detector accepts
- **IC `scripts/detect.py` > Signature (line 21):** "optional switches and at most one file operand."
- **IC `scripts/detect.py` > Several file operands (line 180), PRD FP-01 "Boundary" (line 168):** two or more operands still succeed.
- **Built:** any number of operands. Two or more succeed, scan the first, and write one notice line to standard error.

### C13. Which operand is scanned when several are given
- **IC `scripts/detect.py` > Signature (line 106):** "When several operands are given, the last one is the file scanned."
- **IC `scripts/detect.py` > Several file operands (line 180), PRD FP-01 (line 168):** "the first is scanned".
- **Built:** the **first** operand (two statements against one). The notice names it.

### C14. Maximum number of paths in one `apply_patch` payload
- **PRD FP-05, "Normal behavior" (line 264):** "at most **16** distinct paths."
- **IC Post-tool-use reply (line 260):** "At most ten paths of one payload are scored."
- **Built:** 16 (PRD, the spec that defines the guard). The guard scores the first 16 distinct paths.

### C15. Number of records a session ledger keeps
- **PRD FP-05, "Normal behavior" (line 265):** "At most the newest **20** records are kept."
- **IC "Plugin config and ledger" (line 91):** "Each ledger keeps its newest **50** records."
- **Built:** 20 (PRD).

### C16. How long a session ledger is kept
- **PRD Non-functional constraints, "Privacy" (line 57), and FP-06 (line 290):** a ledger "more than seven days" old is gone; seven days old or younger is kept.
- **IC "Config filenames" (line 65):** "A ledger untouched for more than **one day** is deleted at the next session start."
- **Built:** seven days (PRD), applied both to deletion at session start and to what `show` lists.

### C17. Which transcript `stats` reads when a newer one exists
- **PRD FP-06, "Normal behavior" (line 292):** "a named transcript wins over a newer one."
- **IC `stats` > Transcript rows (line 650):** "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
- **Built:** the named `transcript_path` wins (PRD; the IC statements at lines 646 and 681 also say the named one is read). A named path that cannot be read gives no counts and **no fallback** to another transcript. Without a named path, the newest `.jsonl` under `CLAUDE_CONFIG_DIR/projects` is read.

### C18. Minimum slice length for the session-prose score
- **PRD FP-06, "Normal behavior" (line 292):** the score is printed "only when that slice, with surrounding whitespace trimmed, is longer than **200** characters."
- **IC `stats` > Reply (line 662):** "When the scored slice is longer than **500** characters, the reply contains `session prose ai_tell_score`."
- **Built:** 200 (PRD).

### C19. Whether one use of a model-dialect word fires the family
- **PRD FP-04, "Normal behavior" (line 236):** "Every word on that banned-vocabulary list ... fires a machine-checked family ... (AI vocabulary; model-dialect vocabulary, which **needs two hits**, for its dialect words)."
- **PRD FP-01, "Family rules," model-dialect vocabulary (line 101):** no two-hit condition is given.
- **Built:** model-dialect vocabulary (2) needs **two or more hits** before it is reported. A single "genuinely" or "nuanced" is therefore not a finding. Line 236 is the only statement that gives the condition. The banned-vocabulary words that belong to family 2 are still reported when they occur twice.

### C20. Whether the welcome can name prosecheck when the contract forbids it
- **PRD FP-04, "Normal behavior" (line 235):** the contract is "silent — never announce the contract, never name prosecheck, never report a score ..."
- **PRD FP-04, "Normal behavior" (line 238), IC `hooks/prosecheck-activate.js` > Welcome block (line 201):** the first-run welcome says "prosecheck is installed and on" and names the four commands.
- **Built:** the welcome is delivered once, on a fresh install, as the spec requires, and the welcome itself names prosecheck. The silence rule in the writing contract governs what the agent says in its replies. The contract text itself does name prosecheck in its title and its silence rule, because the spec asks the contract to say "never name prosecheck".

### Disagreements the reviewer did not list

- **D1. "A single sentence that opens with one of the transition words of 37 already fires transition clusters"** (PRD FP-01, family 36 description, line 116). Read literally this contradicts family 37's "two or more sentence-opening transitions in one paragraph". **Built:** family 37 as stated (two or more per paragraph). The sentence in family 36 is not implemented as a separate rule.
- **D2. Catalogue 56, boldface overuse.** PRD line 150 gives no threshold ("bold spans ... in prose"), so a single bold span would fire it. **Built:** three or more bold spans (a threshold is required for "overuse"). Documented as an assumption (Part 2).
- **D3. The guard's label cap.** The PRD gives "up to five fired pattern labels" for the nudge (line 260); the IC says "at most the guard label cap the PRD gives" (line 257). **Built:** five. The `check` tells line caps at eight, `show` rows at five, as the PRD says.
- **D4. Instruction-file skip and the plugin root.** PRD FP-05 (line 263) and IC `CLAUDE_PLUGIN_ROOT` (line 62) say files inside the plugin's own install tree are skipped, and that the default plugin root is the directory containing `hooks/`. In this repository that is `/app`, so with `CLAUDE_PLUGIN_ROOT` unset, **any saved prose file under `/app` is skipped by the guard**. This follows the spec literally. Set `CLAUDE_PLUGIN_ROOT` to point elsewhere if prose files under `/app` must be scored.

---

## Part 2. What the specification does not state (and what was assumed)

### Detector (`scripts/detect.py`)
- **Score formula.** The PRD gives the caps, floors, bands, and rhythm rules but no per-family weight. **Assumed:** each score-moving family contributes `14 × min(1, 0.45 + 0.2 × (hits − 1))`; the sum is rounded and clipped to 0–100; then the caps and floors of FP-01 are applied in that order (rhythm cap, single-family cap, decisive floors, short- and long-document floors). The result is deterministic.
- **Paragraphs and sentences.** Sentences end at `.`, `!`, `?` followed by whitespace or the end of a line, or at a line end. Paragraphs are blank-line-separated runs; if a text has no blank line at all, each line is a paragraph. Words are runs of letters and digits joined by apostrophes or hyphens.
- **Markdown masking.** Front matter, fenced code (CommonMark closing rules), inline code spans, blockquote runs of two or more lines, table rows (lines beginning with `|`), and badge-only lines are blanked before pattern rules run. Character-layer rules (invisible, homoglyph, non-standard space, trailing whitespace) run on the scan window itself, unmasked. Trailing whitespace is advice (weight zero), so the code-block effect does not change the score.
- **Family 2 threshold.** Two hits (see C19).
- **Family 6 (stacked adjectives).** Four or more words in a comma or `and` chain, followed by a noun, where at least one chained word is a stock evaluative adjective or has an adjective suffix. The noun is not checked.
- **Family 8 (synonym cycling).** A cluster fires when three or more of its members occur as whole words (singular or plural). The count is all occurrences of cluster members.
- **Family 3 (promotional).** Phrase list as written; the "three sentences opening with a marketing verb" rule counts those sentences.
- **Family 4 (hyphenated pairs), 22 (persuasive tropes), 19 (filler), 69 (marketing collocations).** Which compounds are on the list is the implementer's choice (PRD line 136, 156). The lists used are those written in the code.
- **Family 25 (question-answer).** A question opening with an auxiliary or modal verb, no more than 100 characters, followed at once by a one-word answer.
- **Family 33 (inline-header list).** A line or list item beginning with a bold run closed by a colon.
- **Family 34 (bullet injection).** Fires only when the document has no heading and has at least one all-bullet paragraph alongside two or more prose paragraphs.
- **Family 35 (fragmented header).** The following non-blank plain line has at most four words and shares a word of three or more letters with the heading.
- **Family 40 and 44 (rhythm).** Sentence-length CV below 0.35 with at least three sentences; paragraph-length CV below 0.4 with at least four paragraphs. Measured on words.
- **Family 41 (alternation).** Six or more consecutive sentences whose lengths alternate in direction at each step, each step at least six words.
- **Family 42 (opener repetition).** A paragraph of at least three sentences in which some first-two-word opener occurs three or more times.
- **Family 46 (semicolons).** Only documents of 300 words or more; fires when there is no semicolon and fewer than two parentheses per 1,000 words.
- **Family 55 (contraction absence).** First-person words at 3% or more of all words, at least 40 words, and at least 80% of the contractible forms written out.
- **Family 59 (title case).** A heading of three or more words, not all capitals, starting with a letter, with at least two major words, all major words capitalised.
- **Family 61 (year ranges).** `YYYY-YYYY` with the earlier year first. Advice (weight zero).
- **Family 70 (decorative rules).** At least three standalone rule lines in a document of 24 lines or more.
- **Family 71 (degenerate repetition).** Six-word runs; fires when repeated runs make up 20% or more of all six-word runs.
- **Homoglyph map.** Cyrillic, Greek, and Armenian letters drawn like the Latin letters in the spec's list. Arabic-presentation lookalikes are not in the map. A run qualifies only if it has ASCII letters, at least one lookalike, and no other non-ASCII letter.
- **Invisible-character set.** Unicode format characters (`Cf`) and control characters other than tab, line feed, and carriage return; the tag block; variation selectors; the Mongolian selectors and a few default-ignorable filler codepoints. Positions where the character does a job follow FP-03 as far as the neighbours can tell (nearest visible character before, one character after).
- **Cleanup scope.** Cleanup runs on the **whole** extracted text, not only the window. CRLF is turned into LF first.
- **`--ci` method.** A bootstrap over sentences: 100 resamples with a fixed seed (20240601), 5th and 95th percentiles. Family hits from sentence-located matches move with their sentence; document-level families stay fixed. This is an implementation choice for "a low/high interval".
- **Multiple file operands.** Only the first is scanned (C13). The notice goes to standard error.
- **Operand `-`.** Treated as an unknown option (exit 2), because FP-01 says any argument beginning with `-` before `--` is unknown. Standard input is read only when there is no operand.
- **Archive members.** A member larger than 64 MB is treated as absent; an archive member that cannot be parsed yields no text. An unreadable zip is a `cannot read input:` error.
- **Unknown extensions** are read as plain text by the detector. The guard does not score them.
- **Errors.** Every failure prints exactly one JSON error line on standard error. An unexpected internal exception prints `{"error": "internal error: <type>"}` and exits 1; no traceback is printed.

### Plugin (`hooks/`)
- **Shared module.** The hooks share `hooks/lib/core.js`. It is not a named entry, but it lives under `hooks/`.
- **Plugin root.** `CLAUDE_PLUGIN_ROOT` if set, else the directory containing `hooks/` (D4).
- **Config directory.** `CLAUDE_CONFIG_DIR` if set, else `~/.claude`.
- **Flag and first run.** The flag file `.prosecheck-active` holds one word. On a session start with no flag file, the resolved level is written to it and the welcome is printed. A later start prints no welcome.
- **Ledger.** `.prosecheck-ledger-<session id>`, with the session id reduced to letters, digits, and underscores. Without a session id the file is `.prosecheck-ledger`. The file is a JSON array of at most 20 records, newest last. Records hold the base name only, never the document text or the full path.
- **Pruning.** Ledger files older than seven days are deleted at session start (C16).
- **Guard threshold and levels.** Threshold 40 at `full`, 20 at `strict`. `lite` and `off` score nothing.
- **Guard path rules.** Paths containing `node_modules` or `.git` are skipped. Instruction files (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `MEMORY.md`, and their `.local` forms) are skipped, with or without an extension. Relative paths resolve against the payload `cwd`, falling back to the hook's working directory.
- **Caps.** Plain text over 524,288 bytes and archives or notebooks over 4,194,304 bytes are recorded as skipped, not scored. Timeouts: 8 s for plain text, 15 s for archives and notebooks.
- **Failure reasons.** `Python not found`, `detector timed out`, `detector output was not a report`, `report has no numeric score`, `detector produced no usable result`, and `cannot read: file is not on disk`.
- **Check path resolution.** The prompt-submit payload carries no `cwd` in the IC, so `check` resolves a relative path against the hook's working directory.
- **Stats.** Assistant rows are de-duplicated by `message.id`, so a message split across several rows counts once. The prose slice is the last 40,000 characters after fenced code is removed.
- **Stop phrases** match the whole trimmed prompt, case-insensitively.
- **Init.** AGENTS.md is written between `<!-- prosecheck:contract:start -->` and `<!-- prosecheck:contract:end -->`. The export names no install path and no user name. The export's detector line names `CLAUDE_PLUGIN_ROOT` together with `skills` and `plugins` on one line, at `full` and `strict`.
- **Cursor rule.** `.cursor/rules/prosecheck.mdc` is shipped at the plugin root and copied into a project on `init`. Its globs are exactly the eight prose globs.
- **Subagent.** The subagent hook returns the same contract as session start (live form, naming the detector path).
- **`doctor` closers.** The "healthy" closer names the 512 KB and 4 MB caps, the 262,144-character window, and the `show` command in the form the user typed.
- **Shipped files not named in the spec.** `.claude-plugin/plugin.json` (version 0.9.3), `hooks/hooks.json` (wires the five events to the hook files), `commands/prosecheck.md` (the menu document; its body is `/prosecheck $ARGUMENTS`), and `skills/prosecheck/SKILL.md` (the rewrite instructions for the host agent).

---

## Part 3. Layout

```
scripts/detect.py            detector: extraction, character layer, 71-pattern catalogue, score, report, cleanup
hooks/lib/core.js            shared logic for all hooks (config, levels, contract, guard, ledger, replies)
hooks/prosecheck-activate.js session-start hook
hooks/prosecheck-tracker.js  prompt-submit hook and /prosecheck router
hooks/prosecheck-subagent.js subagent-start hook
hooks/prosecheck-guard.js    post-tool-use hook (saved-file guard)
hooks/prosecheck-stats.js    stats hook (answers /prosecheck stats)
hooks/hooks.json             hook wiring for the host
commands/prosecheck.md       slash-command menu document
.claude-plugin/plugin.json   plugin manifest
.cursor/rules/prosecheck.mdc shipped Cursor rule (copied by init)
skills/prosecheck/SKILL.md   rewrite guidance for the host agent
NOTES.md                     this file
spec/                        unchanged
```

No network client, no telemetry, no third-party dependency. Python 3.9 or newer is needed for the detector (the code uses no 3.10+ syntax); Node.js is needed for the hooks.

## Part 4. Verification performed

- Detector: plain text, all twenty formats (synthetic archives for docx, pptx, xlsx, odt, epub, ipynb), UTF-8 and UTF-16 with BOM, CRLF, invisible and homoglyph detection, cleanup, `--ci`, help, unknown option, empty input, unreadable input, invalid zip, two operands, and a stress document that triggers most families with no internal error. A 1 MB input with `--ci` finished in about 1 second; a 480 KB invisible-heavy input in about 1 second.
- Hooks: session start (welcome once, then contract), subagent envelope, prompt-submit router (every subcommand, both spellings, stop phrases, unknown word), guard (Write, Edit, apply_patch with add/update/move, binary, missing path, Python missing), `show`, `check` (scored, missing, directory, binary, Python missing, no path), `doctor` (all OK, mode off, Python missing), `stats` (transcript with duplicate message ids, missing named transcript), `init` (off, full, repeat, Cursor rule).
- Not verified here: the host agent's own hook plumbing (Claude Code, Cursor, or other hosts), and the hidden acceptance tests. Score numbers are a deterministic triage heuristic built from the spec's rules; the specific weights are the assumption listed in Part 2.

# NOTES — prosecheck 0.9.3 build

Build of the specification in `spec/` (Full PRD, Hardware Requirements, Interface Contract).
Nothing under `spec/` was changed. There is no build step; the code runs from `/app`.

## Layout

| Path | What it is |
| --- | --- |
| `scripts/detect.py` | The detector (Python 3.9+ standard library only). |
| `hooks/prosecheck-activate.js` | Session-start hook (contract, first-run welcome). |
| `hooks/prosecheck-tracker.js` | Prompt-submit hook and `/prosecheck` router. |
| `hooks/prosecheck-subagent.js` | Subagent-start hook (contract in the SubagentStart envelope). |
| `hooks/prosecheck-guard.js` | Post-tool-use hook (saved-file guard and ledger). |
| `hooks/prosecheck-stats.js` | Stats hook (same reply as `/prosecheck stats`). |
| `hooks/prosecheck-common.js` | Shared Node module used by all hooks (not a hook itself). |
| `hooks/hooks.json` | Host wiring for the five hooks. |
| `commands/prosecheck.md` | Shipped `/prosecheck` menu document (`$ARGUMENTS` template). |
| `.cursor/rules/prosecheck.mdc` | Shipped Cursor rule (prose globs only, no detector step). |
| `.claude-plugin/plugin.json` | Plugin manifest. |
| `skills/prosecheck/SKILL.md` | Short bundled skill for rewrite guidance. |

No network access, no third-party packages, no compiled code. Checked with `python3`
3.13 and Node 22 only. Windows and macOS were not run.

## Spec conflicts and the choice made

The rule I used: where a behaviour is stated in both the PRD and the Interface Contract, the
PRD's behaviour wins. Interface-only details (names, shapes, file paths) are followed as written.

1. **Ledger size.** PRD FP-05: "At most the newest 20 records are kept." Interface, "Plain
   plugin config and ledger": "Each ledger keeps its newest 50 records." Built: **20**.
2. **Ledger age.** Interface, "Config filenames": "A ledger untouched for more than one day is
   deleted at the next session start." PRD, Privacy and FP-06 `show`: a ledger seven days old or
   younger is kept, and a ledger more than seven days old is not listed. Built: ledgers older than
   **seven days** are deleted at session start and are not listed by `show`.
3. **Session-prose score threshold (`stats`).** PRD FP-06: printed only when the slice is "longer
   than 200 characters". Interface, `stats`: "longer than 500 characters". Built: **200**.
4. **Which transcript `stats` reads.** PRD FP-06: "a named transcript wins over a newer one."
   Interface, `stats`: "When the projects folder holds a transcript newer than the named one, the
   newer transcript is read." Built: the **named** transcript (`transcript_path`) wins.
5. **apply_patch path cap.** PRD FP-05: "at most **16** distinct paths." Interface, `tool_input`
   / post-tool-use: "At most **ten** paths of one payload are scored." Built: **16**.
6. **Several file operands.** Interface, `scripts/detect.py` Signature: "When several operands are
   given, the last one is the file scanned." Interface, "Several file operands", and PRD FP-01:
   "the first file is scanned". Built: the **first** operand is scanned, with the notice on stderr.
7. **Stop phrases.** PRD FP-04: "A prompt that contains `stop prosecheck` anywhere switches the
   tool off." PRD FP-06 and Interface: the phrase must be the **entire** prompt; anything before or
   after it is an ordinary prompt. Built: **whole prompt only** (case-insensitive).
8. **Single decisive family and the 45 floor.** PRD FP-01 says a decisive finding "always lifts
   the score to at least 45, whatever the confidence." The same section then says "A single
   decisive family at `none` or `low` confidence does not take that 45 floor." Built: the floor
   applies only at **moderate or high** confidence (the more specific rule).
9. **Trailing spaces in cleanup.** PRD FP-03 says two trailing spaces (markdown hard break) "are
   kept", then "Trailing whitespace at end of line is removed even when two spaces were meant as a
   markdown hard break. That collapse is required." Built: **removed** (the required collapse).
10. **No-break spaces.** PRD glossary: "Every no-break space becomes an ordinary space." PRD FP-03
    keeps a no-break space that holds something together (digit on either side, before `: ; ! ? » › % €`,
    after `« ‹`). Built: the FP-03 keep rules (the more specific statement).
11. **Usage message stream.** PRD FP-01 Public entry: "The usage message goes to the error
    stream." PRD FP-01 Boundary and Interface `--help`: usage goes to **standard output** and exit 0.
    Built: `--help`/`-h` print usage to stdout (exit 0). An unknown option prints only the JSON error.
12. **Hedge stacking (54).** PRD family rule says "Each sentence with stacked hedges adds to the
    score", but the writing-advice list (FP-01) names 54 as weight zero. Built: **weight zero**
    (the explicit list wins).
13. **Model-dialect family (2) threshold.** FP-04 says dialect words "need two hits"; the family
    rule in FP-01 states no threshold. Built: family 2 fires at **two or more** hits.

## Unstated items and assumptions

Scoring (the PRD gives caps and floors, not a formula):
- Each score-moving family contributes `8 + 2 × (extra hits, up to 8)`, capped at `+8` over the base
  (so 8–16 points). Decisive families use base 16. The total is capped at 100.
- Caps applied before floors: one score-moving family → 40; only rhythm kinds → 40; only sentence-length
  monotony (40) → 20. Floors from the PRD (short/long documents, decisive families) are applied after.
- Writing-advice findings (4, 19, 22, 41, 42, 46, 54, 55, 58, 60, 61, 68, and 17's parallelism form)
  are reported with weight zero.
- Word counts use runs of letters, digits, apostrophes, and hyphens in text with code blanked.
- Confidence reasons are my wording.

Detection details:
- Paragraphs are blank-line-separated blocks; sentences end at `.`, `!`, `?` followed by whitespace.
  Heading lines are not sentences.
- Code and quoted structures are blanked to spaces (same length, so samples stay contiguous text
  of the scanned window): YAML front matter, CommonMark fenced blocks, inline code, two or more
  consecutive blockquote lines, markdown table rows, badge-only lines. The character layer (62, 66, 67,
  68) runs over the whole window, consistent with cleanup.
- Where a family list is "the implementer's choice" I chose the entries: hyphenated compounds (4),
  promotional phrases (3), canonical slop phrases (69), placeholder keywords (63), and the
  stock-adjective list used by 6.
- Family 6 (stacked adjectives) and 11 (named outlets) are heuristics: no part-of-speech tagging, and
  outlets are recognised as capitalised words.
- Family 25 (question-answer) needs an auxiliary-led question of up to about 80 characters, then a
  one-word answer sentence.
- Family 56 (boldface) fires on any bold span. Family 70 needs three rules in a document of 24 or more
  non-empty lines. Family 71 fires when at least 20% of six-word runs repeat (minimum 20 runs).
- Family 37 counts openers only within one paragraph (at least two). Family 42 counts repeated
  two-word openers within a paragraph of at least three sentences.
- Family 41 (alternation): six or more sentences in strict up/down alternation, each step differing
  by at least six words.
- Family 55 (contraction absence): at least 2% first-person pronouns, at least three full forms, and
  at least 80% of contractable forms written out.
- Family 58 counts em dashes only in paragraphs with two or more.
- Family 61 accepts years 1500–2099 only.
- Family 63 `[NAME]`-style slots: all-capitals of three or more characters, or a bracketed keyword.
- Homoglyph map: a subset of Cyrillic, Greek, and Armenian lookalikes for the listed letters. Arabic
  presentation forms are **not** included (no table given; not guessed).
- Invisible-character position rules check the immediate neighbour characters only, not the nearest
  non-removed one.
- Unknown extensions passed to `check` or the detector are read as plain text. The guard ignores them.
- `--ci` interval: a deterministic heuristic (half-width from sentence count, 2 to 15 points) around the
  point score, **not** a true resampling. The point score is unchanged.
- The welcome, the reminder, and the contract wording are my text. Shell requirements (banned words,
  `never` before `source code`, target integers, `--clean` at strict only) were checked by script.

Plugin behaviour:
- Level precedence: `PROSECHECK_DEFAULT_MODE` (if valid) overrides the stored flag, as the Interface
  says. So `status` reports the environment value while the variable is set.
- On the first session start (no flag file), the resolved level is written to the flag (`full` unless
  the environment supplied another valid level; `full` is written if the environment says `off`).
- Plugin root defaults to the parent of `hooks/` (the directory containing `hooks/`). **Consequence:**
  with this repository at `/app`, the guard skips every file under `/app`, as the PRD requires for files
  inside the install tree. Files outside the plugin root (for example in another project) are scored.
- Ledger file: `.prosecheck-ledger-<session id>`, with characters outside `[A-Za-z0-9_-]` replaced by
  `_`. Without a session id: `.prosecheck-ledger`. Records hold the base name only.
- `show` rows: scored rows show labels only when the file had fired labels. Failed reasons are the
  five user-readable reasons, plus "cannot read the file" for a missing path.
- Post-tool-use: `tool_name` is matched case-insensitively. `NotebookEdit` reads `notebook_path`, with
  `file_path` as a fallback. `apply_patch` accepts `*** Add File:`, `*** Update File:`, and `*** Move to:`
  lines (the colon is required).
- Stats: assistant rows are de-duplicated by `message.id` (usage taken from the last row for that id;
  text de-duplicated per id). Turns = distinct message ids. Rows without an id count by `uuid` or
  position.
- `check` strips one pair of quotes and one leading `@`, in either order, around the path.
- `init` appends the contract to `AGENTS.md` between HTML-comment markers
  (`<!-- prosecheck:contract:start -->` … `end`). It detects the section by the start marker. It never
  writes the machine path or the user name. The live contract (session start, subagent, prompt) may name
  the detector path, as allowed.
- Doctor's python probe sends a short sentence on standard input to `scripts/detect.py`.
- `doctor` and `check` look for `python3`, then `python`, then `py` on the given `PATH`.

## Not implemented (by design)

- Catalogue numbers 7, 9, 28, 29, 43, 45, 49, 52, 53 have no detector, per the PRD's no-detector list.
- The PRD's "bundled evaluation script", "documentation checker", "recorded demo", and "status-line
  helper" are not product surfaces and were not built.
- Rewriting `.docx`/`.epub`/`.odt`/`.ipynb` in place is not done (cleanup prints text only).

## Verified by hand (not a test suite)

- Detector: prose and flagged samples, scoring floors, character layer, cleanup, UTF-16 and BOM input,
  CRLF, DOCX/PPTX/XLSX/ODT/EPUB/ipynb extraction, corrupt archives, empty input, unknown options,
  `--`, multiple operands, `--ci`, and a 512 KB invisible/space run (about 1.1 s; a regex that was
  quadratic on long text was fixed).
- Hooks: first-run welcome, router replies, `off`/`on`, unknown subcommand, doctor (including with
  Python removed from `PATH`), `check` (scored, directory, PDF, missing), `init` (write, already present,
  off), `show`, guard (flagged, clean, instruction file, binary, missing file, apply_patch, lite no-op),
  subagent envelope, stats (transcript, missing transcript).
- Contract text per level: banned words present, no full-level integer at lite, `--clean` only at strict,
  exported text free of machine paths and user names.

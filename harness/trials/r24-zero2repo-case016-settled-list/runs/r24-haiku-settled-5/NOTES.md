# NOTES: prosecheck build

Scope: the detector (`scripts/detect.py`), the plugin hooks (`hooks/*.js`, `hooks/lib/*.js`),
the `/prosecheck` command document (`commands/prosecheck.md`), the Cursor rule shipped at
`.cursor/rules/prosecheck.mdc`, and the plugin manifest (`.claude-plugin/plugin.json`,
`hooks/hooks.json`). Nothing under `spec/` was changed. No install or build step is needed:
the detector is Python 3.9+ standard library, the hooks are Node.js with only `fs`, `path`,
`os`, and `child_process`.

Where the spec disagrees with itself, `spec/RULINGS.md` gives the owner's ruling, and the
build follows it. Each entry below quotes both sides with their location, then states what was
built.

## A. Conflicts resolved by RULINGS.md

1. **Where the usage message is printed.** PRD FP-01 "Public entry" (line 82–83): "The usage
   message goes to the error stream, so that standard output carries only reports." PRD FP-01
   "Boundary / error behavior" (line 167): "Help ... prints the usage message to standard output
   and succeeds." Built: help writes usage to stdout, exit 0. Usage errors (unknown option) go to
   stderr as a JSON error object with exit 2.
2. **Floor for a single decisive finding.** PRD FP-01 line 93: "A decisive finding always lifts
   the score to at least 45, whatever the confidence." Line 94: "A single decisive family at
   `none` or `low` confidence does not take that 45 floor." Built: any decisive finding gives a
   floor of 45 regardless of confidence (ruling).
3. **Hedge stacking.** PRD line 90: hedge stacking (54) is weight zero and "a document scores the
   same ... whenever the score-moving findings are the same." PRD line 128: "Each sentence with
   stacked hedges adds to the score." Built: 54 is writing advice and never changes the score.
4. **Tailing-negation form of catalogue 17.** PRD line 91: "The tailing-negation form is
   score-moving." IC `scripts/detect.py` > Findings line 148: "Both forms of catalogue 17 are
   writing advice and carry weight zero." Built: both forms are advice. Consequence: the score-moving
   set is 49 numbers, not the PRD's 50, and advice is 13 numbers, not 12 (17 joins the list).
5. **No-break spaces.** PRD Terminology line 30: "Every no-break space becomes an ordinary space."
   PRD FP-03 line 212 keeps a no-break space that "holds something together". Built: an NBSP or
   narrow NBSP is kept under the line-212 positions (digit on either side; before `: ; ! ? » › % €`;
   after `« ‹`); every other one becomes U+0020.
6. **Markdown hard break.** PRD FP-03 line 214: "Two trailing spaces that end a line of prose are
   a markdown hard break and are kept." PRD FP-03 line 223: trailing whitespace "is removed even when
   two spaces were meant as a markdown hard break." Built: exactly two trailing spaces on a non-blank
   line are kept by `--clean`; any other trailing spaces or tabs are removed. Detection still counts
   trailing whitespace as finding 68 (advice).
7. **`utm_source` values.** PRD line 131: "Any `utm_source` parameter ... is an AI tracking parameter
   (65)." PRD line 132: it fires "only when that whole host name is one of those domains." Built:
   65 fires only when the value (up to a sentence-ending period) is exactly one of the seven hosts.
8. **Stop phrases.** PRD FP-04 line 240: "A prompt that contains `stop prosecheck` anywhere switches
   the tool off." PRD FP-06 line 285: the stop phrases store `off` "as the entire prompt". Built:
   `stop prosecheck` anywhere in a prompt stores `off`; a prompt that is entirely `stop prosecheck` or
   `prosecheck off` (any letter case) gets a block reply naming `off`. `prosecheck off` only counts as
   a stop phrase as the entire prompt.
9. **`PROSECHECK_DEFAULT_MODE` precedence.** PRD FP-04 line 246: the environment applies only "when
   nothing valid is stored". IC "Naming conventions" line 63: the variable "takes precedence over the
   stored level." Built: a valid stored level wins; the environment applies only when nothing valid is
   stored; otherwise `full`. On the first start with no flag, the effective level is written to the
   flag file.
10. **`.pdf` as a prose file.** PRD Terminology line 27 and FP-02 line 195: `.pdf` is not prose. PRD
    FP-06 line 290 and IC `show` line 582: "rows appear after prose files, including `.docx` and
    `.pdf` deliverables, are saved." Built: `.pdf` and `.rtf` are binary. The guard records them as
    `not re-scored (binary file)` and gives no nudge. The empty-ledger wording is kept as written.
11. **How many file operands.** IC `scripts/detect.py` line 21: "at most one file operand." IC line 180
    and PRD line 168: two or more operands succeed. Built: two or more operands succeed (exit 0).
12. **Which operand is scanned.** IC line 106: "the last one is the file scanned." IC line 180 and
    PRD line 168: "the first is scanned." Built: the last operand is scanned (ruling). The notice on
    stderr says that only the last operand is scanned and lists the others, including the first, as
    ignored. This keeps the first operand's name in the notice (IC line 180 requires it) while naming
    the scanned file (PRD line 168 requires that).
13. **`apply_patch` payload path limit.** PRD FP-05 line 264: "at most **16** distinct paths." IC
    Post-tool-use reply line 260: "At most ten paths." Built: 16.
14. **Ledger record count.** PRD FP-05 line 265: "At most the newest **20** records are kept." IC
    "Plugin config and ledger" line 91: "newest **50** records." Built: 50.
15. **Ledger retention.** PRD Non-functional "Privacy" line 57 and FP-06 line 290: kept while the last
    modification is seven days old or younger. IC "Config filenames" line 65: "untouched for more than
    one day is deleted." Built: seven days. Ledgers older than seven days are deleted at session start
    and are never listed by `show`.
16. **Which transcript `stats` reads.** PRD FP-06 line 292: "a named transcript wins over a newer one."
    IC `stats` > Signature line 646 and `transcript_path` line 681: the named transcript is read. IC
    `stats` > Transcript rows line 650: "When the projects folder holds a transcript newer than the
    named one, the newer transcript is read." Built: the newer of the named transcript and the newest
    `projects` transcript is read (ruling). A named path that cannot be read gets the missing-transcript
    reply rather than a fallback.
17. **Minimum slice length for the session-prose score.** PRD FP-06 line 292: printed when the trimmed
    slice is "longer than **200** characters." IC `stats` > Reply line 662: "longer than **500**
    characters." Built: 200 (ruling).

## B. Other disagreements or gaps found while building

18. **Archive cap in kilobytes.** PRD FP-02 line 181: the zip/notebook cap is 4 MB, "which is 4096 KB".
    IC `check` line 533 and PRD `show` line 271 ask for the cap "in kilobytes". Built: `over 512 KB`
    for plain text and `over 4096 KB` for archives and notebooks, matching the PRD's own 4096 KB figure.
    The `doctor` closer says `4 MB`.
19. **Cleanup and the window.** PRD FP-02 line 199: "Character-layer rules use the same window: an
    invisible character placed only after character 262,144 is not a finding." PRD FP-03 says cleanup
    prints scrubbed text with no window limit. Built: findings use the window; `--clean` scrubs the whole
    input, since it is not a finding and nothing in the spec truncates the output.
20. **Non-standard spaces versus line separators.** PRD FP-03 line 212 says line and paragraph
    separators "become line feeds," and the cleanup-agrees rule (line 215) says a character cleanup
    normalizes is counted. Built: U+2028 and U+2029 are counted under `nonstandard_spaces` and become
    line feeds under `--clean`.
21. **Interval versus "enough sentences".** PRD line 160 and IC line 160 require an interval only with at
    least four sentences, and "the resampling count and seed are the implementer's choice." Built: no
    resampling. The interval is `score ± round(20/√n)` (at least ±2) clamped to 0–100, where n is the
    sentence count. The note in `score_ci_note` says it is not resampled.

## C. Things the spec does not state (assumptions)

- **Score formula.** The PRD fixes the caps, floors, bands, and confidence, but not the base arithmetic.
  Built: each score-moving family contributes `w × (1 − 0.5^hits)`, with `w = 15` (ordinary), `25`
  (decisive), and `8` (rhythm 40 and 44); the sum is capped at 100. Then the caps apply (single family
  or rhythm-only → 40; only 40 → 20; no caps when a decisive finding is present), then the floors apply
  (decisive → 45; two decisive → 65; short-document and long-document floors as the PRD states). Final
  score is rounded to an integer.
- **Pattern lists.** Several catalogue families name examples and leave the rest to the implementer:
  4 (hyphenated pairs), 69 (canonical marketing phrases), 19, 22, and the stock hyphenated compounds.
  The implementer's lists are in `scripts/detect.py`. Rule-based families were written from the PRD's
  stated conditions (for example 1 uses the PRD's word list with simple inflections; 6 needs four or more
  comma-joined words with at least one stock or suffix-adjective word; 40/41/44 use the coefficient of
  variation from the PRD).
- **Homoglyphs.** The lookalike table covers Cyrillic, Greek, and Armenian letters that look like the
  listed Latin letters. Arabic-presentation lookalikes are not in the table. A run qualifies only if it
  has ASCII Latin letters and lookalikes and no other non-ASCII letter. `homoglyphs` counts lookalike
  characters in qualifying runs; finding 66 counts the runs.
- **Invisible characters.** Category `Cf`, control characters (except tab, LF, CR), variation selectors,
  tags, Mongolian selectors, and the explicit default-ignorable code points. The kept-position rules
  follow PRD FP-03 with simplified neighbour tests (for example, "a symbol" means a symbol category or
  emoji range).
- **Masking.** Before analysis, non-prose regions are replaced by private-use placeholders of the same
  length (offsets preserved): YAML front matter, fenced code (CommonMark closing rule), inline code,
  runs of two or more blockquote lines, table rows (lines starting with `|`), and badge lines. Headings
  stay in the text but are excluded from sentence and paragraph statistics.
- **Words.** A word is a run of letters, digits, apostrophes (straight or curly), and hyphens that contains
  at least one letter or digit.
- **Sentence and paragraph splitting.** Sentences end at `.`, `!`, `?` or a line break; paragraphs are
  separated by blank lines.
- **Cleanup trimming.** Line endings become LF. Leading blank lines are removed. When the input ended with
  a line feed, exactly one is restored.
- **Excerpts.** Finding samples for catalogue 1 are exact substrings of the scanned text (line breaks shown
  as spaces, `...` marks a cut). Other samples are free text.
- **Archives.** Zip members over 64 MB uncompressed are not read. EPUB chapters are read in archive-name
  order (the spine is not parsed). Navigation documents are skipped by name. Notebooks join markdown
  cells with line feeds.
- **Text decoding.** UTF-8 with an optional BOM; UTF-16 with a BOM; invalid UTF-8 bytes are replaced.
- **Detector interpreter.** The hooks try `python3`, then `python`, then `py`, and use the first one that can
  be launched.
- **Option `-`.** A lone `-` is an unknown option, following IC line 106 literally.
- **Stats.** Turns are unique assistant message ids (entries with no id count individually). Token totals
  use each message's last `usage` values. Prose slice: assistant text joined with blank lines, fenced code
  removed, last 40,000 characters.
- **Guard.** Relative paths resolve against the payload `cwd`, then against the process working directory.
  A missing file with a prose extension is recorded as a failed check. Paths under `node_modules`, `.git`,
  or the plugin root are skipped. Instruction files are skipped before any recording.
- **Failed-check reasons** (ledger, `check`, and `show`): "Python cannot be found", "the detector timed
  out", "the detector printed text that is not a report", "the report has no numeric score", "the detector
  produced no output", "the detector exited without a usable result". Reasons in `show` contain no digits.
- **Session identity.** A missing `session_id` uses the ledger `default`. Ledger files are
  `.prosecheck-ledger-<session>` (no extension).
- **First start.** When no flag file exists and the level is not `off`, the welcome is printed and the
  effective level is written to `.prosecheck-active`.
- **Doctor Python check.** Runs the bundled detector on a short sample through stdin. A missing detector
  reports that it could not be run.
- **Init.** Writes `AGENTS.md` and `.cursor/rules/prosecheck.mdc` into `process.cwd()`. The Cursor rule is
  copied from `<plugin root>/.cursor/rules/prosecheck.mdc` (shipped in this repo). If the shipped copy cannot
  be read, the same text is generated. The AGENTS.md section is recognised by its start marker or heading.
- **Live contract path.** The live session contract names the detector path on this machine (the spec allows
  it). The exported contract never names a machine path or user name.
- **Plugin root.** `CLAUDE_PLUGIN_ROOT` if set, otherwise the directory above `hooks/`. `skills/prosecheck/scripts/detect.py`
  is a fallback location. No skill file is shipped, because the PRD says the bundled skill is not a product
  surface.
- **Not built.** The recorded-session demo, documentation checker, evaluation script, and status-line helper
  are not product surfaces under the PRD, so they are not included.

## D. Verification

- `scripts/detect.py`: help, empty input, unknown option, missing file, plain text, AI-style text, two
  operands, `--clean`, `--ci`, the 262,144-character window, a 500 KB invisible-character stress input
  (about 0.5 s), `.docx`, `.odt`, `.epub`, `.ipynb`, malformed zip, malformed notebook, and `.pdf`.
- Hooks, run with a temporary `CLAUDE_CONFIG_DIR`: session start (welcome once, flag written, environment
  default, stored level beats environment, invalid stored level), subagent envelope, prompt routing (every
  subcommand, namespaced form, unknown word, stop phrases, `off` silence), `doctor` in each state,
  `check`, `show` for each row kind, `stats` (transcript and missing), `init` (twice, existing `AGENTS.md`
  preserved), the post-tool guard (flagged, unflagged, skipped paths, binary, oversize, `apply_patch` with
  a missing path), malformed input (exit 0).
- Text constraints from the interface contract (banned words, `source code` sentence rule, levels,
  export contents, Cursor rule globs and body, welcome facts) were checked by script.

Not verified: a live Claude Code or other host session, Windows and macOS behaviour, and Python 3.9
compatibility (the code was run only on Python 3.13).

# NOTES: prosecheck build

Built from `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (IC), and
`spec/Hardware_Requirements.md` (HW). `spec/` is unchanged. `spec/CONFLICTS.md`
was used as a checklist; I checked each entry against the two documents and
added the disagreements it did not list (marked **extra**).

Layout I built:

| Path | What it is |
| --- | --- |
| `scripts/detect.py` | The detector (Python 3.9+, standard library only) |
| `lib/prosecheck-core.js` | Shared Node module: level flag, contract text, router, ledger, detector runner |
| `hooks/prosecheck-activate.js` | session-start |
| `hooks/prosecheck-tracker.js` | prompt-submit and `/prosecheck` router |
| `hooks/prosecheck-subagent.js` | subagent-start |
| `hooks/prosecheck-guard.js` | post-tool-use (saved-file guard) |
| `hooks/prosecheck-stats.js` | stats (also handled inside the router) |
| `hooks/hooks.json` | hook wiring (not in spec; for the plugin host) |
| `.claude-plugin/plugin.json` | plugin metadata (not in spec) |
| `commands/prosecheck.md`, `install/prosecheck-command.md` | `/prosecheck` menu document (both locations the spec allows) |
| `.cursor/rules/prosecheck.mdc` | shipped Cursor rule that `init` copies |

Nothing was committed. The repository is not a git repo.

---

## 1. Conflicts between spec documents

For each one: what each side says (with location), then what I built.

### 1.1 Where the usage message goes (CONFLICTS 1)
- PRD FP-01 "Public entry" (line 82–83): "The usage message goes to the error stream, so that standard output carries only reports."
- PRD FP-01 "Boundary" (line 167) and IC `scripts/detect.py` > Usage (line 110): help "prints the usage message to standard output and exits 0".
- **Built:** `--help`/`-h` print usage to stdout, exit 0. The error stream carries only errors and the multi-file notice.

### 1.2 Floor for a single decisive finding (CONFLICTS 2)
- PRD FP-01 "Normal behavior" (line 93): "A decisive finding always lifts the score to at least 45, whatever the confidence."
- PRD FP-01 "Normal behavior" (line 94): "A single decisive family at `none` or `low` confidence does not take that 45 floor."
- **Built:** the more specific rule (line 94) wins. One decisive family gives a floor of 45 only at `moderate` or `high` confidence. Two or more decisive families give a floor of 65.

### 1.3 Whether hedge stacking moves the score (CONFLICTS 3)
- PRD FP-01 (line 90): 54 (hedge stacking) is one of the 12 writing-advice numbers, "weight zero".
- PRD FP-01 "Family rules" (line 128): "Each sentence with stacked hedges adds to the score."
- **Built:** 54 is advice (weight zero). The advice list (line 90) is the explicit enumeration of weight-zero numbers, so it wins over the family-rule sentence.

### 1.4 Tailing-negation form of catalogue 17 (CONFLICTS 4)
- PRD FP-01 (line 91): "The **tailing-negation form** is score-moving."
- IC `scripts/detect.py` > Findings (line 148): "Both forms of catalogue 17 are writing advice and carry weight zero."
- **Built:** the parallelism form (`17_negative_parallelism`) is advice. The tailing-negation form (`17_tailing_negation`) is score-moving. This follows the PRD, whose advice list (line 90) does not include 17.

### 1.5 No-break spaces (CONFLICTS 5)
- PRD Terminology (line 30): "Every no-break space becomes an ordinary space."
- PRD FP-03 "What is normalized" (line 212): a no-break space is kept when a digit is on either side, or before `: ; ! ? » › % €`, or after `« ‹`.
- **Built:** the FP-03 keep rule wins (it is the operational rule, and it is what "cleanup agrees with detection" needs). Kept no-break spaces are not counted.

### 1.6 Markdown hard-break trailing spaces (CONFLICTS 6)
- PRD FP-03 "What is trimmed" (line 214): two trailing spaces are "kept".
- PRD FP-03 "Boundary" (line 223): "That collapse is required, not optional."
- **Built:** removed (line 223 is the explicit requirement). Trailing whitespace is also reported as advice 68.

### 1.7 Zero-width characters inside the text (CONFLICTS 7)
- PRD FP-01 (line 159): "A zero-width character inside the text is an invisible character."
- PRD FP-03 (lines 211, 215): a ZWJ/ZWNJ/ZWSP/variation selector in listed positions is kept and "not counted as an invisible character".
- **Built:** a zero-width character counts unless FP-03 keeps it in one of its listed positions. Line 159 is read as the general rule with the FP-03 exceptions.

### 1.8 `utm_source` (CONFLICTS 8)
- PRD FP-01 chat markup (line 131): "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
- PRD FP-01 tracking (line 132): fires "only when that whole host name is one of those domains."
- **Built:** only the seven listed domains fire (line 132). Line 131's "any" is read as the general case of the listed set.

### 1.9 Whether `stop prosecheck` must be the whole prompt (CONFLICTS 9)
- PRD FP-04 (line 240): "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- PRD FP-06 (line 285) and IC `/prosecheck` > Stop phrases (line 411): the whole prompt only.
- **Built:** whole-prompt only, case-insensitive. Two of three statements agree, and FP-06 is the operator-facing rule.

### 1.10 Precedence of `PROSECHECK_DEFAULT_MODE` (CONFLICTS 10)
- PRD FP-04 (line 246): the environment applies "when nothing valid is stored".
- IC Naming conventions > Host environment (line 63): the variable "takes precedence over the stored level".
- **Built:** the PRD rule. The variable is a default. A stored valid level always wins, so `/prosecheck lite` keeps working when the variable is set.

### 1.11 `.pdf` as a prose file (CONFLICTS 11)
- PRD Terminology (line 27) and FP-02 (line 195): `.pdf` is not one of the twenty formats.
- PRD FP-06 (line 290) and IC `show` > Empty ledger (line 582): ".docx and .pdf deliverables" appear as rows.
- **Built:** `.pdf` and `.rtf` are not scored, and the guard records them as **binary** rows. `show` lists them as "not re-scored". The empty-ledger text still names `.docx` and `.pdf`, as the IC requires.

### 1.12 Number of file operands (CONFLICTS 12)
- IC `scripts/detect.py` (line 21): "at most one file operand".
- IC "Several file operands" (line 180) and PRD FP-01 (line 168): two or more operands still succeed.
- **Built:** any number of operands. A notice goes to stderr.

### 1.13 Which operand is scanned (CONFLICTS 13)
- IC `scripts/detect.py` Signature (line 106): "the last one is the file scanned".
- IC "Several file operands" (line 180) and PRD FP-01 (line 168): the first.
- **Built:** the first operand. Two of three statements say so.

### 1.14 Maximum paths in one `apply_patch` payload (CONFLICTS 14)
- PRD FP-05 (line 264): "at most **16** distinct paths".
- IC Post-tool-use reply (line 260): "At most ten paths of one payload are scored."
- **Built:** 16 (PRD). The PRD is the behaviour document, and FP-05 owns the guard's semantics.

### 1.15 Records a ledger keeps (CONFLICTS 15)
- PRD FP-05 (line 265): "At most the newest **20** records are kept."
- IC "Plugin config and ledger" (line 91): "keeps its newest **50** records".
- **Built:** 20. The IC itself defers "what a ledger records and how long it is kept" to the PRD (line 91).

### 1.16 How long a ledger is kept (CONFLICTS 16)
- PRD Non-functional, Privacy (line 57): kept while last modified seven days or less ago.
- IC Config filenames (line 65): "untouched for more than **one day** is deleted".
- **Built:** seven days (PRD). The IC defers retention to the PRD (line 91). Ledgers older than seven days are deleted at session start and are not listed by `show`.

### 1.17 Which transcript `stats` reads (CONFLICTS 17)
- PRD FP-06 (line 292): "a named transcript wins over a newer one".
- IC `stats` Transcript rows (line 650): "the newer transcript is read".
- **Built:** the named `transcript_path` wins, as the PRD says. Only when no path is named does `stats` use the newest `.jsonl` under `projects`.

### 1.18 Minimum slice for the session-prose score (CONFLICTS 18)
- PRD FP-06 (line 292): printed only when the slice is "longer than **200** characters".
- IC `stats` Reply (line 662): "longer than **500** characters".
- **Built:** 200 (PRD). The IC does not defer this number, so this is a judgement call. Change one constant in `statsReply` (`lib/prosecheck-core.js`) if the other value is wanted.

### 1.19 Whether one use of a model-dialect word fires (CONFLICTS 19)
- PRD FP-04 (line 236): the model-dialect family "needs two hits" for its dialect words, yet "every word ... fires".
- PRD FP-01 family rules (line 101): no two-hit condition.
- **Built:** one hit fires family 2. The FP-01 family rule is the authoritative definition of the family, and the "every word fires" statement is the one the guard needs. This is a judgement call. A two-hit threshold would change only `rx_fn` for family 2 in `scripts/detect.py`.

### 1.20 Welcome versus "silent" contract (CONFLICTS 20)
- PRD FP-04 (line 235): the contract never names prosecheck.
- PRD FP-04 (line 238): the welcome says "prosecheck is installed and on".
- **Built:** the welcome is shown once, to the user, at first start, as line 238 requires. The contract body stays silent.

### 1.21 Extra conflicts I found (not in CONFLICTS.md)

- **Extra A. `init` contract versus welcome, and the marker.** IC `init` says the section is recognised "by that single copy of the contract, not by a required marker spelling". **Built:** the section starts with `<!-- prosecheck:contract:start -->` and is recognised by that marker, by the heading `## Prose writing contract`, or by the phrase `prose deliverables only`. Any of the three counts as already present.
- **Extra B. Notice line on stderr.** IC `scripts/detect.py` says "A run with a single operand prints no such line." **Built:** exactly that.
- **Extra C. Cleanup on the window.** PRD FP-03 gives no window rule for cleanup, but PRD FP-02 says character rules use the window. **Built:** cleanup works on the whole extracted text (cleanup prints everything, it does not truncate). Findings and metrics use the window only.
- **Extra D. Character findings inside code.** PRD FP-01 says code generates no findings, but FP-03 counts characters in the whole text. **Built:** pattern families ignore masked code. Character-layer counts (62, 66, 67, 68) and their metrics are computed on the whole window, including code, so cleanup and rescan agree.
- **Extra E. Stop phrases and the router.** Already covered by 1.9.

---

## 2. Things the spec does not state, and what I assumed

### 2.1 Scoring model (PRD FP-01 gives the rules, not the arithmetic)
- Family weight is 10 for ordinary score-moving families, 14 for decisive families, and 6 for rhythm kinds (40, 44). A family contributes `weight * (1 - 0.5**hits)`. The total is rounded and capped at 100.
- The caps and floors come from the PRD: one family caps at 40; rhythm-only caps at 20 (only 40 fired) or 40 (40 and 44 fired); the decisive, short-document, and long-document floors are applied after the caps.
- Calibration is my own. Two sample files give a sense of it: an AI-style 99-word draft scores 59 (mixed), and a 207-word ordinary essay scores 0 (clean). Expect the numbers to be adjusted if the hidden tests use other calibration.

### 2.2 Sentences, paragraphs, words
- Words: runs of letters and digits joined by apostrophes or hyphens. A sentence ends at `.`, `!`, `?`, or a line break. Headings are not sentences. A paragraph is a run of lines with no blank line between them.

### 2.3 Pattern lists the spec leaves open
- Catalogue 4 (hyphenated pairs), 6 (stock evaluative adjectives plus -ive/-ous/-able/… suffixes), 8 (synonym clusters, as listed in PRD FP-01), 22, 69 (canonical phrases), and 19 are lists I chose. PRD says the list is "the implementer's choice" for 4 and 69.
- Catalogue 66 (homoglyphs) covers Cyrillic, Greek, and Armenian lookalikes. I did not add Arabic-presentation lookalikes; this is the one gap I know of.
- Catalogue 25: a question must start with an auxiliary or modal, and the answer is a one-word reply followed by `.` or `!`.
- Catalogue 37 (transitions): counted within a paragraph; the count is the number of transitions in paragraphs with two or more.
- Catalogue 40/44 use the coefficient of variation rules as written. Catalogue 41 (alternation) counts runs of six or more sentences with substantial alternating differences (5+ words).
- Catalogue 46 is advice; fires only on documents of 300+ words with no semicolon and at most two parentheses.
- Catalogue 55 (contraction absence) fires on first-person-heavy text (3%+ first-person pronouns) where at least three full forms appear and under 20% are contracted.
- Catalogue 61 uses four-digit years only (1000–2999), with the earlier year first.
- Catalogue 63: placeholder text includes the fill-in words you listed, all-caps brackets of three or more letters, `{{...}}`, `xxx`, and `lorem ipsum`. A bracket followed by `(` or `[` is a link.
- Catalogue 70: horizontal rules count only when the document has at least 24 lines.
- Catalogue 71: fires when at least 20% of six-word runs recur.

### 2.4 Samples, labels, keys
- A sample is an excerpt of the scanned text, about 80 characters around the match, with line breaks replaced by spaces and `...` marking cuts.
- Labels are human-readable phrases. Keys are `<N>_<slug>`. Catalogue 17 uses the two exact keys the IC requires.

### 2.5 `--ci` interval
- The sentences are split into four contiguous blocks. Each block is scored, and the interval is the min to max of those scores together with the point score (so it always contains the point score). Deterministic. Fewer than four sentences gives `score_ci: null` and a note.

### 2.6 Argument parsing
- A lone `-` is treated as an unknown option, exactly as the IC literally says ("any other argument that begins with `-`"). Standard input is read only when no operand is given.

### 2.7 Encoding and decoding
- Plain-text input: a UTF-8 byte-order mark is stripped. UTF-16 with a byte-order mark is decoded. Other invalid UTF-8 is replaced. CRLF and lone CR become LF before analysis.
- The `.docx` and similar extraction joins paragraphs with blank lines and trims the result, following FP-02.
- Notebooks: each markdown cell is one paragraph. Cell sources may be strings or lists of strings. A malformed cell makes the whole notebook empty.

### 2.8 Plugin host behaviour
- `PostToolUse` payloads: `tool_name`, `tool_input.file_path` (or `notebook_path` for NotebookEdit, or `command` for apply_patch), `session_id`, `cwd`. Other tool names are ignored.
- The plugin install tree is the plugin root. With `CLAUDE_PLUGIN_ROOT` unset, that is the directory containing `hooks/` (`/app`). This means prose files inside `/app` are skipped by the guard, as the spec requires. If you test the guard with files under `/app`, set `CLAUDE_PLUGIN_ROOT` to another directory.
- Session start writes the flag file (`.prosecheck-active`) with the resolved level when none exists, so the welcome appears only once.
- Python is looked up as `python3`, then `python`, then `py` (spec allows any order).
- Ledger file names: `.prosecheck-ledger-<sanitized session id>`. Without a session id: `.prosecheck-ledger`.
- The guard labels: up to five score-moving labels, in catalogue order. `check` lists all fired labels, sorted by count, capped at eight.

### 2.9 `doctor`
- The Python check runs the detector on a fixed sample sentence through stdin. The settings check writes and deletes a probe file in the config folder.

### 2.10 Cursor rule and `init`
- The Cursor rule's globs are one comma-separated line in its front matter (the IC only requires the eight prose globs in that block).
- `init` exports a portable contract. The export contains `CLAUDE_PLUGIN_ROOT`, `skills`, and `plugins` only on one line at `full` and `strict`. It contains no absolute path and no user name.

### 2.11 Stats
- Assistant messages are de-duplicated by `message.id`. Token totals are summed once per message. Numbers are grouped with commas.
- Code fences are removed before scoring the session prose, and the last 40,000 characters are scored.

---

## 3. Not verified or not done

- Windows and macOS were not tested. The sandbox has Linux, Python 3.13, and Node 22.
- The hidden tests are not known to me; I did not look for them. The checks I ran are my own (listed below).
- The skill-folder fallback (`skills/prosecheck/scripts/detect.py`) is looked up but no copy is shipped.
- No README was written; the spec does not require one.

### Checks I ran (not part of the repo)
- Detector: help, unknown option (exit 2), empty input (exit 1), missing file, bad zip, `.pdf`, two operands, `--clean`, `--ci`, UTF-16 BOM, CRLF, extraction for docx, pptx, xlsx, odt, epub, and ipynb (the other zip formats — docm, pptm, xlsm, odp, ods — share those code paths but were not separately run), invisible/zero-width handling, non-standard spaces, homoglyph folding, scan window (262,144 characters, `truncated`), and timing on adversarial inputs (all under 1 second).
- Catalogue registry: 62 machine-checked numbers, unique labels, 12 advice numbers plus the 17 parallelism form.
- Hooks, end to end with a scratch `CLAUDE_CONFIG_DIR`: welcome once, flag persistence, doctor (four `[OK]` lines; off-only; missing Python), router (help, unknown word, lite/full/strict/off/on/status, stop phrases, namespaced form), guard (flagged Write, clean Edit, `.docx`, `.pdf` binary, missing file, instruction-file skip, `node_modules` skip, apply_patch with several files, over-cap skip), show (ordering, empty ledger, skip, binary, failed rows), check (quoted and `@` paths, directory, `.pdf`, over cap, missing), init (fresh, repeat, lite, off), stats (duplicate message ids, named transcript, missing transcript).
- Contract constraints from the IC (banned words, `source code` wording, per-level integers and band words, `--clean` placement, export portability, Cursor rule globs and contents).

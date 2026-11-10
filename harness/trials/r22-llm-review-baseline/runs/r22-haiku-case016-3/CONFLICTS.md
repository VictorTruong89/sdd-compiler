# Specification conflicts

Scope: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (IC), `spec/Hardware_Requirements.md` (HW). Line numbers refer to the files as read. Only statements that cannot both hold for the same case are listed.

---

### 1. Ledger retention period

- **PRD**, Non-functional constraints, Privacy (line 57): "A ledger whose last modification is more than seven days old is gone by the time a later session is in use; a ledger seven days old or younger is kept." (Repeated in FP-06 `show`, line 290.)
- **IC**, Config filenames (line 65): "A ledger untouched for more than one day is deleted at the next session start."

A ledger last touched two days ago is kept under the first statement and deleted under the second.

### 2. Ledger record cap

- **PRD**, FP-05 Normal behavior (line 265): "At most the newest 20 records are kept."
- **IC**, Plugin config and ledger (line 91): "Each ledger keeps its newest 50 records."

A ledger holding 35 records keeps 20 under the PRD and 35 under the IC.

### 3. Which prompts switch the tool off

- **PRD**, FP-04 Normal behavior (line 240): "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- **PRD**, FP-06 Normal behavior (line 285): "The phrases “stop prosecheck” and “prosecheck off” as the entire prompt (letter case ignored) also store `off`; the same words with anything else before or after them are an ordinary prompt."
- **IC**, Stop phrases (line 411) follows the FP-06 rule (entire prompt only).

A prompt such as "please stop prosecheck for this file" must both switch the tool off (FP-04) and be an ordinary prompt (FP-06).

### 4. The 45 floor for a single decisive family

- **PRD**, FP-01 Normal behavior, family rules (line 93): "A decisive finding always lifts the score to at least 45, whatever the confidence."
- **PRD**, FP-01 Normal behavior (line 94): "A single decisive family raises it to **at least 45** only when confidence is above `low`. A single decisive family at `none` or `low` confidence does not take that 45 floor."

Line 93 requires a floor of 45 at every confidence level; line 94 denies it at `none` and `low`.

### 5. Whether hedge stacking moves the score

- **PRD**, FP-01 Normal behavior (line 90): the twelve writing-advice numbers, including "54 (hedge stacking)", "reported, weight zero", and "a document scores the same as the same document without that phrasing".
- **PRD**, FP-01 family rules, hedge stacking (line 128): "Each sentence with stacked hedges adds to the score."

Line 90 says a stacked-hedge sentence changes nothing; line 128 says it adds to the score.

### 6. Weight of catalogue 17's tailing-negation form

- **PRD**, FP-01 Normal behavior (line 91): "The **tailing-negation form** is score-moving".
- **IC**, Catalogue (line 148): "Both forms of catalogue 17 are writing advice and carry weight zero."

The same finding `17_tailing_negation` must move the score (PRD) and must not (IC).

### 7. Hit requirement for model-dialect vocabulary

- **PRD**, FP-01 family rules, model-dialect vocabulary (line 101): the family fires on the listed words and phrases, with no hit count.
- **PRD**, FP-04 Normal behavior (line 236): "model-dialect vocabulary, which needs two hits, for its dialect words".

Under line 101 a single "genuinely" fires family 2; under line 236 it needs a second hit before it fires.

### 8. Transition-cluster threshold

- **PRD**, FP-01 family rules, formulaic challenges (line 116): "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
- **PRD**, FP-01 family rules, transition clusters (line 117): "two or more sentence-opening transitions … in one paragraph."

One sentence with one transition opener fires family 37 under line 116 and does not under line 117.

### 9. Whether every no-break space is normalized

- **PRD**, FP-03 Terminology (line 30): "Every no-break space becomes an ordinary space."
- **PRD**, FP-03 Normal behavior (line 212): normalization is "except a no-break space (U+00A0) or narrow no-break space (U+202F) that holds something together: one with a digit on either side, one before `:` `;` `!` `?` `»` `›` `%` `€`, or one after `«` `‹`."

A no-break space between two digits is turned into an ordinary space by line 30 and kept by line 212.

### 10. Trailing spaces that form a markdown hard break

- **PRD**, FP-03 Normal behavior, "What is trimmed" (line 214): "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
- **PRD**, FP-03 Boundary / error behavior (line 223): "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required, not optional."

Two trailing spaces at a line end are kept by line 214 and removed by line 223.

### 11. Stream for the usage message and help output

- **PRD**, FP-01 Public entry (line 82): "The usage message goes to the error stream, so that standard output carries only reports."
- **PRD**, FP-01 Boundary / error behavior (line 167): "Help (the help switch or the short help alias) prints the usage message to standard output and succeeds."
- **IC**, Usage (line 110): "`--help` and `-h` write the usage message to standard output and exit 0."

Line 82 puts the usage message on standard error; lines 167 and IC 110 put `--help` output on standard output.

### 12. Whether more than one file operand is allowed

- **IC**, Shape of the public surface, detector command (line 21): "Invocation is the host Python interpreter followed by `scripts/detect.py`, then optional switches and at most one file operand."
- **PRD**, FP-01 Boundary / error behavior (line 168) and **IC**, Several file operands (line 180): two or more operands succeed, with a notice on the error stream.

A run with two file operands is both outside the invocation form ("at most one") and a documented success case.

### 13. Which operand is scanned when several are given

- **PRD**, FP-01 Boundary / error behavior (line 168): "the first file is scanned".
- **IC**, Global observables (line 82) and Several file operands (line 180): "the first file is scanned" / "the first is scanned".
- **IC**, `scripts/detect.py` Signature (line 106): "When several operands are given, the last one is the file scanned."

With `a.md b.md`, line 106 scans `b.md` and lines 82, 168, and 180 scan `a.md`.

### 14. Interval member when the document has too few sentences

- **PRD**, FP-01 Normal behavior (line 160): "With fewer than four sentences, the interval is **omitted** and the metrics state that there are too few sentences."
- **IC**, `scripts/detect.py` Report, Metrics (line 160): "`score_ci`: present only when `--ci` was given … `null` when it has too few."

Under the PRD the `score_ci` interval is absent; under the IC the member is present with the value `null`.

### 15. Character-layer findings inside code

- **PRD**, FP-01 Normal behavior (line 98): "Inside the scan window, these generate no findings: fenced code blocks as CommonMark defines them …, inline code spans, …"
- **PRD**, FP-01 family rules, invisible characters (line 129): "every invisible character that character cleanup (FP-03) removes, counted on the scan window"; line 159: "A zero-width character inside the text is an invisible character."

A zero-width space inside a fenced code block is "no finding" under line 98 and a counted invisible character under lines 129 and 159. (The same question applies to non-standard spaces, family 67, and trailing whitespace, family 68.)

### 16. Maximum number of paths scored from one apply_patch payload

- **PRD**, FP-05 Normal behavior (line 264): "An apply_patch payload that names several files is scored one file at a time, at most **16** distinct paths."
- **IC**, Post-tool-use reply (line 260): "At most **ten** paths of one payload are scored."

A patch naming 12 files is scored for 16 paths by the PRD and for 10 by the IC.

### 17. Precedence of the `PROSECHECK_DEFAULT_MODE` environment variable

- **PRD**, FP-04 Boundary / error behavior (line 246): "When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words, in which case that word is used." (Same rule at FP-04 line 237.)
- **IC**, Host environment (line 63): "`PROSECHECK_DEFAULT_MODE` — … when it is set, it takes precedence over the stored level."

With a valid stored level of `strict` and the variable set to `lite`, the PRD uses `strict` and the IC uses `lite`.

### 18. Minimum session-prose length for the stats score

- **PRD**, FP-06 Normal behavior, `stats` (line 292): "the session-prose score is printed only when that slice, with surrounding whitespace trimmed, is longer than **200** characters."
- **IC**, `stats` Reply (line 662): "When the scored slice is longer than **500** characters, the reply contains `session prose ai_tell_score: <score>`."

A slice of 300 characters gets a score line under the PRD and none under the IC.

### 19. Which transcript `stats` reads when a named one is older than a newer one

- **PRD**, FP-06 Normal behavior, `stats` (line 292): "a named transcript wins over a newer one."
- **IC**, `stats` Transcript rows (line 650): "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."

With `transcript_path` naming an older file and a newer `.jsonl` present in `projects`, the PRD reads the named file and the IC reads the newer one.

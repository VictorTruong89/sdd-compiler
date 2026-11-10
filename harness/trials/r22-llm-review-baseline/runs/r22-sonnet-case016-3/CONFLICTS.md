# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

## Between documents

1. **Ledger retention.**
   - PRD, Non-functional constraints → Privacy, and FP-06 `show`: a ledger more than seven days old is gone, and one seven days old or younger is kept.
   - IC, Naming conventions → Config filenames: "A ledger untouched for more than one day is deleted at the next session start."
   - A ledger that is three days old would be kept under one and deleted under the other.

2. **Ledger size.**
   - PRD, FP-05: "At most the newest 20 records are kept."
   - IC, Global observables → Plugin config and ledger: "Each ledger keeps its newest 50 records."
   - A ledger holding 30 records would keep 20 under one and 30 under the other.

3. **apply_patch path limit.**
   - PRD, FP-05: a patch naming several files is scored at "at most **16** distinct paths".
   - IC, Post-tool-use reply: "At most ten paths of one payload are scored."
   - For a patch naming 12 files, one text scores all 12 and the other scores only 10.

4. **Catalogue 17, tailing-negation form.**
   - PRD, FP-01: the parallelism form is weight-zero writing advice, and "the **tailing-negation form** is score-moving".
   - IC, `scripts/detect.py` → Findings: "Both forms of catalogue 17 are writing advice and carry weight zero."
   - The tailing-negation form cannot both move the score and carry weight zero.

5. **Environment default mode versus stored level.**
   - PRD, FP-04 Boundary: when nothing valid is stored the level is `full`, "unless the environment supplies one of those four words". The environment is only a fallback for the stored level.
   - IC, Naming conventions → Host environment: `PROSECHECK_DEFAULT_MODE` "when it is set, it takes precedence over the stored level."
   - If `strict` is stored and the variable says `lite`, the PRD gives `strict` and the IC gives `lite`.

6. **Session-prose score threshold in `stats`.**
   - PRD, FP-06 `stats`: the score is printed only when the trimmed slice is "longer than 200 characters".
   - IC, `stats` → Reply: the score line appears "when the scored slice is longer than 500 characters".
   - A 300-character slice gets a score line under one and not under the other.

7. **`stats` transcript selection.**
   - PRD, FP-06 `stats`: "a named transcript wins over a newer one."
   - IC, `stats` → Transcript rows: "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
   - With a named transcript and a newer one in `projects`, each text reads a different file.

8. **Which operand the detector scans when several are given.**
   - PRD, FP-01 Boundary, and IC, Global observables and "Several file operands": the first file is scanned.
   - IC, `scripts/detect.py` → Signature: "When several operands are given, the last one is the file scanned."
   - This disagreement is inside the IC. With two operands the scanned file cannot be both the first and the last.

## Within the PRD

9. **Where the detector's usage message goes.**
   - PRD, FP-01 Public entry: "The usage message goes to the error stream, so that standard output carries only reports."
   - PRD, FP-01 Boundary: help "prints the usage message to standard output and succeeds." The IC also says standard output.
   - Help usage cannot go to both standard error and standard output.

10. **Single decisive family at low confidence.**
    - PRD, FP-01 scoring bullet: "A decisive finding always lifts the score to at least 45, whatever the confidence."
    - PRD, FP-01 decisive bullet: a single decisive family reaches 45 "only when confidence is above `low`", and "does not take that 45 floor" at `none` or `low`.
    - A short text with one decisive finding gets the 45 floor under one statement and does not under the other.

11. **Hedge stacking weight.**
    - PRD, FP-01: pattern 54 is one of the twelve writing-advice patterns that "never change the score".
    - PRD, FP-01 family rule for 54: "Each sentence with stacked hedges adds to the score."
    - Pattern 54 cannot both leave the score unchanged and add to it.

12. **Single transition word.**
    - PRD, FP-01 family rule for 36 (last sentence): "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
    - PRD, FP-01 family rule for 37: it fires on "two or more sentence-opening transitions ... in one paragraph".
    - One sentence opening with "However," fires 37 under the first statement and does not under the second.

13. **Numeric span written in words.**
    - PRD, FP-01 family rule for 61: "A numeric span written in words, such as from 9 to 5, is a false range (15)."
    - PRD, FP-01 family rule for 15: it covers only the rhetorical sweep from a "dawn / birth / humble ..." start to a "modern / mighty ..." end. "from 9 to 5" matches neither shape.
    - "from 9 to 5" cannot be a false range and also fall outside the rule for false ranges.

14. **Markdown hard break in cleanup.**
    - PRD, FP-03 Normal: "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
    - PRD, FP-03 Boundary: trailing whitespace is removed "even when two spaces were meant as a markdown hard break. That collapse is required, not optional."
    - A line ending in two spaces is either kept or trimmed.

15. **No-break spaces in cleanup.**
    - PRD, Terminology → Character cleanup: "Every no-break space becomes an ordinary space."
    - PRD, FP-03 Normalized: U+00A0 and U+202F are kept next to a digit, before `:;!?»›%€`, or after `«‹`.
    - A no-break space between digits is either converted or kept.

16. **"stop prosecheck" trigger.**
    - PRD, FP-04: "A prompt that contains `stop prosecheck` anywhere switches the tool off."
    - PRD, FP-06: "stop prosecheck" only counts as the entire prompt. "The same words with anything else before or after them are an ordinary prompt." The IC says the same.
    - "please stop prosecheck now" either switches the tool off or is an ordinary prompt.

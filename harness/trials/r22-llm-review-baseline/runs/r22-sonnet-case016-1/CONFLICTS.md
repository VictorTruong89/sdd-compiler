# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

## Conflicts between the PRD and the Interface Contract

1. **Session ledger retention.**
   - PRD, Non-functional constraints → Privacy: a ledger more than seven days old is gone; one seven days old or younger is kept. FP-06 `show` says the same.
   - IC, Naming conventions → Config filenames: "A ledger untouched for more than one day is deleted at the next session start."
   - A ledger that is three days old would be kept under one rule and deleted under the other.

2. **Number of ledger records kept.**
   - PRD, FP-05: "At most the newest 20 records are kept."
   - IC, Global observables → Plugin config and ledger: "Each ledger keeps its newest 50 records."
   - A ledger with 30 records would hold 20 under one rule and 30 under the other.

3. **Which file is scanned when several operands are given.**
   - PRD, FP-01 Boundary: "the first file is scanned". IC, Global observables and "Several file operands": the first operand is scanned.
   - IC, `scripts/detect.py` → Signature: "When several operands are given, the last one is the file scanned."
   - Both are IC statements about the same case, and they disagree with each other. The IC Signature rule also disagrees with the PRD.

4. **Whether catalogue 17's tailing-negation form moves the score.**
   - PRD, FP-01: the parallelism form is weight-zero writing advice, and the tailing-negation form "is score-moving".
   - IC, `scripts/detect.py` → Findings: "Both forms of catalogue 17 are writing advice and carry weight zero."
   - The tailing-negation form cannot both move the score and carry weight zero.

5. **Precedence of `PROSECHECK_DEFAULT_MODE`.**
   - PRD, FP-04 Boundary: the environment word is used only "when nothing valid is stored". A valid stored level wins.
   - IC, Naming conventions → Host environment: `PROSECHECK_DEFAULT_MODE` "takes precedence over the stored level".
   - With `strict` stored and the variable set to `lite`, the level cannot be both.

6. **Maximum paths scored from one apply_patch payload.**
   - PRD, FP-05: "at most **16** distinct paths".
   - IC, Post-tool-use reply: "At most ten paths of one payload are scored."
   - A patch naming 12 files would have 12 scored under one rule and 10 under the other.

7. **Minimum slice length for the `stats` session-prose score.**
   - PRD, FP-06 `stats`: printed only when the trimmed slice is longer than 200 characters.
   - IC, `stats` → Reply: printed "when the scored slice is longer than 500 characters".
   - A 300-character slice would get a score under one rule and none under the other.

8. **Named transcript versus newer transcript in `stats`.**
   - PRD, FP-06 `stats`: "a named transcript wins over a newer one".
   - IC, `stats` → Transcript rows: "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
   - The two cannot both hold when a named transcript exists and a newer one sits in `projects`.

## Conflicts inside the PRD

9. **Single decisive finding and the 45 floor.**
   - FP-01: "A decisive finding always lifts the score to at least 45, whatever the confidence."
   - FP-01, the next paragraph: a single decisive family reaches 45 "only when confidence is above `low`", and at `none` or `low` confidence "does not take that 45 floor".
   - A lone decisive finding in a document of 30 words (confidence `none`) cannot be both floored and not floored.

10. **Where the usage message goes.**
    - FP-01 Public entry: "The usage message goes to the error stream, so that standard output carries only reports."
    - FP-01 Boundary: help "prints the usage message to standard output and succeeds". The IC also says standard output.
    - Usage cannot go to both streams. The IC agrees with the boundary text, not the Public entry text.

11. **No-break spaces during cleanup.**
    - Terminology → Character cleanup: "Every no-break space becomes an ordinary space."
    - FP-03: a no-break space or narrow no-break space is kept when a digit is beside it, or it comes before `:` `;` `!` `?` `»` `›` `%` `€`, or after `«` `‹`.
    - A no-break space between two digits is either converted or kept.

12. **Two trailing spaces (markdown hard break).**
    - FP-03 Normal: "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
    - FP-03 Boundary: trailing whitespace "is removed even when two spaces were meant as a markdown hard break. That collapse is required."
    - The two spaces cannot be both kept and removed.

13. **Transition clusters: one opener or two.**
    - FP-01, formulaic challenges (36): "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
    - FP-01, transition clusters (37): it needs "two or more sentence-opening transitions ... in one paragraph".
    - A paragraph with exactly one transition opener either fires 37 or does not.

14. **"stop prosecheck" as the entire prompt or anywhere in the prompt.**
    - FP-04: "A prompt that contains `stop prosecheck` anywhere switches the tool off."
    - FP-06: the phrases as the entire prompt store `off`; "the same words with anything else before or after them are an ordinary prompt". IC, `/prosecheck` → Stop phrases and `lite`...`on`, agrees with FP-06.
    - "Please stop prosecheck now" either switches the tool off or is an ordinary prompt.

15. **`utm_source` as an AI tracking parameter.**
    - FP-01, chat reference markup (64): "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
    - FP-01, AI tracking parameters (65): it fires only when the value is exactly one of the listed chat-product hosts.
    - A link with `utm_source=newsletter` either is or is not an AI tracking parameter.

16. **Whether a numeric "from 9 to 5" is a false range.**
    - FP-01, hyphen-for-en-dash (61): "A numeric span written in words, such as from 9 to 5, is a false range (15)."
    - FP-01, false ranges (15): "only the rhetorical sweep between a beginning and a grand or present-day end", for example "from the dawn ... to the modern". "From 9 to 5" does not fit that shape.
    - "from 9 to 5" cannot be both a false range and outside it.

## Conflicts inside the Interface Contract

(The conflict between the "first" and "last" operand rules in item 3 is also inside the IC.)

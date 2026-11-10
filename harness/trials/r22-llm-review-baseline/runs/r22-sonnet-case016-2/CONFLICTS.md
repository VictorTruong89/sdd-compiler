# Specification conflicts

Files: `PRD` = spec/Full_PRD.md, `IC` = spec/Interface_Contract.md.

## Conflicts inside the PRD

1. **Usage message stream.**
   - PRD, FP-01 "Public entry": "The usage message goes to the error stream, so that standard output carries only reports."
   - PRD, FP-01 "Boundary / error behavior": "Help ... prints the usage message to standard output and succeeds."
   - One help invocation cannot send its usage text to stderr and to stdout.

2. **Floor for a single decisive finding.**
   - PRD, FP-01 scoring bullets: "A decisive finding always lifts the score to at least 45, whatever the confidence."
   - Next decisive bullet: "A single decisive family raises it to at least 45 only when confidence is above `low`... at `none` or `low` confidence does not take that 45 floor."
   - A single decisive finding at `low` confidence either gets the 45 floor or it does not.

3. **Hedge stacking is both weightless and score-adding.**
   - PRD, FP-01: pattern 54 is one of the 12 writing-advice patterns that "never change the score".
   - PRD, FP-01 family rule for Hedge stacking (54): "Each sentence with stacked hedges adds to the score."
   - Pattern 54 cannot both add to the score and never change it.

4. **Transition words: one sentence vs two.**
   - PRD, FP-01 Formulaic challenges (36): "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
   - PRD, FP-01 Transition clusters (37): fires on "two or more sentence-opening transitions ... in one paragraph".
   - A paragraph with one transition-opening sentence either fires 37 or it does not.

5. **No-break space under cleanup.**
   - PRD, Terminology "Character cleanup": "Every no-break space becomes an ordinary space."
   - PRD, FP-03 "What is normalized": a no-break space (U+00A0 or U+202F) next to a digit, before `:;!?»›%€`, or after `«‹` is kept.
   - A no-break space beside a digit is either converted or kept.

6. **Two trailing spaces (markdown hard break).**
   - PRD, FP-03 "What is trimmed": "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
   - PRD, FP-03 "Boundary / error behavior": "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required."
   - The same two trailing spaces cannot be both kept and removed.

7. **"stop prosecheck" trigger.**
   - PRD, FP-04: "A prompt that contains `stop prosecheck` anywhere switches the tool off."
   - PRD, FP-06: the phrases "as the entire prompt ... also store `off`; the same words with anything else before or after them are an ordinary prompt."
   - A prompt such as "please stop prosecheck now" either switches the tool off or is an ordinary prompt.

## Conflicts between the PRD and the Interface Contract

8. **Session ledger length.**
   - PRD, FP-05: "At most the newest 20 records are kept."
   - IC, "Global observables / Plugin config and ledger": "Each ledger keeps its newest 50 records."
   - The retained record cap cannot be both 20 and 50.

9. **Ledger retention age.**
   - PRD, Non-functional "Privacy" and FP-06 `show`: a ledger more than seven days old is gone, and one seven days old or younger is kept.
   - IC, "Config filenames": "A ledger untouched for more than one day is deleted at the next session start."
   - A ledger two days old is either kept (PRD) or deleted (IC).

10. **apply_patch path limit.**
    - PRD, FP-05: an apply_patch payload is scored "at most 16 distinct paths".
    - IC, "Post-tool-use reply": "At most ten paths of one payload are scored."
    - The 11th–16th file of a patch is either scored or not.

11. **Weight of catalogue 17's tailing-negation form.**
    - PRD, FP-01: the parallelism form is weight-zero advice, but "The tailing-negation form is score-moving". The PRD counts 50 score-moving patterns on that basis.
    - IC, `scripts/detect.py` Findings: "Both forms of catalogue 17 are writing advice and carry weight zero."
    - The tailing-negation form either moves the score or carries weight zero.

12. **Which operand is scanned when several are given.**
    - PRD, FP-01 and IC, "Several file operands": the first file is scanned.
    - IC, `scripts/detect.py` Signature: "When several operands are given, the last one is the file scanned."
    - The IC contradicts itself and the PRD: with two operands, one file is scanned, and it is either the first or the last.

13. **Environment default level vs stored level.**
    - PRD, FP-04: a stored valid level is used. The environment word applies only "when nothing valid is stored".
    - IC, "Host environment": `PROSECHECK_DEFAULT_MODE`, "when it is set, it takes precedence over the stored level."
    - With `strict` stored and the variable set to `lite`, the level is either `strict` or `lite`.

14. **Minimum slice length for the session-prose score in `stats`.**
    - PRD, FP-06 `stats`: the score is printed only when the trimmed slice is "longer than 200 characters".
    - IC, `stats` Reply: the score appears "when the scored slice is longer than 500 characters", otherwise it is absent.
    - A 300-character slice either gets a score line or does not.

15. **Named transcript vs newer transcript in `stats`.**
    - PRD, FP-06 `stats`: "a named transcript wins over a newer one."
    - IC, `stats` Transcript rows: "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."
    - When both exist, `stats` reads either the named one or the newer one.

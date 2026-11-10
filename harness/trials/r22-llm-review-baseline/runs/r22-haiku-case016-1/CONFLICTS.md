# Specification conflicts

Scope: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (IC), `spec/Hardware_Requirements.md` (HW).
Each entry quotes both sides with file and section, then says why both cannot hold.
HW was checked against the PRD and IC (Python 3.9+, Node.js, CPU-only, Linux/macOS/Windows) and has no disagreement.

---

## 1. Where the usage message is printed

- **PRD, FP-01, "Public entry" (line 82–83):** "The usage message goes to the error stream, so that standard output carries only reports."
- **PRD, FP-01, "Boundary / error behavior" (line 167):** "Help (the help switch or the short help alias) prints the usage message to standard output and succeeds."

The same usage message cannot go to the error stream and to standard output in the same case. (IC `scripts/detect.py` > Usage, line 110, follows line 167.)

## 2. Floor for a single decisive finding

- **PRD, FP-01, "Normal behavior" (line 93):** "A decisive finding always lifts the score to at least 45, whatever the confidence."
- **PRD, FP-01, "Normal behavior" (line 94):** "A single decisive family at `none` or `low` confidence does not take that 45 floor."

One says a decisive finding always gets a floor of 45 whatever the confidence, and the other says it does not when confidence is `none` or `low`.

## 3. Whether hedge stacking changes the score

- **PRD, FP-01, "Normal behavior" (line 90):** catalogue 54 (hedge stacking) is one of the 12 "writing advice" numbers, "weight zero", and "a document scores the same as the same document without that phrasing whenever the score-moving findings are the same."
- **PRD, FP-01, "Family rules" (line 128):** "Each sentence with stacked hedges adds to the score."

A document with stacked hedges and no other score-moving findings must score the same as one without them (line 90) and must score higher (line 128).

## 4. Whether the tailing-negation form of catalogue 17 moves the score

- **PRD, FP-01, "Normal behavior" (line 91):** "The **tailing-negation form** is score-moving."
- **IC, `scripts/detect.py` > Findings (line 148):** "Both forms of catalogue 17 are writing advice and carry weight zero."

The PRD makes the tailing-negation form score-moving, and the IC makes it weight zero. (The PRD's advice list on line 90 does not include 17, so the PRD is consistent with itself here.)

## 5. Whether every no-break space is turned into a space

- **PRD, Terminology, "Character cleanup" (line 30):** "Every no-break space becomes an ordinary space."
- **PRD, FP-03, "What is normalized" (line 212):** a no-break space (U+00A0) or narrow no-break space (U+202F) is kept when it holds something together: a digit on either side, before `:` `;` `!` `?` `»` `›` `%` `€`, or after `«` `‹`.

"Every" no-break space cannot become an ordinary space while the same rule keeps some of them as they are.

## 6. Whether a markdown hard break's trailing spaces are kept

- **PRD, FP-03, "What is trimmed" (line 214):** "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
- **PRD, FP-03, "Boundary / error behavior" (line 223):** "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required, not optional."

The same two trailing spaces on a line of prose are both kept and removed.

## 7. Whether every zero-width character in the text is invisible

- **PRD, FP-01, "Normal behavior" (line 159):** "A zero-width character inside the text is an invisible character."
- **PRD, FP-03, "What is removed" (line 211) and "Cleanup agrees with detection" (line 215):** a zero-width joiner, non-joiner, zero-width space, or variation selector in the listed positions (for example beside a Hebrew or Arabic letter, or beside an emoji) is kept, and "a character the scrub keeps is not counted as an invisible character."

Line 159 says every zero-width character inside the text counts as invisible, while lines 211 and 215 say some such characters are not counted. (Line 129 already allows this exception, so line 159 is the one that conflicts.)

## 8. Whether any `utm_source` value triggers catalogue 65

- **PRD, FP-01, "Family rules," chat reference markup (line 131):** "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
- **PRD, FP-01, "Family rules," AI tracking parameters (line 132):** it "fires only when that whole host name is one of those domains" (chatgpt.com, claude.ai, and the others listed).

A `utm_source` with a value outside that list is both a tracking parameter under line 131 and not one under line 132.

## 9. Whether `stop prosecheck` must be the whole prompt

- **PRD, FP-04, "Normal behavior" (line 240):** "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- **PRD, FP-06, "Normal behavior" (line 285):** the stop phrases store `off` "as the entire prompt"; "the same words with anything else before or after them are an ordinary prompt."
- **IC, `/prosecheck` > Stop phrases (line 411):** "The entire prompt `stop prosecheck`, or the entire prompt `prosecheck off`" (agrees with FP-06).

A prompt such as "please stop prosecheck, I want to keep it" both switches the tool off (FP-04) and is an ordinary prompt that leaves it on (FP-06).

## 10. Precedence of the `PROSECHECK_DEFAULT_MODE` environment variable

- **PRD, FP-04, "Boundary / error behavior" (line 246):** "When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words, in which case that word is used." The environment applies only when nothing valid is stored.
- **IC, "Naming conventions" > Host environment (line 63):** `PROSECHECK_DEFAULT_MODE` "when it is set, it takes precedence over the stored level."

If a valid level is stored and the variable is set to a different word, one says the stored level is used and the other says the variable wins.

## 11. Whether `.pdf` is a prose file

- **PRD, FP-06, "Normal behavior" (line 290):** "rows appear after prose files, including `.docx` and `.pdf` deliverables, are saved."
- **PRD, Terminology, "Prose file" (line 27):** "a saved file whose extension is in the twenty-format set." **PRD, FP-02, "Boundary" (line 195):** "`.pdf` and `.rtf` are not among the twenty formats." (Also PRD non-goal, line 68.)
- The IC's empty-ledger reply (IC `show` > Empty ledger, line 582) repeats the same ".docx and .pdf" wording.

`.pdf` cannot be a prose file in the twenty-format set and also be a prose file that gets a prose deliverable row.

## 12. How many file operands the detector accepts

- **IC, `scripts/detect.py` (line 21):** "optional switches and at most one file operand."
- **IC, `scripts/detect.py` > Several file operands (line 180):** "With two or more operands the first is scanned and its report printed (exit 0)." **PRD, FP-01, "Boundary" (line 168):** "Two or more file operands still succeed."

"At most one" forbids the multi-operand runs that the other two statements require to succeed.

## 13. Which operand is scanned when several are given

- **IC, `scripts/detect.py` > Signature (line 106):** "When several operands are given, the last one is the file scanned."
- **IC, `scripts/detect.py` > Several file operands (line 180):** "the first is scanned"; **PRD, FP-01, "Boundary" (line 168):** "the first file is scanned."

The last operand and the first operand cannot both be the one scanned.

## 14. Maximum number of paths in one `apply_patch` payload

- **PRD, FP-05, "Normal behavior" (line 264):** "An apply_patch payload that names several files is scored one file at a time, at most **16** distinct paths."
- **IC, Post-tool-use reply (line 260):** "At most ten paths of one payload are scored."

The same payload with 11 to 16 distinct paths is scored under one rule and not scored under the other.

## 15. Number of records a session ledger keeps

- **PRD, FP-05, "Normal behavior" (line 265):** "At most the newest **20** records are kept."
- **IC, "Plugin config and ledger" (line 91):** "Each ledger keeps its newest **50** records."

A ledger with 30 records must keep 20 under one rule and 50 under the other.

## 16. How long a session ledger is kept

- **PRD, Non-functional constraints, "Privacy" (line 57):** "A ledger whose last modification is more than **seven days** old is gone by the time a later session is in use; a ledger seven days old or younger is kept." (Repeated in PRD, FP-06, "Normal behavior," line 290.)
- **IC, "Config filenames" (line 65):** "A ledger untouched for more than **one day** is deleted at the next session start."

A ledger that is two days old is kept under the PRD and deleted under the IC.

## 17. Which transcript `stats` reads when a newer one exists

- **PRD, FP-06, "Normal behavior" (line 292):** "a named transcript wins over a newer one."
- **IC, `transcript_path` (line 681) and `stats` > Signature (line 646):** the host-named `transcript_path` is read when supplied.
- **IC, `stats` > Transcript rows (line 650):** "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."

Line 650 says the newer transcript is read in the case where lines 646, 681, and PRD line 292 say the named one is read.

## 18. Minimum slice length for the session-prose score

- **PRD, FP-06, "Normal behavior" (line 292):** "the session-prose score is printed only when that slice, with surrounding whitespace trimmed, is longer than **200** characters."
- **IC, `stats` > Reply (line 662):** "When the scored slice is longer than **500** characters, the reply contains `session prose ai_tell_score: <score>`."

A slice of 300 characters gets a score line under the PRD and none under the IC.

## 19. Whether one use of a model-dialect word fires the family

- **PRD, FP-04, "Normal behavior" (line 236):** "Every word on that banned-vocabulary list, used as a standalone word in otherwise ordinary prose, fires a machine-checked family of FP-01 under that family's rule (AI vocabulary; model-dialect vocabulary, which **needs two hits**, for its dialect words)."
- **PRD, FP-01, "Family rules," model-dialect vocabulary (line 101):** has no two-hit condition.

Within line 236, a single standalone use of "genuinely" or "nuanced" both fires the family ("every ... fires") and does not fire it ("needs two hits"). Line 101 gives no such condition at all.

## 20. Whether the welcome can name prosecheck when the contract forbids it

- **PRD, FP-04, "Normal behavior" (line 235):** the contract is "silent — never announce the contract, never name prosecheck, never report a score ..."
- **PRD, FP-04, "Normal behavior" (line 238):** the first-run welcome is "prepended to the contract" and "says that prosecheck is installed and on ... and that it is shown once."

If the welcome is shown to the user as it says, the agent must name prosecheck, and the same contract forbids that.

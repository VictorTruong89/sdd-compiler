# Specification conflicts

Scope: `spec/Full_PRD.md` (PRD), `spec/Hardware_Requirements.md` (HW), `spec/Interface_Contract.md` (IC). Line numbers are the file's own line numbers. Each entry is a pair of statements that cannot both hold for the same case.

---

## 1. Usage message stream for `--help`

- **PRD, FP-01 "Public entry" (line 82):** "The usage message goes to the error stream, so that standard output carries only reports."
- **PRD, FP-01 "Boundary / error behavior" (line 167):** "Help (the help switch or the short help alias) prints the usage message to standard output and succeeds."
- **IC, `scripts/detect.py` > Usage (line 110):** "`--help` and `-h` write the usage message to standard output and exit 0."

Why: The same usage message cannot be both on the error stream (line 82) and on standard output (lines 167 and 110).

---

## 2. Which no-break spaces are normalized

- **PRD, Terminology, "Character cleanup" (line 30):** "Every no-break space becomes an ordinary space."
- **PRD, FP-03 "Normal behavior" (line 212):** "every space separator other than U+0020 becomes U+0020, except a no-break space (U+00A0) ... that holds something together: one with a digit on either side, one before `:` `;` `!` `?` `»` `›` `%` `€`, or one after `«` `‹`."

Why: Line 30 requires every no-break space to become an ordinary space, while line 212 says some no-break spaces are kept unchanged.

---

## 3. Two trailing spaces (markdown hard break) under cleanup

- **PRD, FP-03 "Normal behavior" (line 214):** "Two trailing spaces that end a line of prose are a markdown hard break and are kept."
- **PRD, FP-03 "Boundary / error behavior" (line 223):** "Trailing whitespace at end of line is removed even when two spaces were meant as a markdown hard break. That collapse is required, not optional."

Why: Cleanup output for a line ending in two spaces either keeps those spaces (line 214) or removes them (line 223), and it cannot do both.

---

## 4. Score floor for a single decisive finding at low confidence

- **PRD, FP-01 "Normal behavior" (line 93):** "A decisive finding always lifts the score to at least 45, whatever the confidence."
- **PRD, FP-01 "Normal behavior" (line 94):** "A single decisive family raises it to **at least 45** only when confidence is above `low`. A single decisive family at `none` or `low` confidence does not take that 45 floor."

Why: Line 93 gives a 45 floor for a decisive finding at any confidence, and line 94 denies that floor at `none` and `low` confidence.

---

## 5. Scope of the "stop prosecheck" / "prosecheck off" phrases

- **PRD, FP-04 "Normal behavior" (line 240):** "A prompt that contains `stop prosecheck` anywhere switches the tool off."
- **PRD, FP-06 "Normal behavior" (line 285):** "The phrases 'stop prosecheck' and 'prosecheck off' as the entire prompt (letter case ignored) also store `off`; the same words with anything else before or after them are an ordinary prompt."
- **IC, `/prosecheck` > Stop phrases (line 411):** "The entire prompt `stop prosecheck`, or the entire prompt `prosecheck off`..."

Why: A prompt such as "please stop prosecheck for this file" switches the tool off under line 240 but is an ordinary prompt under line 285.

---

## 6. Whether hedge stacking affects the score

- **PRD, FP-01 "Normal behavior" (line 128), family 54:** "Each sentence with stacked hedges adds to the score."
- **PRD, FP-01 "Normal behavior" (line 90):** lists "54 (hedge stacking)" among the 12 "writing advice" numbers, "reported, weight zero", and states "A writing-advice finding never changes the score ... a document scores the same as the same document without that phrasing".

Why: Line 128 says stacked hedges raise the score, while line 90 says hedge stacking is weight-zero advice that never changes the score.

---

## 7. `utm_source` as an AI tracking parameter

- **PRD, FP-01 "Normal behavior" (line 131), family 64:** "Any `utm_source` parameter left in a link is an AI tracking parameter (65)."
- **PRD, FP-01 "Normal behavior" (line 132), family 65:** "The value is the host name after the equals sign ... it fires only when that whole host name is one of those domains."

Why: Line 131 makes every `utm_source` parameter fire family 65, while line 132 fires it only when the value is one of the listed AI domains.

---

## 8. How many sentence-opening transitions make a transition cluster

- **PRD, FP-01 "Normal behavior" (line 116), family 36:** "A single sentence that opens with one of the transition words of 37 already fires transition clusters."
- **PRD, FP-01 "Normal behavior" (line 117), family 37:** "Transition clusters (37): two or more sentence-opening transitions ... in one paragraph."

Why: Line 116 says one transition-opening sentence fires family 37, while line 117 requires two or more in one paragraph.

---

## 9. Whether a single model-dialect word fires its family

- **PRD, FP-04 "Normal behavior" (line 236):** "Every word on that banned-vocabulary list, used as a standalone word in otherwise ordinary prose, fires a machine-checked family ... (AI vocabulary; model-dialect vocabulary, which needs two hits, for its dialect words)."
- **PRD, FP-01 "Normal behavior" (lines 99 and 101):** family rules state the conditions for firing, and the model-dialect family (line 101) lists its words with no two-hit condition.

Why: Line 236 says each standalone dialect word such as "genuinely" fires family 2, yet the same sentence says that family needs two hits, so one such word cannot both fire it and fail to fire it.

---

## 10. Whether Node.js is needed to run the detector

- **HW, "Execution profiles" > "CPU baseline" > Setup (line 18):** "Setup: Python 3.9 or newer and Node.js." The profile covers the detector run (line 13: "the detector script runs from this repository's source tree, scores prose ..., and prints its JSON report").
- **PRD, Public surface inventory (line 36):** "The detector needs Python 3.9 or newer and nothing else. The plugin's saved-file and command hooks need Node.js."
- **PRD, Non-functional constraints > Language floor (line 53):** "Python 3.9 or newer for the detector. Node.js for the hooks."

Why: The hardware document makes Node.js a setup requirement of the detector profile, while the PRD says the detector needs nothing beyond Python.

---

## 11. Which file is scanned when several operands are given

- **IC, `scripts/detect.py` > Signature (line 106):** "When several operands are given, the last one is the file scanned."
- **IC, `scripts/detect.py` > Several file operands (line 180):** "With two or more operands the first is scanned and its report printed (exit 0)."
- **PRD, FP-01 "Boundary / error behavior" (line 168):** "Two or more file operands still succeed: the first file is scanned, and the error stream notes that only the first file was scanned and names that file."

Why: The contract's signature section says the last operand is scanned, while its own later section and the PRD say the first operand is scanned.

---

## 12. Ledger retention count

- **PRD, FP-05 "Normal behavior" (line 265):** "At most the newest 20 records are kept."
- **IC, Global observables > Plugin config and ledger (line 91):** "Each ledger keeps its newest 50 records."

Why: A ledger cannot keep both at most 20 records (PRD) and its newest 50 records (IC).

---

## 13. Ledger lifetime

- **PRD, Non-functional constraints > Privacy (line 57):** "A ledger whose last modification is more than seven days old is gone by the time a later session is in use; a ledger seven days old or younger is kept."
- **PRD, FP-06 "Normal behavior" (line 290):** "A ledger whose last modification is more than seven days old is not listed by a later session; one seven days old or younger is."
- **IC, Naming conventions > Config filenames (line 65):** "A ledger untouched for more than one day is deleted at the next session start."

Why: A ledger that is two days old must be kept until seven days under the PRD, but is deleted at the next session start under the contract.

---

## 14. Precedence of `PROSECHECK_DEFAULT_MODE` over the stored level

- **PRD, FP-04 "Boundary / error behavior" (line 246):** "Any stored value other than `off`, `lite`, `full`, or `strict` is ignored. When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words, in which case that word is used."
- **IC, Naming conventions > Host environment (line 63):** "`PROSECHECK_DEFAULT_MODE` — ... when it is set, it takes precedence over the stored level."

Why: The PRD uses the environment word only when nothing valid is stored, whereas the contract says it overrides a valid stored level, so a valid stored `strict` with the variable set to `off` gives different results under each.

---

## 15. Weight of catalogue 17's tailing-negation form

- **PRD, FP-01 "Normal behavior" (line 91):** "The **tailing-negation form** is score-moving: a clause followed by a comma and a short 'no ...' tail of the stock kind."
- **IC, `scripts/detect.py` > Report > Findings (line 148):** "Both forms of catalogue 17 are writing advice and carry weight zero."

Why: The PRD says the tailing-negation form moves the score, and the contract says both forms carry weight zero.

---

## 16. Number of paths scored from one `apply_patch` payload

- **PRD, FP-05 "Normal behavior" (line 264):** "An apply_patch payload that names several files is scored one file at a time, at most **16** distinct paths."
- **IC, Post-tool-use reply (line 260):** "At most ten paths of one payload are scored."

Why: A payload naming 12 distinct files is scored for 16 paths under the PRD and for 10 under the contract.

---

## 17. Which transcript `stats` reads when a newer one exists

- **PRD, FP-06 "Normal behavior" (line 292):** "`stats` reads the session transcript the host named, or else the newest transcript ... a named transcript wins over a newer one."
- **IC, `transcript_path` / `stats` > Transcript rows (line 650):** "When the `projects` folder holds a transcript newer than the named one, the newer transcript is read."

Why: When the host names a transcript and a newer one exists, the PRD reads the named one and the contract reads the newer one.

---

## 18. Length threshold for printing the session-prose score

- **PRD, FP-06 "Normal behavior" (line 292):** "the session-prose score is printed only when that slice, with surrounding whitespace trimmed, is longer than 200 characters."
- **IC, `stats` > Reply (line 662):** "When the scored slice is longer than 500 characters, the reply contains `session prose ai_tell_score: <score>` once."

Why: A slice of 300 characters gets a score printed under the PRD (over 200) and no score under the contract (not over 500).

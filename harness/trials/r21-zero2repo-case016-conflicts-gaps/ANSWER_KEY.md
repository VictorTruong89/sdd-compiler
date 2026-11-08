# Answer key (round 21, case016) — never given to an agent

Written 2026-11-05, before any model call. Planted spec: `work/spec-planted/` (git-ignored), made by
`python3 notes/plant.py work/spec-planted <the 33 items below>`: **41 edits for 33 items**, words
18 964 → 18 845; sha256 `Full_PRD.md` 05da27a5…, `Interface_Contract.md` 546980cb…,
`Hardware_Requirements.md` 11bb8c7d… (unchanged). Side-A, side-B and removed phrases are the short
anchors in `notes/plant.py` (`PHRASES`, `KEY`); alternative builds in `notes/sides.py`; probes in
`notes/probe.py`; footprint test names in `notes/footprint.json`.

**Probe readings:** *upstream* = side A (conflict) or the removed fact (gap); *alternative* = side B
or the gap's alternative. Every probe was checked on the base build (upstream on all 47 candidates) and
on every alternative copy (alternative on its own item, upstream on the others): 0 mismatches
(`work/probe_check.log`).

## Kept conflicts (17)

Side A stays as stated in the original spec; side B is one planted sentence, in the spec's own voice,
with no marker.

| Id | Side A (original) | Side B (planted) | Side B in | Footprint |
|---|---|---|---|---|
| C01 | 54 hedge stacking is writing advice, does not move the score | stacked hedges add to the score | PRD | 2 |
| C06 | a single decisive family takes the 45 floor only when confidence is above `low` | a decisive finding always lifts to 45, whatever the confidence | PRD | 2 |
| C08 | with several file operands, the first is scanned and stderr notes it | the last operand is the file scanned | Contract | 3 |
| C09 | `--help` writes usage to stdout, exit 0 | usage goes to the error stream | PRD | 3 |
| C11 | transitions fire 37 only for two or more sentence-opening transitions | a single transition already fires | PRD | 1 |
| C12 | false range (15) only for a rhetorical sweep to a grand or present-day end | "from N to M" is a false range | PRD | 2 |
| C13 | 65 fires only when the whole host is a listed AI domain | any `utm_source` parameter left in a link fires | PRD | 1 |
| C15 | a no-break space that holds something together is kept by cleanup | every no-break space becomes an ordinary space | PRD | 3 |
| C16 | cleanup removes trailing spaces even when meant as a hard break | two trailing spaces are a hard break and are kept | PRD | 1 |
| C17 | `apply_patch` scores at most 16 distinct paths | at most ten paths are scored | Contract | 2 |
| C18 | a ledger keeps at most the newest 20 records | the newest 50 records | Contract | 1 |
| C19 | a ledger more than seven days old is gone | more than one day old is deleted | Contract | 1 |
| C20 | the environment level applies only when nothing valid is stored | the environment level takes precedence over the stored level | Contract | 2 |
| C21 | stop phrases switch off only as the entire prompt | the phrase anywhere in the prompt switches off | PRD | 1 |
| C22 | stats scores session prose longer than 200 characters | longer than 500 characters | Contract | 2 |
| C23 | stats: a named transcript wins over a newer one | the newer transcript is read | Contract | 1 |
| C25 | catalogue 17's tailing-negation form is score-moving | both forms of 17 are writing advice | Contract | 1 |

## Kept gaps (16)

Every place that states the fact is edited; no marker and no "unspecified" wording is added.

| Id | Removed fact (upstream) | Alternative (probe) | Places edited | Footprint |
|---|---|---|---|---|
| G01 | model dialect (2) fires on two or more hits | fires on one hit | PRD | 2 |
| G02 | a banned word split only by zero-width characters still fires | the split word does not fire | PRD | 2 |
| G03 | a word with lookalike letters still matches the vocabulary finding | does not match | PRD | 1 |
| G04 | input with a NUL byte (no UTF-16 BOM) is empty input | NUL bytes decoded as text | PRD ×2, Contract | 1 |
| G05 | indented code blocks are not scanned | indented code is scanned | PRD | 2 |
| G06 | cleanup keeps a line's own indentation | indentation stripped | PRD | 1 |
| G07 | cleanup keeps the file's newline convention | CRLF becomes LF | PRD | 1 |
| G08 | epub chapters in natural order (digit runs compare as numbers) | lexical order | PRD | 1 |
| G09 | no nudge at confidence `none` | nudge at confidence `none` | PRD ×2 | 1 |
| G10 | instruction file names are matched in any case | case-sensitive | PRD | 1 |
| G11 | paths under a `memory` directory are skipped | `memory/` not skipped | PRD | 1 |
| G12 | saved ledgers are owner-only | ledger written 0644 | PRD, Contract | 1 |
| G13 | assistant records sharing one message id count once | counted twice | PRD | 1 |
| G21 | a no-break space is a nonstandard space, never an invisible character | also counted as invisible | PRD | 3 |
| G30 | doctor stays successful when Python is missing (detector line kept) | detector line fails without Python | PRD, Contract | 1 |
| G33 | the welcome is not shown when the flag cannot be written | welcome shown even when unwritable | PRD ×2, Contract ×2 | 1 |

Footprint union of the 33 kept items: **50** tests, none shared between items; **core = 388 − 50 =
338** tests (`notes/footprint.json`).

## Dropped candidates (14), with the reason

| Id | Reason |
|---|---|
| C04, C05, C14, C26, G14 | footprint 0: no hidden test tells the two values apart |
| C02 (4), C07 (6), G19 (7), G25 (52), G24 (205) | footprint over 3; G24 is also stated in 3 places |
| C03 | shares a test with C01 (`listed_writing_advice_numbers…`) and one with G13 (a stats test); confirmed by a rerun |
| C10 | shares a test with G05 (`second_named_fire_inside_each_mask…`); tie at 2 tests, dropped from the larger kind |
| G67 | shares a test with G04 (`nul_without_utf16_bom…`); footprint 3 against 1; confirmed by a rerun |
| G60 | shares a test with C19 (`show_omits_a_ledger_only_when_older_than_seven_days`); footprint 3 against 1; confirmed by a rerun |

Overlap rule (as round 20, where G15 was dropped for sharing tests with G14): drop the item with the
larger footprint; on a tie, drop from the kind with more survivors.

## Found after the check run (2026-11-06, before the other 23 runs)

- **G01 is not a gap.** The removal edited the catalogue entry (original PRD line 102, planted line 101) but missed a second one in FP-04
  (planted PRD line 236: model-dialect vocabulary "needs two hits"). Criterion 2 was checked by key phrase, and
  this sentence used other words. G01 stays in the planted spec (the same in all three arms; a second
  compile is not approved) and in the scorer, but is **reported apart and not counted in set 2b**
  (`STATED_G` in `notes/plant.py`). Set 2b is over **15 gaps**.
- **G21 can be derived.** No sentence states it any more, but PRD 129 defines an invisible character as
  one that cleanup *removes*, and PRD 211–212 *normalize* a no-break space rather than remove it. A
  careful reader can derive the upstream value. G21 is kept and marked *derivable* in the tables.
- A search of the planted spec for every other kept gap's terms (zero-width, homoglyph, NUL, indent,
  CRLF, epub, confidence `none`, instruction names, `memory`, owner/permission, message id, Python
  missing, welcome) found no other statement of a removed fact.

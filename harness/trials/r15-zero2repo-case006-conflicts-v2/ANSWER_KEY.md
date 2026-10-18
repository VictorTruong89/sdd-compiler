# Answer key: conflicts planted in case006 (never shown to an agent)

> Written 2026-10-16, before the compile and before any agent run. The planted Markdown is made by
> `notes/plant.py work/spec-planted P1 P2 P3 P4 P6 P7 R1` from Zero2Repo case006's `public/` (stays in
> git-ignored `work/`: Zero2Repo has no licence file). Only the short phrases below are quoted.
> Design and reasons: `sdd/design/rel-02/rel02_brainstorm.md` S17 and this trial's `TRIAL.md`.

Side **A** is the text the case already had: click's behaviour, what the hidden tests check and what
the model may remember. Side **B** is the planted sentence: one place edited, in the spec's voice, no
marker. Lines are those of the planted files.

| Item | Distance | Kind | A (kept) | B (planted) | Footprint (hidden tests that flip A→B) |
|---|---|---|---|---|---|
| P1 | same paragraph (control) | direct | PRD 403 FP-14: "the runner removes that directory on exit" (no parent given) | PRD 403, same bullet: "always left in place after the block ends" | 1: `F14 …new_empty_dir_removed_when_no_parent` |
| P2 | across files | prose vs table | Contract 40, channels: "deprecation warning for a command, option or argument" → standard error | PRD 83 FP-01: a deprecated command's "deprecation warning on standard output" | 0 |
| P3 | across files | precedence | PRD 143 FP-03: command line, "then environment, then the default map" | Contract 234, `default_map` row: its values "take precedence over environment variables" | 3: `F03 …feature_switch_more_explicit_source_wins`, `F03 …fill_order_command_line_env_map_declared`, `F07 …default_map_string_splits_like_environment` |
| P4 | far, same file | rule inside a definition | PRD 145 FP-03: "A missing parameter still runs its callback" | PRD 28, Terminology "Callback": a parameter callback "is not called for a parameter that was omitted" and got no value | 1: `F03 …missing_parameter_still_runs_its_callback` |
| P6 | far, same file | direct value | PRD 107 FP-02: a "maximum content width that defaults to 80 columns" | PRD 340 FP-11: help pages use a "maximum content width of 100 columns" | 1: `F02 …help_rewrapped_to_width_capped_at_default_80` |
| P7 | same bullet | example against its rule | PRD 108 FP-02: "the default metavar is the type name in uppercase" | PRD 108, an example: an integer option `--count` appears "as `--count COUNT`" | 1: `F02 …value_option_metavar_is_type_name_not_parameter_name` |
| R1 | across files | prose vs table | PRD 271 FP-08: for confirm, "any other answer asks again" | Contract 286, `confirm` row: an answer other than yes, no or "an empty line counts as no" | 0 |

**Footprint union: 7 tests.** The *core score* of a run is its result on the other 469 tests.

## Candidates tried and dropped (step 0, no model call)

| Item | Why dropped |
|---|---|
| P5: example against its rule in FP-07 (an automatic-prefix key that includes the top-level command name) | footprint 7 (rule 3: at most 3) |
| R2: Terminology row "Leaf": a bare leaf shows help | footprint 238; it also changed 3 other probes |

## How each side is read (`notes/probe.py`, black box, written from this key and the Contract only)

| Item | Probe | A | B |
|---|---|---|---|
| P1 | `CliRunner().isolated_filesystem()` with no parent; does the folder exist afterwards? | gone | exists |
| P2 | a deprecated command run as a program; which stream has "deprecat" | stderr only | stdout only |
| P3 | `--name` with `envvar` set and `default_map={"name": …}` | environment value | default-map value |
| P4 | an omitted `--x` with a callback and no default; is the callback called? | called | not called |
| P6 | `--help` of a long description with `COLUMNS=200`; longest line | ≤ 80 | 81–100 |
| P7 | `--help` of `--count` with `type=INT` | `--count INTEGER` | `--count COUNT` |
| R1 | `confirm("Go?")` with input `maybe` then `y` | True (asked again) | False |

Other readings: `both` (P2 on both streams), `neither`, `error` (the probe program failed). Probe
checks: on the base build every probe reads A; on each side-B copy only its own item reads B.

## Phrases used for the exposure check

Each side's phrase above (in quotes) occurs exactly once in the planted Markdown. A run is
*exposed* to a side when some tool result in its transcript contains that phrase.

## Rulings for the settled round

All to side **B**, so that following a ruling cannot come from memory of click. Only items the
compiler reported get a ruling (as in `lend` round 4): `DECISIONS.md` (Markdown control) and the
export's adjudications carry the same rulings. Filled in after the compile: see `TRIAL.md`.

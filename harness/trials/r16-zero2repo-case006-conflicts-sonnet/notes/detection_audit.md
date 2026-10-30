# Detection audit (round 16, Sonnet) — for the owner

One table per planted item. **Lines** are every line of the run's `NOTES.md` that matches the
item's keywords (cut at 300 characters); **Reading** is the assistant's (`detection.tsv`:
noticed · stated side · side the probe found in the code). Fill **Owner** with `agree` or your
reading. A line about something else that happens to match the keywords is not a detection.
All 4 runs are included. Round 15's sheet: `../r15-zero2repo-case006-conflicts-v2/notes/detection_audit.md`.

## P1 — isolated filesystem: removed on exit (A) / always left in place (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 6. **`isolated_filesystem`.** PRD FP-14 says the directory is both removed (no parent given) and<br>"always left in place". Built: removed when `temp_dir` is None, left in place otherwise. | yes · A · A | |
| r16-sonnet-markdown-2 | \| `isolated_filesystem`: "removed on exit when no parent is given" vs "always left in place" \| PRD FP-14 \| Removed when `temp_dir` is `None`, kept when a parent is given. \| | yes · A · A | |
| r16-sonnet-export-1 | 5. **CF-000153 `isolated_filesystem`**: built "removed on exit when no `temp_dir` is given, left in place when<br>a parent `temp_dir` is supplied". | yes · A · A | |
| r16-sonnet-export-2 | 6. **CF-000153 isolated_filesystem cleanup** (N-000732 vs N-001015): built **removed on exit when no<br>`temp_dir` is given; left in place when a parent `temp_dir` is given**. | yes · A · A | |

## P2 — deprecated command's warning: stderr (A) / stdout (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 1. **Deprecation warning channel.** PRD FP-01 says standard output; Interface Contract section 2 | yes · A · A | |
| r16-sonnet-markdown-2 | \| Deprecation warning channel: PRD FP-01 says standard output, Contract §2 says standard error \| PRD FP-01 vs Contract "Channels" \| Standard error (Contract). Emitted before the callback runs. \|<br>\| Declaration errors (deprecated+required, deprecated+prompt, open-bound clamp, chain nesting, ...) \| PRD FP-03/04/05/10 \| `DeclarationError`, a subclass of `TypeError`, `ValueError` and `RuntimeError`. \| | yes · A · A | |
| r16-sonnet-export-1 | 1. **CF-000146 deprecation warning channel** (FP-01 says stdout, Contract channel table says stderr): | yes · A · A | |
| r16-sonnet-export-2 | 1. **CF-000146 deprecation warning channel** (N-000081 stdout vs N-000803 stderr): built **standard error** | yes · A · A | |

## P3 — environment beats default map (A) / default map beats environment (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | *(none)* | no · - · A | |
| r16-sonnet-markdown-2 | \| Default map vs environment precedence: Contract §6 says default-map values beat environment variables; PRD FP-03/FP-07 rank command line > environment > default map > declared default \| Contract §6 vs PRD FP-03 \| PRD order (environment beats default map). \| | yes · A · A | |
| r16-sonnet-export-1 | 2. **CF-000150 default map vs environment** (FP-03/FP-07 list env above default map; Contract section 6 says<br>default_map beats env): built **command line > environment > default map > declared default**, the | yes · A · A | |
| r16-sonnet-export-2 | 3. **CF-000150 env vs default map** (N-000230 env first vs N-000937 default map beats env): built<br>**command line > environment > default map > declared default** (FP-03 ordering). | yes · A · A | |

## P4 — callback for an omitted parameter: runs (A) / not called (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 4. **Callbacks for omitted parameters.** PRD Terminology says a parameter callback is not called when<br>nothing supplied a value; FP-03 says a missing parameter still runs its callback (so it can default<br>from earlier values). Built: the callback runs with `None`. | yes · A · A | |
| r16-sonnet-markdown-2 | \| Deprecation warning channel: PRD FP-01 says standard output, Contract §2 says standard error \| PRD FP-01 vs Contract "Channels" \| Standard error (Contract). Emitted before the callback runs. \|<br>\| Parameter callback on an omitted parameter: PRD glossary says it is not called; FP-03 says a missing parameter still runs its callback (to default from earlier values) \| PRD Terminology vs FP-03 \| The callback runs with `None` (FP-03). \|<br>\| Chaining group with standalone mode off: PRD says it returns the list of child return values whether or not a result callback is registered \| PRD FP-10 \| `main()` returns that list; the result callback still runs. \| | yes · A · A | |
| r16-sonnet-export-1 | - A parameter callback runs even for an omitted parameter (FP-03), despite the Terminology wording. | yes · A · A | |
| r16-sonnet-export-2 | (the Interface Contract channel table), emitted before the callback runs.<br>- `main()` on a chaining group with standalone mode off returns the list of child return values even when a result callback exists (result callback is still called). | no · - · A | |

## P6 — max content width: 80 (A) / 100 (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 3. **Maximum content width.** PRD FP-02 says 80 columns, FP-11 says 100. Built: 80 for help pages and | yes · A · A | |
| r16-sonnet-markdown-2 | \| Maximum content width default: FP-02 says 80, FP-11 says 100 \| PRD \| 80. An explicit `terminal_width` is used as-is; auto-detected width is `min(terminal, max_content_width) - 2` (at least 50). \| | yes · A · A | |
| r16-sonnet-export-1 | 6. **CF-000155 max content width** (80 vs 100): built **80**. Inside `CliRunner.invoke` the wrap width is fixed<br>at 80 so help output is deterministic. | yes · A · A | |
| r16-sonnet-export-2 | 2. **CF-000155 max content width** (N-000127 80 vs N-001014 100): built **80**. Explicit<br>`terminal_width` is used as-is; the runner pins the width to 80 as well.<br>- The unsettled alternatives rejected above (N-000081, N-000127/N-001014 (100), N-000937, N-001016, N-001013, N-001015): **not done** on purpose. | yes · A · A | |

## P7 — integer option metavar: INTEGER (A) / COUNT (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 5. **Default metavar example.** PRD FP-02 says the default metavar is the type name upper-cased but<br>gives `--count COUNT` as the example for an int option. Built: the rule (`--count INTEGER`).<br>options are listed short-name first (`-c, --count INTEGER`). | yes · A · A | |
| r16-sonnet-markdown-2 | \| Default metavar of a valued option: "type name in uppercase" vs example `--count COUNT` for an integer option \| PRD FP-02 \| Type name upper-cased (`--count INTEGER`); a custom `ParamType` shows its own `name`. \| | yes · A · A | |
| r16-sonnet-export-1 | 4. **CF-000152 default metavar** (type name uppercased vs the example `--count COUNT`): built the type name<br>uppercased, so an int option shows `--count INTEGER`; choice types show `[a\|b]`. | yes · A · A | |
| r16-sonnet-export-2 | 5. **CF-000152 metavar of an int option** (N-000326 type name `INTEGER` vs N-001013 `--count COUNT`): built<br>**type name upper-cased** (`--count INTEGER`); an author `metavar` replaces it. | yes · A · A | |

## R1 — confirm, other answer: asks again (A) / counts as no (B)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r16-sonnet-markdown-1 | 2. **`confirm` with an unrecognised answer.** Contract section 7 says it counts as no; PRD FP-08 says | yes · A · A | |
| r16-sonnet-markdown-2 | \| `confirm` with an unrecognised answer: PRD FP-08 says ask again, Contract §7 says it counts as no \| PRD vs Contract \| Ask again; if input then runs out, the result is `False` instead of an abort. EOF with no earlier invalid answer aborts. \| | yes · A · A | |
| r16-sonnet-export-1 | 3. **CF-000151 standalone `confirm` with an unrecognised answer** (FP-08 "asks again"; Contract "counts as no"): | yes · A · A | |
| r16-sonnet-export-2 | 4. **CF-000151 standalone confirm with other answer** (N-000495 asks again vs N-001016 counts as no): built **asks again** | yes · A · A | |


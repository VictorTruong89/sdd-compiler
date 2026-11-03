# Answer key: 24 conflicts planted in case006, round 17 (never shown to an agent)

> Written 2026-10-30, after the step-0 checks and before the compile and any agent run. The planted
> Markdown is made by `notes/plant.py work/spec-planted C01 … C29` (the 24 kept ids) from Zero2Repo
> case006's `public/`; it stays in git-ignored `work/` (Zero2Repo has no licence file), 14 435 words
> (14 138 before), hashes in `work/spec-planted.sha256`. Only short phrases are quoted here.

Side **A** is the text the case already had: click's behaviour and what the hidden tests check. Side
**B** is the planted sentence: one place edited, in the spec's voice, no marker. Lines are those of
the planted files (PRD = `Full_PRD.md`, Contract = `Interface_Contract.md`). C01–C05 are round 14's
P1, P3, P4, P6, P7 with the same edits; C29 was reserve R4.

| Item | Distance | A (kept) | B (planted) | Footprint (hidden tests A→B) | Past fails |
|---|---|---|---|---|---|
| C01 | same bullet | PRD 403: runner "removes that directory on exit" | PRD 403: "always left in place after the block ends" | `F14 isolated_filesystem_new_empty_dir_removed_when_no_parent` | 10 |
| C02 | across files | PRD 143: command line, "then environment, then the default map" | Contract 234: default-map values "take precedence over environment variables" | `F03 feature_switch_more_explicit_source_wins`, `F03 fill_order_command_line_env_map_declared`, `F07 default_map_string_splits_like_environment` | 17, 5, 7 |
| C03 | far, same file | PRD 145: "A missing parameter still runs its callback" | PRD 28 (Terminology): callback "not called for a parameter that was omitted" | `F03 missing_parameter_still_runs_its_callback` | 6 |
| C04 | far, same file | PRD 107: max content width "defaults to 80 columns" | PRD 340: "maximum content width of 100 columns" | `F02 help_rewrapped_to_width_capped_at_default_80` | 5 |
| C05 | same bullet | PRD 108: option metavar "is the type name in uppercase" | PRD 108: example `--count COUNT` | `F02 value_option_metavar_is_type_name_not_parameter_name` | 6 |
| C06 | across files | PRD 102: form feed, "text after that character is omitted" | Contract 74: form feed "dropped and the text after it is kept" | `F02 form_feed_truncates_description_and_is_omitted` | 0 |
| C07 | across files | PRD 137: counting option "(zero if omitted)" | Contract 177: "or `None` when the option was omitted" | `F03 counting_option_zero_when_omitted_stacked_shorts_count`, `F03 omitted_optional_without_default_is_absent` | 0, 0 |
| C08 | far, same file | PRD 138: omitted repeatable "receives an empty tuple" (also Contract 174) | PRD 84: omitted repeatable "is passed as an absent value" | `F03 repeatable_omitted_no_default_is_empty_tuple` | 0 |
| C09 | across files | PRD 141: env name list "(first one set wins)" (also PRD 169) | Contract 137: "the last name that is set wins" | `F03 option_env_list_first_set_wins`, `F04 env_name_list_first_set_wins` | 0, 0 |
| C10 | far, same file | PRD 142: other flag env value "is a conversion usage error" | PRD 192: "any other value turns the flag off" | `F03 unknown_boolean_env_is_usage_error_not_silent_off` | 2 |
| C12 | across files | PRD 195: date-time formats, "the first success wins" | Contract 211: "the last matching format is used" | `F05 datetime_formats_tried_in_order_first_success_wins` | 0 |
| C13 | far, same file | PRD 195: author list "replaces the default list (it does not extend it)" | PRD 40: author list "is added to the default formats" | `F05 author_replaces_datetime_format_list` | 0 |
| C14 | across files | PRD 196: open-bound clamp, "the adjacent integer inside the range" | Contract 212: the value "becomes that bound’s value" | `F05 integer_open_bound_clamp_uses_nearest_included` | 2 |
| C15 | across files | PRD 197: float clamp "only allowed when both bounds are closed" (also PRD 208) | Contract 213: with an open bound the value "becomes the bound" | `F05 float_range_refuses_clamp_when_bound_open` | 0 |
| C17 | far, same file | PRD 272: confirmation "rejects a mismatch by asking the pair again" | PRD 381: two different values in a confirmation prompt are an abort | `F08 confirmation_prompt_asks_twice_and_reasks_on_mismatch`, `F08 password_option_accepts_matching_hidden_lines` | 6, 4 |
| C18 | far, same file | PRD 274: "Prompts re-ask on conversion failure" | PRD 380: a prompt value failing conversion is a usage error, "not asked again" | `F08 option_prompt_eof_after_invalid_is_abort_not_usage`, `F08 option_prompt_reasks_on_conversion_failure`, `F08 standalone_prompt_reasks_until_valid_or_eof` | 6, 6, 0 |
| C20 | across files | PRD 292: resolved path, "a leading tilde is not expanded" | Contract 216: "a leading `~` is first expanded" | `F09 path_resolve_absolute_follows_symlinks_without_expanding_tilde` | 0 |
| C21 | across files | PRD 339: Unix config home is `$XDG_CONFIG_HOME` when set | Contract 292: "always under `~/.config`" | `F11 app_dir_unix_default_xdg_override_and_posix_forced` | 0 |
| C22 | far, same file | PRD 335: pause, not interactive, "does nothing" | PRD 346: "it still prints its message there" | `F11 pause_does_nothing_when_not_interactive` | 0 |
| C23 | across files | PRD 358: "Options are listed only once at least a dash has been typed" | Contract 306: an empty token lists "the subcommand names followed by the option names" | `F12 options_listed_only_after_a_dash` | 1 |
| C25 | across files | PRD 110: off-flag default "remains hidden even if show-default is on" | Contract 150: shown for every option, "a flag whose default is `False` included" | `F02 off_boolean_flag_default_stays_hidden` | 0 |
| C26 | across files | PRD 104: short help "is the first sentence of the docstring" | Contract 55: "the start of the child’s first paragraph, cut … at 45 characters" | `F02 subcommand_short_help_is_first_sentence` | 1 |
| C27 | across files | PRD 105: "The epilog is printed at the end of the help page" (also Contract 49–56) | Contract 74: epilog "printed right after the description, before the options" | `F02 group_help_lists_children_options_and_epilog_at_end` | 1 |
| C29 | across files | PRD 194: choice "Matching is case-sensitive unless the author turns that off" (also the Contract 210 signature) | Contract 210: "by default the match ignores letter case" | `F07 lowercase_normalizer_matches_choice_value` | 10 |

**Footprint union: 31 tests, none shared by two items.** The **core** (set 1) is the other **445**
tests. The base build fails 3 tests, none in the union (`notes/footprint.json`, `BASE_failed`).
Distances: same bullet 2 (C01, C05); far in one file 8; across files 14.

**Past fails** = how many of the 36 earlier case006 runs scored on all 476 tests failed that test
(rounds 13b–16, every `runs/*/reward_detail.json`; counted 2026-10-30). For C01–C05 these runs
include builds that took side B on purpose (rulings in round 14, choices in rounds 14–16), so the
count overstates how hard the test is. Weakest new item: **C29** (10 of 36): a miss on C29 and a
failure to build choice matching may be hard to tell apart; read its side from the probe.

## Candidates tried and dropped (step 0, no model call)

| Item | Behaviour | Why dropped |
|---|---|---|
| C11 | empty environment value delivers `""` | footprint 6 |
| C16 | empty answer to a prompt with a default asks again | footprint 4 |
| C19 | write-mode file opened at conversion | footprint 6 |
| C24 | clean stop with no status exits 1 | footprint 394 (the patch changed the library's own success path) |
| C28 | single newlines kept in help | shares `F02 help_rewrapped_to_width_capped_at_default_80` with C04; also turned C04's probe to "neither" |
| R3 | confirm, empty answer is no | footprint 0 |
| P2, R1 (round 14) | deprecation stream; confirm, other answer | footprint 0 (no hidden test covers them) |

## How each side is read (`notes/probe.py`, black box, from this key and the Contract only)

C01–C05: round 14's probes P1, P3, P4, P6, P7 (`../r14-zero2repo-case006-conflicts/ANSWER_KEY.md`).

| Item | Probe | A | B |
|---|---|---|---|
| C06 | `--help` of a command with help `"Before part.\fAfter part."` | only "Before part" | both parts |
| C07 | omitted `count=True` option | `0` | `None` |
| C08 | omitted `multiple=True` option | `()` | `None` |
| C09 | `envvar=[first, second]`, both set | first | second |
| C10 | flag with `envvar`, value `maybe` | exit 2 | `False` |
| C12 | `DateTime(["%Y-%m-%d", "%Y-%d-%m"])` on `2020-01-02` | month 1 | month 2 |
| C13 | `DateTime(["%d/%m/%Y"])` on `2020-01-02` | exit 2 | parsed |
| C14 | `IntRange(0, 10, max_open=True, clamp=True)` on 15 | 9 | 10 |
| C15 | `FloatRange(0, 1, max_open=True, clamp=True)` | refused | built, clamps to 1.0 |
| C17 | `prompt(confirmation_prompt=True)`, input `aa bb cc cc` | `cc` | abort |
| C18 | `prompt(type=INT)`, input `abc 5` | `5` | an exception |
| C20 | `Path(resolve_path=True)` on `~/x` | `<cwd>/~/x` | `$HOME/x` |
| C21 | `get_app_dir("Foo Bar")` with `XDG_CONFIG_HOME` set | `$XDG_CONFIG_HOME/foo-bar` | `~/.config/foo-bar` |
| C22 | `pause()` without a terminal | prints nothing | prints a message |
| C23 | `bash_complete` with an empty token on a group with an option | no option | option listed |
| C25 | `--help` of `is_flag=True, show_default=True` | no default shown | default shown |
| C26 | group help, child docstring `"Do it. Then more."` | `Do it.` | `Do it. Then more.` |
| C27 | `--help` with an epilog and one option | epilog after the option | epilog before it |
| C29 | `Choice(["Red"])` on `red` | exit 2 | `Red` |

Check passed 2026-10-30: the base reads A on all items; every side-B copy reads B on its own item
and A on every other kept item (`work/probe_check.log`).

## Exposure phrases

One phrase per side and item, each occurring exactly once in the planted Markdown (`PHRASES` in
`notes/plant.py`; checked by the script). A transcript "saw" a side when a tool result contains it.

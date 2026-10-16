# Markdown vs export: failed tests per case and model

Built by `notes/compare.py` from `runs/*/reward.json` and `reward_detail.json`.

## case006, haiku

| Run | Passed | Official |
|---|---|---|
| haiku-case006-export-1 | 425 / 476 | 0.0 |
| haiku-case006-export-2 | 467 / 476 | 0.0 |
| haiku-case006-markdown-1 | 452 / 476 | 0.0 |
| haiku-case006-markdown-2 | 0 / 0 | 0.0 | tests did not load; left out of the sets below
| (13b sweep, Markdown) | 464 / 476 | 0.0 |

**Failed in every Markdown run, in no export run** (12):
- `F09` test_atomic_write_keeps_original_until_close_then_replaces
- `F09` test_copy_dash_to_file_then_file_to_dash
- `F09` test_default_write_does_not_truncate_until_used
- `F03` test_feature_switch_more_explicit_source_wins
- `F09` test_lazy_forced_on_write_does_not_truncate_until_used
- `F03` test_nonboolean_flag_value_env_exact_or_bool_tokens
- `F02` test_parameter_named_help_does_not_disable_automatic_help
- `F08` test_required_prompt_asks_on_omit_and_on_bare_flag
- `F09` test_text_and_binary_modes
- `F01` test_trailing_command_suffix_stripped_from_invoked_name[_group]
- `F01` test_trailing_command_suffix_stripped_from_invoked_name[_grp]
- `F05` test_uuid_type_converts_text_and_is_never_inferred

**Failed in every export run, in no Markdown run** (3):
- `F12` test_bash_and_powershell_suggest_value_without_requiring_help
- `F02` test_long_short_help_ellipsized_to_one_line
- `F12` test_zsh_and_fish_include_author_help_next_to_value

**Failed in every run, both formats** (3):
- `F12` test_custom_type_completion_unlike_string_sibling
- `F03` test_on_off_pair_tokens
- `F11` test_pager_keeps_styles_when_destination_supports_styles

**Failed in some runs only** (63):
- `F09` test_atomic_write_keeps_original_until_close_then_replaces
- `F02` test_backspace_paragraph_keeps_breaks_and_strips_marker
- `F12` test_bash_and_powershell_suggest_value_without_requiring_help
- `F05` test_boolean_value_type_tokens_case_insensitive
- `F08` test_callable_default_still_prompts_and_is_invoked
- `F10` test_chained_child_file_closes_after_callback_group_file_stays_for_result_callback
- `F10` test_chaining_current_subcommand_name_is_neither_one_child_nor_absent
- `F10` test_chaining_options_bind_per_command_before_that_commands_arguments
- `F05` test_choice_must_be_unique_after_normalization
- `F07` test_command_line_source_does_not_consume_prompt_stdin
- `F08` test_command_line_value_skips_prompt
- `F08` test_confirmation_prompt_asks_twice_and_reasks_on_mismatch
- `F10` test_consume_rest_on_non_last_child_is_declared_and_eats_later_names
- `F09` test_copy_dash_to_file_then_file_to_dash
- `F08` test_custom_prompt_string_replaces_name_derived_prompt
- `F09` test_declared_text_encoding_is_used
- `F07` test_default_map_string_splits_like_environment
- `F08` test_default_map_value_still_prompts
- `F09` test_default_write_does_not_truncate_until_used
- `F08` test_deprecated_plus_prompt_declaration_is_refused
- `F12` test_directories_only_path_asks_shell_for_directories_only
- `F08` test_empty_line_answer_uses_shown_default
- `F08` test_environment_value_skips_prompt_even_on_eof
- `F03` test_feature_switch_more_explicit_source_wins
- `F11` test_getchar_interrupt_and_eof_are_distinct_failures_not_raw_characters
- `F11` test_getchar_reads_terminal_even_when_stdin_is_a_pipe
- `F03` test_group_mixing_can_be_enabled
- `F08` test_hidden_input_not_echoed_visible_prompt_is
- `F14` test_hidden_prompt_does_not_echo_typed_line
- `F05` test_integer_open_bound_clamp_uses_nearest_included
- `F09` test_lazy_forced_on_write_does_not_truncate_until_used
- `F02` test_long_short_help_ellipsized_to_one_line
- `F07` test_lowercase_normalizer_matches_choice_value
- `F03` test_missing_value_for_required_value_option_is_usage_error
- `F03` test_multi_value_fixed_arity_not_consume_rest
- `F11` test_named_background_colors_each_wrap_unlike_foreground
- `F04` test_non_unary_env_splits_like_multivalue_option
- `F03` test_nonboolean_flag_value_env_exact_or_bool_tokens
- `F08` test_omitted_prompted_option_reads_converted_stdin
- `F04` test_omitted_variadic_empty_unless_required
- `F13` test_option_missing_value_is_usage_class_skips_callback
- `F08` test_option_prompt_eof_after_invalid_is_abort_not_usage
- `F08` test_option_prompt_reasks_on_conversion_failure
- `F03` test_optional_value_flag_alone_token_or_default
- `F11` test_pager_strips_styles_when_destination_is_not_a_terminal
- `F03` test_parameter_callback_runs_for_prompt_source
- `F12` test_parameter_completer_sees_context_parameter_and_incomplete_token
- `F02` test_parameter_named_help_does_not_disable_automatic_help
- `F11` test_pause_prints_and_waits_when_interactive
- `F08` test_required_prompt_asks_on_omit_and_on_bare_flag
- `F02` test_single_newlines_in_paragraph_are_not_hard_breaks
- `F07` test_source_distinguishes_five_origins_for_the_same_value
- `F08` test_standalone_confirm_strips_ansi_when_stream_is_not_a_terminal
- `F08` test_standalone_prompt_strips_ansi_when_stream_is_not_a_terminal
- `F08` test_static_declared_default_still_prompts
- `F09` test_text_and_binary_modes
- `F01` test_trailing_command_suffix_stripped_from_invoked_name[_group]
- `F01` test_trailing_command_suffix_stripped_from_invoked_name[_grp]
- `F04` test_two_variadics_are_not_independent_consume_rest
- `F07` test_undeclared_extra_key_is_not_converted_or_tracked
- `F05` test_uuid_type_converts_text_and_is_never_inferred
- `F14` test_visible_prompt_echoes_typed_line_and_shows_prompt
- `F12` test_zsh_and_fish_include_author_help_next_to_value

## case006, sonnet

| Run | Passed | Official |
|---|---|---|
| sonnet-case006-export-1 | 473 / 476 | 0.0 |
| sonnet-case006-export-2 | 470 / 476 | 0.0 |
| sonnet-case006-markdown-1 | 470 / 476 | 0.0 |
| sonnet-case006-markdown-2 | 469 / 476 | 0.0 |

**Failed in every Markdown run, in no export run** (0)

**Failed in every export run, in no Markdown run** (0)

**Failed in every run, both formats** (1):
- `F03` test_feature_switch_last_declared_wins_when_tied

**Failed in some runs only** (9):
- `F03` test_bare_string_default_on_repeatable_is_usage_error
- `F09` test_copy_dash_to_file_then_file_to_dash
- `F02` test_first_eager_flag_on_command_line_wins
- `F03` test_nonboolean_flag_value_env_exact_or_bool_tokens
- `F09` test_open_helper_keeps_stdio_open_and_closes_real_files
- `F14` test_optional_mode_echoes_every_stdin_read_not_only_prompts
- `F11` test_pager_keeps_styles_when_destination_supports_styles
- `F02` test_parameter_named_help_does_not_disable_automatic_help
- `F09` test_text_and_binary_modes

## case010, haiku

| Run | Passed | Official |
|---|---|---|
| haiku-case010-export-1 | 168 / 197 | 0.0 |
| haiku-case010-export-2 | 166 / 197 | 0.0 |
| haiku-case010-markdown-1 | 162 / 197 | 0.0 |
| haiku-case010-markdown-2 | 169 / 197 | 0.0 |
| (13b sweep, Markdown) | 166 / 197 | 0.0 |

**Failed in every Markdown run, in no export run** (0)

**Failed in every export run, in no Markdown run** (0)

**Failed in every run, both formats** (26):
- `F01` test_cli_one_output_line_per_nonempty_input_line
- `F01` test_cli_tokenize_hello_world_joined_by_spaces
- `F03` test_empty_token_list_tags_as_empty_on_recommended_english
- `F03` test_english_universal_mapping_absent_without_tables_ptb_still_works
- `F02` test_lancaster_named_pairs
- `F04` test_named_entity_fails_without_ne_resource_when_perceptron_present
- `F03` test_recommended_english_fails_when_only_russian_perceptron_installed
- `F03` test_recommended_english_homepage_proper_vs_common_noun
- `F03` test_recommended_english_john_list_ptb_category_structure
- `F03` test_recommended_korean_does_not_succeed_english_does
- `F03` test_recommended_refuses_raw_john_string_token_list_succeeds
- `F03` test_recommended_refuses_runtime_raw_string_token_list_succeeds
- `F03` test_recommended_runtime_unsupported_language_does_not_succeed
- `F03` test_recommended_russian_fails_when_only_english_perceptron_installed
- `F03` test_recommended_russian_rnc_named_s_v_and_category_contrasts
- `F03` test_recommended_russian_universal_maps_noun_and_verb
- `F01` test_recommended_sentence_tokenizer_same_atoms_other_order
- `F01` test_recommended_sentence_tokenizer_single_atom_is_one_sentence
- `F01` test_recommended_sentence_tokenizer_three_muffin_sentences
- `F01` test_recommended_word_with_sentence_split_three_points_no_glue
- `F03` test_russian_universal_succeeds_without_universal_tables_english_does_not
- `F02` test_snowball_arabic_named_pairs
- `F02` test_snowball_german_schranke_and_skip_off_keinen_without_wordlist
- `F02` test_snowball_russian_named_pair
- `F02` test_snowball_spanish_visionado
- `F02` test_snowball_ten_languages_named_pairs

**Failed in some runs only** (13):
- `F06` test_accuracy_classifier_length_four_is_half
- `F06` test_accuracy_classifier_pos_pos_neg_against_pos_neg_neg_is_two_thirds
- `F06` test_accuracy_classifier_same_bag_permutation_is_one_third
- `F02` test_arlstem_and_arlstem2_construct_and_stem_noun_to_str
- `F02` test_arlstem_and_arlstem2_construct_and_stem_verb_to_str
- `F06` test_decision_tree_full_training_featuresets_positive_and_negative
- `F06` test_decision_tree_runtime_full_featuresets_follow_training_labels
- `F06` test_naive_bayes_nice_only_positive_bad_only_negative_with_ranked_probs
- `F06` test_naive_bayes_runtime_features_and_labels_rank_and_swap
- `F06` test_naive_bayes_unseen_feature_does_not_flip_or_zero_all_probs
- `F02` test_snowball_german_skip_on_does_not_construct_without_wordlist
- `F02` test_snowball_german_skip_on_leaves_keinen_when_wordlist_present
- `F02` test_snowball_listed_language_without_named_stem_is_usable

## case010, sonnet

| Run | Passed | Official |
|---|---|---|
| sonnet-case010-export-1 | 176 / 197 | 0.0 |
| sonnet-case010-export-2 | 175 / 197 | 0.0 |
| sonnet-case010-markdown-1 | 175 / 197 | 0.0 |
| sonnet-case010-markdown-2 | 176 / 197 | 0.0 |

**Failed in every Markdown run, in no export run** (0)

**Failed in every export run, in no Markdown run** (0)

**Failed in every run, both formats** (20):
- `F01` test_cli_one_output_line_per_nonempty_input_line
- `F01` test_cli_tokenize_hello_world_joined_by_spaces
- `F03` test_empty_token_list_tags_as_empty_on_recommended_english
- `F03` test_english_universal_mapping_absent_without_tables_ptb_still_works
- `F04` test_named_entity_fails_without_ne_resource_when_perceptron_present
- `F03` test_recommended_english_fails_when_only_russian_perceptron_installed
- `F03` test_recommended_english_homepage_proper_vs_common_noun
- `F03` test_recommended_english_john_list_ptb_category_structure
- `F03` test_recommended_korean_does_not_succeed_english_does
- `F03` test_recommended_refuses_raw_john_string_token_list_succeeds
- `F03` test_recommended_refuses_runtime_raw_string_token_list_succeeds
- `F03` test_recommended_runtime_unsupported_language_does_not_succeed
- `F03` test_recommended_russian_fails_when_only_english_perceptron_installed
- `F03` test_recommended_russian_rnc_named_s_v_and_category_contrasts
- `F03` test_recommended_russian_universal_maps_noun_and_verb
- `F01` test_recommended_sentence_tokenizer_same_atoms_other_order
- `F01` test_recommended_sentence_tokenizer_single_atom_is_one_sentence
- `F01` test_recommended_sentence_tokenizer_three_muffin_sentences
- `F01` test_recommended_word_with_sentence_split_three_points_no_glue
- `F03` test_russian_universal_succeeds_without_universal_tables_english_does_not

**Failed in some runs only** (2):
- `F02` test_snowball_arabic_named_pairs
- `F02` test_snowball_ten_languages_named_pairs

## case016, haiku

| Run | Passed | Official |
|---|---|---|
| haiku-case016-export-1 | 364 / 388 | 0.0 |
| haiku-case016-export-2 | 379 / 388 | 0.0 |
| haiku-case016-markdown-1 | 381 / 388 | 0.0 |
| haiku-case016-markdown-2 | 378 / 388 | 0.0 |
| (13b sweep, Markdown) | 370 / 388 | 0.0 |

**Failed in every Markdown run, in no export run** (1):
- `F06` test_check_not_a_file_unreadable_and_pdf_rtf_differ

**Failed in every export run, in no Markdown run** (3):
- `F01` test_constructable_fires_match_named_probes[synonym-companies]
- `F06` test_help_names_the_threshold_integers_and_the_export_path[named]
- `F06` test_help_names_the_threshold_integers_and_the_export_path[plain]

**Failed in every run, both formats** (2):
- `F05` test_five_failure_reasons_stay_distinguishable
- `F03` test_tag_payload_after_flag_terminator_is_removed_flag_stays

**Failed in some runs only** (36):
- `F01` test_band_matches_documented_range_on_named_oracles
- `F01` test_banned_word_split_only_by_zero_width_still_fires
- `F01` test_character_layer_findings_ignore_bytes_past_the_window
- `F06` test_check_names_the_file_only_for_no_output_and_stated_failure
- `F06` test_check_names_the_window_only_when_truncated[named]
- `F06` test_check_names_the_window_only_when_truncated[plain]
- `F06` test_check_not_a_file_unreadable_and_pdf_rtf_differ
- `F06` test_check_over_cap_names_kilobytes_and_no_score
- `F02` test_check_scores_at_plain_text_cap_and_refuses_one_byte_over
- `F01` test_constructable_fires_match_named_probes[adj-stack]
- `F01` test_constructable_fires_match_named_probes[article-title]
- `F01` test_constructable_fires_match_named_probes[synonym-companies]
- `F01` test_constructable_non_fires_stay_quiet_with_live_baselines[noun-list]
- `F05` test_detector_budgets_are_8s_plain_and_15s_archive
- `F02` test_detector_still_reads_a_path_over_the_plugin_plain_text_cap
- `F05` test_empty_result_shares_its_reason_with_unreadable
- `F02` test_guard_over_cap_write_exits_without_scoring_nudge
- `F06` test_help_names_the_threshold_integers_and_the_export_path[named]
- `F06` test_help_names_the_threshold_integers_and_the_export_path[plain]
- `F04` test_init_export_omits_detector_path_and_user_name
- `F06` test_init_exports_a_portable_contract_and_a_prose_rule
- `F06` test_init_lite_omits_detector_resolution
- `F03` test_interior_tab_lf_cr_are_not_stripped_as_invisible
- `F01` test_latin_run_homoglyph_fires_66_and_the_ascii_vocabulary_finding
- `F01` test_leftover_decisive_pairs_raise_score_to_at_least_65
- `F03` test_long_unspaced_token_finishes_within_8_seconds_with_and_without_cleanup
- `F05` test_missing_score_is_not_any_integer
- `F01` test_named_line_126_oracles_are_not_a_constant_fifty
- `F02` test_opendocument_preserves_linked_text_and_explicit_whitespace[write_odp-.odp]
- `F02` test_opendocument_preserves_linked_text_and_explicit_whitespace[write_ods-.ods]
- `F02` test_opendocument_preserves_linked_text_and_explicit_whitespace[write_odt-.odt]
- `F01` test_placeholder_plus_tracking_parameter_scores_at_least_65
- `F01` test_second_banned_word_split_only_by_zero_width_still_fires
- `F06` test_show_names_the_window_only_when_truncated
- `F01` test_single_decisive_at_low_or_none_does_not_take_45
- `F01` test_two_decisive_families_raise_score_to_at_least_65

## case016, sonnet

| Run | Passed | Official |
|---|---|---|
| sonnet-case016-export-1 | 387 / 388 | 0.0 |
| sonnet-case016-export-2 | 388 / 388 | 1.0 |
| sonnet-case016-markdown-1 | 385 / 388 | 0.0 |
| sonnet-case016-markdown-2 | 387 / 388 | 0.0 |

**Failed in every Markdown run, in no export run** (0)

**Failed in every export run, in no Markdown run** (0)

**Failed in every run, both formats** (0)

**Failed in some runs only** (5):
- `F02` test_guard_over_cap_write_exits_without_scoring_nudge
- `F05` test_instruction_stems_without_prose_extension_are_absent
- `F03` test_kept_characters_are_not_invisible_or_stray_space_on_the_original_scan
- `F03` test_named_keep_sequences_are_byte_for_byte
- `F03` test_tag_payload_after_flag_terminator_is_removed_flag_stays


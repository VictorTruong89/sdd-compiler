"""F1 CT-1.4 — the profile contract, and the exit codes it raises.

Tier: contract (constitution §4).
"""
from __future__ import annotations

import pytest

from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.profile import DEFAULT_PROFILE, Profile, load_profile, render_default_profile


def write(tmp_path, text: str):
    sdd = tmp_path / ".sdd"
    sdd.mkdir(exist_ok=True)
    (sdd / "profile.yaml").write_text(text, encoding="utf-8")
    return tmp_path


def test_ct_1_4_defaults_match_the_spec():
    """CT-1.4 names four keys with these defaults."""
    assert DEFAULT_PROFILE["spec_globs"] == ["sdd/specs/**/*.md"]
    assert DEFAULT_PROFILE["exclude_globs"] == ["sdd/specs/_templates/**"]
    assert DEFAULT_PROFILE["include_code_blocks"] is False
    assert DEFAULT_PROFILE["atomizer"]["backend"] == "claude-code"
    assert DEFAULT_PROFILE["atomizer"]["model"] == "haiku"
    assert DEFAULT_PROFILE["atomizer"]["pass_api_key"] is False


def test_ct_1_4_rendered_default_round_trips(tmp_path):
    """What `sddc init` writes must load back as the defaults, comments and all."""
    root = write(tmp_path, render_default_profile())
    profile = load_profile(root)
    assert list(profile.spec_globs) == DEFAULT_PROFILE["spec_globs"]
    assert list(profile.exclude_globs) == DEFAULT_PROFILE["exclude_globs"]
    assert profile.include_code_blocks is False
    assert profile.atomizer.backend == "claude-code"
    assert profile.atomizer.model == "haiku"


def test_ct_1_4_partial_profile_fills_defaults(tmp_path):
    root = write(tmp_path, 'spec_globs: ["docs/**/*.md"]\n')
    profile = load_profile(root)
    assert list(profile.spec_globs) == ["docs/**/*.md"]
    assert list(profile.exclude_globs) == DEFAULT_PROFILE["exclude_globs"]
    assert profile.atomizer.model == "haiku"


def test_ac_1_24_missing_store_is_a_store_error(tmp_path):
    """AC-1.24 — any command except init, with no .sdd/, exits 4 naming `sddc init`."""
    with pytest.raises(SddcError) as excinfo:
        load_profile(tmp_path)
    assert excinfo.value.exit_code is ExitCode.STORE
    assert "sddc init" in str(excinfo.value)


@pytest.mark.parametrize(
    "text, fragment",
    [
        ("spec_globs: 3\n", "spec_globs"),
        ("spec_globs: []\n", "spec_globs"),
        ("include_code_blocks: maybe\n", "include_code_blocks"),
        ("atomizer: {backend: telepathy, model: haiku}\n", "backend"),
        ("unknown_key: 1\n", "unknown_key"),
        ("spec_globs: [\n", "profile.yaml"),
    ],
)
def test_ct_1_4_invalid_profile_is_rejected_by_name(tmp_path, text, fragment):
    """Fail loud: every rejection names the offending field or file."""
    root = write(tmp_path, text)
    with pytest.raises(SddcError) as excinfo:
        load_profile(root)
    assert excinfo.value.exit_code is ExitCode.INPUT
    assert fragment in str(excinfo.value)


def test_profile_is_frozen(tmp_path):
    root = write(tmp_path, render_default_profile())
    profile = load_profile(root)
    assert isinstance(profile, Profile)
    with pytest.raises(Exception):
        profile.spec_globs = ["x"]  # type: ignore[misc]


def test_ct_3_4_atomizer_settings_and_weak_words_load(tmp_path):
    """F3 CT-3.4 — the atomizer settings and the weak-word lexicon."""
    root = write(tmp_path, render_default_profile())
    profile = load_profile(root)
    assert profile.atomizer.pass_api_key is False
    assert profile.atomizer.max_calls_per_run == 200
    assert profile.atomizer.timeout_s == 120
    assert profile.atomizer.thinking is False
    assert "user-friendly" in profile.weak_words


def test_ct_3_4_weak_words_are_lower_cased(tmp_path):
    root = write(tmp_path, "weak_words: [Fast, APPROPRIATE]\n")
    assert load_profile(root).weak_words == ("fast", "appropriate")


@pytest.mark.parametrize(
    "text, fragment",
    [
        ("atomizer: {max_calls_per_run: 0}\n", "max_calls_per_run"),
        ("atomizer: {timeout_s: -1}\n", "timeout_s"),
        ("atomizer: {pass_api_key: yes-please}\n", "pass_api_key"),
        ("atomizer: {thinking: sometimes}\n", "thinking"),
        ("weak_words: 3\n", "weak_words"),
    ],
)
def test_ct_3_4_invalid_atomizer_settings_are_rejected(tmp_path, text, fragment):
    root = write(tmp_path, text)
    with pytest.raises(SddcError) as excinfo:
        load_profile(root)
    assert fragment in str(excinfo.value)


# -- F2 AC-2.22: layers are constants; only display names and hints load ------

def test_ac_2_22_display_names_and_hints_load(tmp_path):
    write(tmp_path, "layers:\n  L1: {display: Behaviour, hints: ['## Behaviour', '## Scenarios']}\n")
    profile = load_profile(tmp_path)
    assert profile.layers["L1"] == {"display": "Behaviour", "hints": ["## Behaviour", "## Scenarios"]}


@pytest.mark.parametrize(
    "body",
    [
        "layers:\n  L6: {display: Extra}\n",                    # adding a layer
        "layers:\n  L1: {meaning: Anything goes}\n",           # redefining a meaning
    ],
)
def test_ac_2_22_a_profile_cannot_add_or_redefine_a_layer(tmp_path, body):
    write(tmp_path, body)
    with pytest.raises(SddcError) as error:
        load_profile(tmp_path)
    assert "layer" in str(error.value)


def test_ac_1_32_skip_headings_defaults_to_the_traceability_section(tmp_path):
    assert DEFAULT_PROFILE["skip_headings"] == ["Traceability"]
    root = write(tmp_path, render_default_profile())
    assert load_profile(root).skip_headings == ("Traceability",)


def test_ac_1_32_skip_headings_may_be_empty(tmp_path):
    assert load_profile(write(tmp_path, "skip_headings: []\n")).skip_headings == ()


@pytest.mark.parametrize("text", ['skip_headings: "Traceability"\n', "skip_headings: [3]\n"])
def test_ac_1_32_skip_headings_must_be_a_list_of_strings(tmp_path, text):
    with pytest.raises(SddcError) as excinfo:
        load_profile(write(tmp_path, text))
    assert excinfo.value.exit_code is ExitCode.INPUT
    assert "skip_headings" in str(excinfo.value)


def test_ac_1_33_contract_languages_default_and_validation(tmp_path):
    assert DEFAULT_PROFILE["contract_languages"] == ["json", "yaml", "text"]
    assert load_profile(write(tmp_path, render_default_profile())).contract_languages == (
        "json", "yaml", "text")
    assert load_profile(write(tmp_path, "contract_languages: [JSON]\n")).contract_languages == ("json",)
    with pytest.raises(SddcError) as excinfo:
        load_profile(write(tmp_path, "contract_languages: json\n"))
    assert excinfo.value.exit_code is ExitCode.INPUT and "contract_languages" in str(excinfo.value)


def test_d16_rare_keyword_share_defaults_and_is_validated(tmp_path):
    """F5 D16, CT-5.2: a share of nodes, above 0 and at most 1."""
    assert load_profile(write(tmp_path, "")).retrieval.rare_keyword_share == 0.01
    assert load_profile(write(tmp_path, "retrieval: {rare_keyword_share: 0.05}\n")).retrieval.rare_keyword_share == 0.05
    for bad in ("0", "1.5", "yes"):
        with pytest.raises(SddcError) as excinfo:
            load_profile(write(tmp_path, f"retrieval: {{rare_keyword_share: {bad}}}\n"))
        assert "rare_keyword_share" in str(excinfo.value)

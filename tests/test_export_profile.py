"""F7 CT-7.2 — the `export` profile key (an F1 CT-1.4 addition); AC-7.8's "one key" half.

Tier: contract.
"""
from __future__ import annotations

import pytest

from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.profile import DEFAULT_PROFILE, load_profile, render_default_profile


def write(tmp_path, text):
    (tmp_path / ".sdd").mkdir(exist_ok=True)
    (tmp_path / ".sdd" / "profile.yaml").write_text(text, encoding="utf-8")
    return tmp_path


def test_ct_7_2_default_foundation_globs():
    assert DEFAULT_PROFILE["export"] == {"foundation_globs": ["**/vision.md", "**/constitution.md"]}


def test_ct_7_2_rendered_default_round_trips(tmp_path):
    profile = load_profile(write(tmp_path, render_default_profile()))
    assert list(profile.export.foundation_globs) == ["**/vision.md", "**/constitution.md"]


def test_ct_7_2_an_empty_list_means_no_foundation(tmp_path):
    profile = load_profile(write(tmp_path, "export:\n  foundation_globs: []\n"))
    assert profile.export.foundation_globs == ()


def test_ct_7_2_there_is_no_omit_key_of_its_own(tmp_path):
    """D11: omitted headings are F1's `skip_headings`; `omit_headings` is an unknown key."""
    with pytest.raises(SddcError, match="omit_headings") as excinfo:
        load_profile(write(tmp_path, 'export:\n  omit_headings: ["Traceability"]\n'))
    assert excinfo.value.exit_code is ExitCode.INPUT


@pytest.mark.parametrize("text", ["export: 3\n", "export:\n  foundation_globs: vision.md\n",
                                  "export:\n  foundation_globs: [1]\n"])
def test_ct_7_2_bad_types_are_input_errors(tmp_path, text):
    with pytest.raises(SddcError) as excinfo:
        load_profile(write(tmp_path, text))
    assert excinfo.value.exit_code is ExitCode.INPUT
    assert "export" in str(excinfo.value)

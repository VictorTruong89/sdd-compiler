"""F7 §4.2 step 2, D7 — the export refuses a graph older than its specs (AC-7.18).

Tier: contract.
"""
from __future__ import annotations

import pytest

from sdd_compiler.commands import init
from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.export.sources import check_sources
from sdd_compiler.ingest import pipeline
from sdd_compiler.profile import load_profile


@pytest.fixture()
def repo(tmp_path):
    for name in ("a", "b"):
        spec = tmp_path / "sdd" / "specs" / f"{name}.md"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(f"## {name}\n\nA {name} must work.\n", encoding="utf-8")
    init(tmp_path)
    pipeline.ingest(tmp_path)
    return tmp_path


def problems(repo):
    return check_sources(repo, load_profile(repo))


def test_a_current_graph_has_no_problem(repo):
    assert problems(repo) == []


def test_ac_7_18_an_edited_file_is_named_with_the_fix(repo):
    (repo / "sdd/specs/a.md").write_text("## a\n\nChanged.\n", encoding="utf-8")
    with pytest.raises(SddcError) as excinfo:
        check_sources(repo, load_profile(repo), raise_on_problem=True)
    assert excinfo.value.exit_code is ExitCode.INPUT
    assert "sdd/specs/a.md" in str(excinfo.value) and "run sddc compile first" in str(excinfo.value)
    assert "sdd/specs/b.md" not in str(excinfo.value)


def test_a_new_and_a_missing_file_are_named(repo):
    (repo / "sdd/specs/c.md").write_text("## c\n", encoding="utf-8")
    (repo / "sdd/specs/b.md").unlink()
    text = "\n".join(problems(repo))
    assert "new: sdd/specs/c.md" in text and "missing: sdd/specs/b.md" in text


def test_line_endings_are_read_as_ingest_reads_them(repo):
    (repo / "sdd/specs/a.md").write_bytes(b"## a\r\n\r\nA a must work.\r\n")
    assert problems(repo) == []          # ingest hashes universal-newline text

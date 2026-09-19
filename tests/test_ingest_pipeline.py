"""T5 — `init`, the ingest phase (`sddc ingest`, also the first phase of `compile`), and `status` (F1 AC-1.8, AC-1.21 … AC-1.26).

Tier: integration, with the CLI driven as a real process where exit codes matter.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

from sdd_compiler.errors import ExitCode
from sdd_compiler.store.jsonl import read_jsonl

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"

SPEC = """\
## Behaviour
First paragraph.

- item one
- item two
"""


def sddc(*args, cwd):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SRC), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    return subprocess.run(
        [sys.executable, "-m", "sdd_compiler", *args],
        capture_output=True, text=True, cwd=cwd, env=env,
    )


@pytest.fixture()
def repo(tmp_path):
    specs = tmp_path / "sdd" / "specs" / "F1_demo"
    specs.mkdir(parents=True)
    (specs / "spec.md").write_text(SPEC, encoding="utf-8")
    assert sddc("init", cwd=tmp_path).returncode == 0
    return tmp_path


# -- init -------------------------------------------------------------------

def test_init_creates_the_store_and_a_loadable_profile(tmp_path):
    result = sddc("init", cwd=tmp_path)
    assert result.returncode == 0
    assert (tmp_path / ".sdd" / "profile.yaml").exists()
    assert sddc("status", cwd=tmp_path).returncode == 0


def test_ac_1_25_init_does_not_overwrite(repo):
    (repo / ".sdd" / "profile.yaml").write_text("spec_globs: ['keep/**/*.md']\n", encoding="utf-8")
    result = sddc("init", cwd=repo)
    assert result.returncode != 0
    assert "keep/**/*.md" in (repo / ".sdd" / "profile.yaml").read_text(encoding="utf-8")


def test_ac_1_24_commands_need_a_store(tmp_path):
    for command in ("status", "compile", "ingest"):
        result = sddc(command, cwd=tmp_path)
        assert result.returncode == int(ExitCode.STORE)
        assert "sddc init" in result.stderr


# -- the ingest phase (`sddc ingest`; `compile` runs it first) ------------------

def test_ingest_writes_blocks_sources_and_a_run(repo):
    result = sddc("ingest", cwd=repo)
    assert result.returncode == 0, result.stderr

    blocks = read_jsonl(repo / ".sdd" / "blocks.jsonl")
    assert len(blocks) == 3
    assert all(block["atomized_hash"] is None and block["removed_run"] is None for block in blocks)
    assert {block["source"] for block in blocks} == {"sdd/specs/F1_demo/spec.md"}

    sources = read_jsonl(repo / ".sdd" / "sources.jsonl")
    assert sources[0]["path"] == "sdd/specs/F1_demo/spec.md"
    assert sources[0]["file_hash"].startswith("sha256:")

    runs = read_jsonl(repo / ".sdd" / "runs.jsonl")
    assert runs[0]["command"] == "ingest"
    assert runs[0]["counts"] == {"new": 3, "changed": 0, "unchanged": 0, "removed": 0}


def test_ac_1_8_re_ingesting_an_unchanged_file_reports_nothing(repo):
    """AC-1.8, first half: a second ingest of an unchanged file changes nothing."""
    sddc("ingest", cwd=repo)
    result = sddc("ingest", "--json", cwd=repo)
    counts = json.loads(result.stdout)["counts"]
    assert counts == {"new": 0, "changed": 0, "unchanged": 3, "removed": 0}


def test_ac_1_8_a_second_run_leaves_the_store_byte_identical(repo):
    """AC-1.8 as written — satisfiable since F1 D13 stopped storing the run's delta."""
    sddc("ingest", cwd=repo)
    blocks = (repo / ".sdd" / "blocks.jsonl").read_bytes()
    sources = (repo / ".sdd" / "sources.jsonl").read_bytes()

    sddc("ingest", cwd=repo)
    assert (repo / ".sdd" / "blocks.jsonl").read_bytes() == blocks
    assert (repo / ".sdd" / "sources.jsonl").read_bytes() == sources
    assert len(read_jsonl(repo / ".sdd" / "runs.jsonl")) == 2  # runs still accumulate


def test_an_edit_shows_up_as_one_changed_block(repo):
    sddc("ingest", cwd=repo)
    spec = repo / "sdd" / "specs" / "F1_demo" / "spec.md"
    spec.write_text(SPEC.replace("item one", "item ONE"), encoding="utf-8")

    result = sddc("ingest", "--json", cwd=repo)
    counts = json.loads(result.stdout)["counts"]
    assert counts == {"new": 0, "changed": 1, "unchanged": 2, "removed": 0}


def test_ingest_accepts_explicit_paths(repo):
    other = repo / "sdd" / "specs" / "F2_demo"
    other.mkdir(parents=True)
    (other / "spec.md").write_text("Only me.\n", encoding="utf-8")

    sddc("ingest", "sdd/specs/F2_demo/spec.md", cwd=repo)
    sources = read_jsonl(repo / ".sdd" / "sources.jsonl")
    assert [source["path"] for source in sources] == ["sdd/specs/F2_demo/spec.md"]


# -- status -----------------------------------------------------------------

def test_ac_1_21_status_json_matches_ct_1_5(repo):
    sddc("ingest", cwd=repo)
    result = sddc("status", "--json", cwd=repo)
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert set(payload) == {"run", "counts", "pending"}
    assert payload["counts"] == {"sources": 1, "blocks": 3, "pending": 3}
    first = payload["pending"][0]
    assert set(first) == {"id", "status", "source", "lines", "heading_path", "kind", "text"}
    assert first["heading_path"] == ["Behaviour"]
    assert first["status"] == "new"


def test_ac_1_31_status_still_lists_unatomized_blocks_after_a_second_run(repo):
    sddc("ingest", cwd=repo)
    sddc("ingest", cwd=repo)
    payload = json.loads(sddc("status", "--json", cwd=repo).stdout)
    assert payload["counts"]["pending"] == 3


def test_status_text_output_is_readable(repo):
    sddc("ingest", cwd=repo)
    result = sddc("status", cwd=repo)
    assert "3 blocks" in result.stdout
    assert "1 source" in result.stdout


# -- failures ---------------------------------------------------------------

def test_ac_1_22_a_bad_file_leaves_the_store_untouched(repo):
    sddc("ingest", cwd=repo)
    before = (repo / ".sdd" / "blocks.jsonl").read_bytes()

    bad = repo / "sdd" / "specs" / "F1_demo" / "broken.md"
    bad.write_bytes(b"# valid start\n\n\xff\xfe not utf-8\n")
    result = sddc("ingest", cwd=repo)

    assert result.returncode == int(ExitCode.INPUT)
    assert "broken.md" in result.stderr
    assert (repo / ".sdd" / "blocks.jsonl").read_bytes() == before


def test_ac_1_23_a_path_outside_the_root_is_refused(repo, tmp_path):
    outside = tmp_path.parent / "outside.md"
    outside.write_text("Nope.\n", encoding="utf-8")
    result = sddc("ingest", str(outside), cwd=repo)
    assert result.returncode == int(ExitCode.INPUT)


def test_a_path_that_is_not_a_spec_source_is_refused(repo):
    stray = repo / "notes.md"
    stray.write_text("Not a spec.\n", encoding="utf-8")
    result = sddc("ingest", "notes.md", cwd=repo)
    assert result.returncode == int(ExitCode.INPUT)
    assert "spec_globs" in result.stderr


def test_ac_1_26_a_held_lock_stops_a_second_run(repo):
    (repo / ".sdd" / "run.lock").write_text(json.dumps({"pid": os.getpid(), "started_at": "x"}), encoding="utf-8")
    env = dict(os.environ)
    env["SDDC_LOCK_WAIT_SECONDS"] = "0.2"
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(
        [sys.executable, "-m", "sdd_compiler", "ingest"],
        capture_output=True, text=True, cwd=repo, env=env,
    )
    assert result.returncode == int(ExitCode.STORE)
    assert "lock" in result.stderr

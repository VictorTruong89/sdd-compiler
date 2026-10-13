"""Hidden tests for the F1 (Ingest) task — black-box, through the `sddc` command and the files it writes.

Never shown to the agent. Derived from the frozen F1 spec (requirements.md maps each test to R1…R28).
They call no function by name: a from-scratch implementation names its internals freely.

Run: SDDC_CMD="/path/to/venv/bin/sddc" pytest hidden_tests/
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

SDDC = shlex.split(os.environ.get("SDDC_CMD", "sddc"))
SPEC = "sdd/specs/a.md"


# -- helpers -------------------------------------------------------------------------------------

def sddc(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([*SDDC, "--root", str(root), *args], capture_output=True, text=True,
                          timeout=60, cwd=root)


def make_repo(tmp_path: Path, files: dict[str, str | bytes] | None = None, init: bool = True) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    for name, content in (files or {}).items():
        write(root, name, content)
    if init:
        result = sddc(root, "init")
        assert result.returncode == 0, result.stderr
    return root


def write(root: Path, name: str, content: str | bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_bytes(content.encode("utf-8"))


def ingest(root: Path, *paths: str) -> subprocess.CompletedProcess:
    result = sddc(root, "ingest", *paths)
    assert result.returncode == 0, f"ingest failed ({result.returncode}): {result.stderr}"
    return result


def jsonl(root: Path, name: str) -> list[dict]:
    path = root / ".sdd" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def blocks(root: Path) -> list[dict]:
    return jsonl(root, "blocks.jsonl")


def live(root: Path) -> list[dict]:
    return [b for b in blocks(root) if b.get("removed_run") is None]


def last_counts(root: Path) -> dict:
    return jsonl(root, "runs.jsonl")[-1]["counts"]


def status(root: Path) -> dict:
    result = sddc(root, "--json", "status")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def by_text(records: list[dict], fragment: str) -> dict:
    [found] = [b for b in records if fragment in b["text"]]
    return found


def store_bytes(root: Path) -> dict[str, bytes]:
    names = ("blocks.jsonl", "sources.jsonl", "runs.jsonl", "profile.yaml")
    return {n: (root / ".sdd" / n).read_bytes() for n in names if (root / ".sdd" / n).exists()}


def set_profile(root: Path, **values) -> None:
    path = root / ".sdd" / "profile.yaml"
    profile = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    profile.update(values)
    path.write_text(yaml.safe_dump(profile), encoding="utf-8")


def rewrite_blocks(root: Path, records: list[dict]) -> None:
    (root / ".sdd" / "blocks.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


# -- segmentation: R1–R8 ---------------------------------------------------------------------------

DOC_1_1 = """# T

P one.

P two.

P three.

- item one
- item two

| H1 | H2 |
|---|---|
| a | b |
| c | d |
"""


def test_ac_1_1_block_kinds_lines_and_heading_path(tmp_path):
    root = make_repo(tmp_path, {SPEC: DOC_1_1})
    ingest(root)
    records = live(root)
    assert len(records) == 7
    kinds = sorted(b["kind"] for b in records)
    assert kinds == ["list_item"] * 2 + ["paragraph"] * 3 + ["table_row"] * 2
    assert by_text(records, "P one.")["lines"] == [3, 3]
    assert by_text(records, "item two")["lines"] == [10, 10]
    assert by_text(records, "| c | d |")["lines"] == [15, 15]
    assert all(b["heading_path"] == ["T"] for b in records)
    assert all(b["source"] == SPEC for b in records)


def test_ac_1_2_headings_set_the_path_and_make_no_block(tmp_path):
    root = make_repo(tmp_path, {SPEC: "## A\n\n### B\n\nText.\n"})
    ingest(root)
    [only] = live(root)
    assert only["heading_path"] == ["A", "B"] and only["text"] == "Text."


def test_ac_1_3_a_nested_item_points_at_its_parent(tmp_path):
    root = make_repo(tmp_path, {SPEC: "- outer\n  - inner\n"})
    ingest(root)
    records = live(root)
    assert sorted(b["kind"] for b in records) == ["list_item", "list_item"]
    [outer] = [b for b in records if b["parent_block"] is None]
    [inner] = [b for b in records if b["parent_block"] is not None]
    assert "inner" in inner["text"]
    assert inner["parent_block"] == outer["id"] and inner["parent_relation"] == "nested"


def test_ac_1_4_table_rows_carry_the_header_and_nothing_else_is_a_block(tmp_path):
    root = make_repo(tmp_path, {SPEC: "| H1 | H2 |\n|---|---|\n| a | b |\n| c | d |\n"})
    ingest(root)
    records = live(root)
    assert len(records) == 2 and all(b["kind"] == "table_row" for b in records)
    assert all(b["table_header"] == "| H1 | H2 |" for b in records)
    assert not any("---" in b["text"] or "H1" in b["text"] for b in records)


def test_ac_1_5_a_blockquote_keeps_its_kind_and_is_marked(tmp_path):
    root = make_repo(tmp_path, {SPEC: "> ⚠ Tokens must never be logged.\n"})
    ingest(root)
    [only] = live(root)
    assert only["kind"] == "paragraph" and only["in_blockquote"] is True


def test_ac_1_6_code_is_stored_and_pending_only_when_the_profile_says(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Intro.\n\n```python\nx = 1\n```\n"})
    ingest(root)
    code = next(b for b in live(root) if b["kind"] == "code")
    assert code["id"] not in {p["id"] for p in status(root)["pending"]}
    set_profile(root, include_code_blocks=True)
    assert code["id"] in {p["id"] for p in status(root)["pending"]}


def test_ac_1_30_continuation_and_nested_and_top_level(tmp_path):
    doc = "- item\n\n  second paragraph\n\n  - sub\n\nTop.\n"
    root = make_repo(tmp_path, {SPEC: doc})
    ingest(root)
    records = live(root)
    [item] = [b for b in records if b["kind"] == "list_item" and b["parent_block"] is None]
    second = by_text(records, "second paragraph")
    [sub] = [b for b in records if b["kind"] == "list_item" and b["parent_block"] is not None]
    top = by_text(records, "Top.")
    assert second["kind"] == "paragraph"
    assert (second["parent_block"], second["parent_relation"]) == (item["id"], "continuation")
    assert (sub["parent_block"], sub["parent_relation"]) == (item["id"], "nested")
    assert top["parent_block"] is None and top["parent_relation"] is None


def test_ac_1_7_front_matter_comments_and_rules_make_no_block(tmp_path):
    doc = "---\ntitle: x\n---\n\n<!-- a comment -->\n\nText.\n\n---\n\nMore.\n"
    root = make_repo(tmp_path, {SPEC: doc})
    ingest(root)
    texts = sorted(b["text"] for b in live(root))
    assert texts == ["More.", "Text."]


# -- identity and change: R9–R14 --------------------------------------------------------------------

def test_ac_1_8_an_unchanged_file_changes_nothing(tmp_path):
    root = make_repo(tmp_path, {SPEC: DOC_1_1})
    ingest(root)
    before = store_bytes(root)
    ingest(root)
    counts = last_counts(root)
    assert (counts["new"], counts["changed"], counts["removed"]) == (0, 0, 0)
    after = store_bytes(root)
    assert after["blocks.jsonl"] == before["blocks.jsonl"]
    assert after["sources.jsonl"] == before["sources.jsonl"]


def test_ac_1_9_an_insertion_keeps_the_other_ids(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Alpha.\n\nBeta.\n"})
    ingest(root)
    ids = {b["text"]: b["id"] for b in live(root)}
    write(root, SPEC, "Inserted.\n\nAlpha.\n\nBeta.\n")
    ingest(root)
    now = {b["text"]: b["id"] for b in live(root)}
    assert now["Alpha."] == ids["Alpha."] and now["Beta."] == ids["Beta."]
    assert now["Inserted."] not in ids.values()
    counts = last_counts(root)
    assert (counts["new"], counts["unchanged"], counts["changed"], counts["removed"]) == (1, 2, 0, 0)


def test_ac_1_10_a_one_word_edit_keeps_the_id(tmp_path):
    root = make_repo(tmp_path, {SPEC: "- one two\n- three\n"})
    ingest(root)
    old = {b["id"]: b for b in live(root)}
    write(root, SPEC, "- one five\n- three\n")
    ingest(root)
    new = {b["id"]: b for b in live(root)}
    assert set(new) == set(old)
    edited = by_text(list(new.values()), "five")
    assert old[edited["id"]]["text_hash"] != edited["text_hash"]
    other = by_text(list(new.values()), "three")
    assert other["text_hash"] == old[other["id"]]["text_hash"]
    counts = last_counts(root)
    assert (counts["changed"], counts["unchanged"], counts["new"], counts["removed"]) == (1, 1, 0, 0)


def test_ac_1_11_a_removed_block_is_kept_and_its_id_never_reused(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Alpha.\n\nBeta.\n"})
    ingest(root)
    beta = by_text(live(root), "Beta.")
    write(root, SPEC, "Alpha.\n")
    ingest(root)
    record = next(b for b in blocks(root) if b["id"] == beta["id"])
    assert record["removed_run"] == jsonl(root, "runs.jsonl")[-1]["id"]
    assert last_counts(root)["removed"] == 1
    write(root, SPEC, "Alpha.\n\nBeta.\n")
    ingest(root)
    again = by_text(live(root), "Beta.")
    assert again["id"] != beta["id"]                                # D12: never resurrected


def test_ac_1_31_pending_is_derived_from_the_atomized_hash(tmp_path):
    root = make_repo(tmp_path, {SPEC: "One.\n\nTwo.\n\nThree.\n"})
    ingest(root)
    ingest(root)
    pending = status(root)["pending"]
    assert len(pending) == 3 and {p["status"] for p in pending} == {"new"}
    records = blocks(root)
    target = by_text(records, "Two.")
    target["atomized_hash"] = target["text_hash"]
    rewrite_blocks(root, records)
    assert len(status(root)["pending"]) == 2
    write(root, SPEC, "One.\n\nTwo, edited.\n\nThree.\n")
    ingest(root)
    pending = {p["id"]: p for p in status(root)["pending"]}
    assert len(pending) == 3 and pending[target["id"]]["status"] == "changed"


def test_ac_1_12_whitespace_and_line_endings_do_not_change_a_block_but_case_does(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Some text must hold.\n"})
    ingest(root)
    write(root, SPEC, b"Some text must hold.   \r\n")
    ingest(root)
    counts = last_counts(root)
    assert (counts["unchanged"], counts["changed"]) == (1, 0)
    write(root, SPEC, "Some text MUST hold.\n")
    ingest(root)
    assert last_counts(root)["changed"] == 1


# -- storage and failures: R15–R19 ---------------------------------------------------------------------

def test_ac_1_21_status_json_is_one_object_of_the_contract_shape(tmp_path):
    root = make_repo(tmp_path, {SPEC: "## H\n\nOne.\n\n- two\n"})
    ingest(root)
    result = sddc(root, "--json", "status")
    assert result.returncode == 0
    payload = json.loads(result.stdout)                               # exactly one JSON document
    assert isinstance(payload, dict)
    assert payload["run"] == jsonl(root, "runs.jsonl")[-1]["id"]
    assert payload["counts"] == {**payload["counts"], "sources": 1, "blocks": 2, "pending": 2}
    for item in payload["pending"]:
        assert {"id", "status", "source", "lines", "heading_path", "kind", "text"} <= set(item)
        assert item["status"] in ("new", "changed")
    assert sorted(p["kind"] for p in payload["pending"]) == ["list_item", "paragraph"]


def test_ac_1_22_a_non_utf8_file_fails_the_whole_ingest(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Fine.\n"})
    ingest(root)
    before = store_bytes(root)
    write(root, "sdd/specs/b.md", b"Bad \xff\xfe bytes.\n")
    write(root, SPEC, "Fine, edited.\n")
    result = sddc(root, "ingest")
    assert result.returncode == 2
    assert "b.md" in result.stderr + result.stdout
    assert store_bytes(root) == before


def test_ac_1_23_a_path_outside_the_root_is_an_input_error(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Fine.\n"})
    outside = tmp_path / "outside.md"
    outside.write_text("Elsewhere.\n", encoding="utf-8")
    assert sddc(root, "ingest", str(outside)).returncode == 2


def test_ac_1_24_without_a_store_every_command_but_init_exits_4(tmp_path):
    root = make_repo(tmp_path, {SPEC: "Fine.\n"}, init=False)
    for command in ("ingest", "status"):
        result = sddc(root, command)
        assert result.returncode == 4, command
        assert "sddc init" in result.stderr + result.stdout


def test_ac_1_25_init_never_overwrites_a_profile(tmp_path):
    root = make_repo(tmp_path)
    profile = root / ".sdd" / "profile.yaml"
    profile.write_text(profile.read_text(encoding="utf-8") + "\n# hand edit\n", encoding="utf-8")
    before = profile.read_bytes()
    assert sddc(root, "init").returncode != 0
    assert profile.read_bytes() == before


# -- contracts: R21–R25 ----------------------------------------------------------------------------------

BLOCK_KEYS = {"id", "source", "kind", "heading_path", "lines", "text", "text_hash", "parent_block",
              "parent_relation", "table_header", "in_blockquote", "first_seen_run", "last_changed_run",
              "removed_run", "atomized_hash"}


def test_ct_1_1_block_records(tmp_path):
    doc = "# T\n\nFirst paragraph\nover two lines.\n\n- item\n\n| A |\n|---|\n| r |\n"
    root = make_repo(tmp_path, {SPEC: doc})
    ingest(root)
    records = blocks(root)
    assert [b["id"] for b in records] == sorted(b["id"] for b in records)
    source_lines = doc.split("\n")
    for b in records:
        assert BLOCK_KEYS <= set(b), BLOCK_KEYS - set(b)
        assert re.fullmatch(r"B-\d{6,}", b["id"])
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", b["text_hash"])
        assert b["kind"] in ("paragraph", "list_item", "table_row", "code")
        assert (b["parent_block"] is None) == (b["parent_relation"] is None)
        assert b["atomized_hash"] is None and b["removed_run"] is None
    para = by_text(records, "First paragraph")
    assert para["lines"] == [3, 4]
    assert para["text"] == "\n".join(source_lines[2:4])               # verbatim slice, 1-based inclusive
    assert para["text_hash"] == "sha256:" + hashlib.sha256(para["text"].encode()).hexdigest()


def test_ct_1_2_source_records(tmp_path):
    root = make_repo(tmp_path, {"sdd/specs/b.md": "B.\n", SPEC: "A.\n"})
    ingest(root)
    records = jsonl(root, "sources.jsonl")
    assert [r["path"] for r in records] == ["sdd/specs/a.md", "sdd/specs/b.md"]
    run = jsonl(root, "runs.jsonl")[-1]["id"]
    for r in records:
        assert {"path", "file_hash", "last_ingest_run"} <= set(r)
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", r["file_hash"]) and r["last_ingest_run"] == run


def test_ct_1_3_one_run_record_per_successful_run_appended(tmp_path):
    root = make_repo(tmp_path, {SPEC: "A.\n"})
    ingest(root)
    first = (root / ".sdd" / "runs.jsonl").read_text(encoding="utf-8")
    ingest(root)
    runs = jsonl(root, "runs.jsonl")
    assert len(runs) == 2
    assert (root / ".sdd" / "runs.jsonl").read_text(encoding="utf-8").startswith(first)
    for r in runs:
        assert {"id", "started_at", "command", "files", "counts", "cli_version"} <= set(r)
        assert {"new", "changed", "unchanged", "removed"} <= set(r["counts"])
    assert runs[0]["id"] != runs[1]["id"]
    assert runs[0]["files"] == [SPEC] and runs[0]["counts"]["new"] == 1


def test_ct_1_4_init_writes_the_profile(tmp_path):
    root = make_repo(tmp_path)
    profile = yaml.safe_load((root / ".sdd" / "profile.yaml").read_text(encoding="utf-8"))
    assert profile["spec_globs"] == ["sdd/specs/**/*.md"]
    assert profile["exclude_globs"] == ["sdd/specs/_templates/**"]
    assert profile["include_code_blocks"] is False


def test_ct_1_6_exit_codes(tmp_path):
    root = make_repo(tmp_path, {SPEC: "A.\n"})
    assert sddc(root, "frobnicate").returncode == 1                   # usage
    assert sddc(root, "ingest", "sdd/specs/missing.md").returncode == 2   # input
    (root / ".sdd" / "profile.yaml").unlink()
    assert sddc(root, "status").returncode == 4                        # store


# -- source selection and determinism: R26, R27 ------------------------------------------------------

def test_source_selection_globs_and_excludes(tmp_path):
    root = make_repo(tmp_path, {SPEC: "A.\n", "sdd/specs/_templates/t.md": "Template.\n",
                                "notes/n.md": "Not a spec.\n"})
    ingest(root)
    assert {r["path"] for r in jsonl(root, "sources.jsonl")} == {SPEC}
    assert sddc(root, "ingest", "notes/n.md").returncode == 2


def test_determinism_identical_sources_give_identical_files(tmp_path):
    files = {SPEC: DOC_1_1, "sdd/specs/b/spec.md": "## X\n\n- a\n  - b\n"}
    one = make_repo(tmp_path / "one", files)
    two = make_repo(tmp_path / "two", files)
    ingest(one)
    ingest(two)
    for name in ("blocks.jsonl", "sources.jsonl"):
        assert (one / ".sdd" / name).read_bytes() == (two / ".sdd" / name).read_bytes(), name

"""F7 §4.2, §4.7–§4.9, CT-7.5, CT-7.6 — `sddc export` end to end.

Covers AC-7.1 … AC-7.4, AC-7.8 … AC-7.11, AC-7.16 … AC-7.20, AC-7.25 (checklist part), AC-7.27. Tier: as each test says.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from export_helpers import b, fixture, link, make_store, n
from smart_fake import SmartFake
from sdd_compiler import __version__
from sdd_compiler.cli import run
from sdd_compiler.conflicts.adjudicate import record_adjudication
from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.export import packs as packs_module
from sdd_compiler.export.pipeline import export
from sdd_compiler.pipeline import compile_graph
from sdd_compiler.store.graph import load_graph

GOLDEN = Path(__file__).parent / "golden" / "export"


def tree(out: Path) -> dict[str, str]:
    return {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(out.rglob("*")) if p.is_file()}


def export_fixture(tmp_path, **kwargs):
    root = fixture(tmp_path / "repo")
    result = export(root, allow_open=True, **kwargs)
    return root, result, tree(result.out)


def code_of(root, *args):
    return run(["--root", str(root), "export", *args])


# -- AC-7.1 lossless, AC-7.8 omitted, AC-7.9 checklist -----------------------------------------

def test_ac_7_1_every_kept_block_is_in_exactly_one_pack(tmp_path):
    root, result, files = export_fixture(tmp_path)
    blocks = [json.loads(line) for line in (root / ".sdd/blocks.jsonl").read_text().splitlines()]
    kept = [x for x in blocks if x["id"] not in {"B-08", "B-10"}]       # Traceability; real duplicate
    packs = {k: v.split("## Text")[1].split("## Claims to implement")[0]     # block text, not list echoes
             for k, v in files.items() if k.startswith("packs/")}
    for block in kept:
        homes = [name for name, text in packs.items() if block["text"] in text]
        assert len(homes) == 1, (block["id"], homes)
    assert "B-10" == result.meta["excluded_blocks"][-1]["block"]


def test_ac_7_8_traceability_is_in_no_file_and_is_counted(tmp_path):
    _, result, files = export_fixture(tmp_path)
    assert not any("test_share.py" in text or "Traceability" in text
                   for name, text in files.items() if name != "export.meta.json")
    assert result.meta["counts"]["blocks_omitted"] == 1
    assert {"block": "B-08", "reason": "skip_heading"} in result.meta["excluded_blocks"]


def test_ac_7_9_the_checklist_has_every_kept_node_once_under_its_pack(tmp_path):
    root, result, files = export_fixture(tmp_path)
    graph = load_graph(root / ".sdd")
    items = re.findall(r"^- \[ \] (\S+)", files["CHECKLIST.md"], re.M)
    assert sorted(items) == sorted(set(graph.nodes) - {"N-000010"})   # N-000010 is the excluded twin
    assert len(items) == len(set(items)) == result.meta["counts"]["checklist_items"]
    section = files["CHECKLIST.md"].split("## Pack 01")[1].split("## Pack")[0]
    assert "N-000002" in section                                        # F1 is pack 01: F2 needs it


# -- AC-7.2 -----------------------------------------------------------------------------------

def test_ac_7_2_a_dropped_block_is_loud_and_nothing_is_written(tmp_path, monkeypatch):
    root = fixture(tmp_path / "repo")
    real = packs_module._text

    def lossy(ctx, unit):
        return real(ctx, unit).replace("A share link MUST expire after 30 days.", "")

    monkeypatch.setattr(packs_module, "_text", lossy)
    with pytest.raises(SddcError) as excinfo:
        export(root, allow_open=True)
    assert excinfo.value.exit_code is ExitCode.STORE and "B-02" in str(excinfo.value)
    assert not (root / ".sdd" / "export").exists()


def test_ac_7_2_a_failed_export_leaves_the_previous_one_intact(tmp_path, monkeypatch):
    root, result, before = export_fixture(tmp_path)
    monkeypatch.setattr(packs_module, "_text", lambda ctx, unit: "")
    with pytest.raises(SddcError):
        export(root, allow_open=True)
    assert tree(result.out) == before


# -- AC-7.3 determinism, AC-7.16 shapes (golden) ---------------------------------------------

def normalise(files):
    return {k: v.replace(__version__, "<version>") for k, v in files.items()}


def test_ac_7_3_two_exports_are_byte_identical_and_match_the_golden(tmp_path):
    _, _, first = export_fixture(tmp_path / "one")
    _, _, second = export_fixture(tmp_path / "two")
    assert first == second
    files = normalise(first)
    if os.environ.get("SDDC_UPDATE_GOLDEN") == "1":
        shutil.rmtree(GOLDEN, ignore_errors=True)
        for name, text in files.items():
            (GOLDEN / name).parent.mkdir(parents=True, exist_ok=True)
            (GOLDEN / name).write_text(text, encoding="utf-8")
    stored = {p.relative_to(GOLDEN).as_posix(): p.read_text(encoding="utf-8")
              for p in sorted(GOLDEN.rglob("*")) if p.is_file()}
    assert stored, "no golden; run with SDDC_UPDATE_GOLDEN=1 and review it"
    assert files == stored


def test_ac_7_16_shapes(tmp_path):
    _, _, files = export_fixture(tmp_path)
    assert sorted(k for k in files if k.startswith("packs/")) == [
        "packs/00-foundation.md", "packs/01-f1-share--1-goal.md", "packs/02-f1-share--2-rules.md",
        "packs/03-f1-share--3-contracts.md", "packs/04-f1-share--4-acceptance.md",
        "packs/05-f2-keep--1-goal.md", "packs/06-f2-keep--2-rules.md"]
    sections = ["## Text", "## Claims to implement", "## Acceptance criteria", "## Constraints in scope",
                "## Related elsewhere", "## Conflicts", "## Terms"]
    for name, text in files.items():
        if name.startswith("packs/"):
            positions = [text.index(s) for s in sections]
            assert positions == sorted(positions), name
    headings = [line for line in files["MAP.md"].splitlines() if line.startswith("#")]
    order = ["# Map", "## Read first", "## Units in build order", "## Needs against the order", "## Contracts",
             "## Decisions", "## How to use", "## Counts"]
    assert headings == order


def test_ac_7_7_a_backward_need_is_listed_in_the_map_and_meta(tmp_path):
    A, B = "sdd/specs/a.md", "sdd/specs/b.md"
    blocks = [b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S"))]
    nodes = [n(f"N-00000{i}", "B-1") for i in (1, 2, 3)] + [n("N-000004", "B-2"), n("N-000005", "B-2"),
                                                          n("N-000006", "B-2")]
    links = [link("N-000001", "depends_on", "N-000004"), link("N-000002", "depends_on", "N-000005"),
             link("N-000003", "depends_on", "N-000006"), link("N-000004", "depends_on", "N-000001")]
    root = make_store(tmp_path, blocks, nodes, links)
    result = export(root)
    assert result.meta["backward_needs"] == [{"from": "01", "to": "02", "links": 1}]
    text = (result.out / "MAP.md").read_text()
    assert "- pack 01 needs pack 02 (1 link)" in text
    assert "01-b--s.md" in text.split("## Units in build order")[1].split("| 02 |")[0]   # b first


# -- AC-7.4 -----------------------------------------------------------------------------------

def test_ac_7_4_no_model_is_constructed(tmp_path, monkeypatch):
    root = fixture(tmp_path / "repo")
    (root / ".sdd" / "profile.yaml").write_text(
        (root / ".sdd" / "profile.yaml").read_text().replace("backend: claude-code", "backend: anthropic-api"))
    import sdd_compiler.llm as llm

    def boom(*args, **kwargs):
        raise AssertionError("a backend was constructed")

    monkeypatch.setattr(llm, "get_backend", boom)
    monkeypatch.setattr(llm, "ClaudeCodeBackend", boom)
    assert export(root, allow_open=True).meta["counts"]["packs"] == 7


# -- gate: AC-7.10, AC-7.11 ---------------------------------------------------------------------

def test_ac_7_10_an_unsettled_contradiction_stops_the_export_with_exit_3(tmp_path, capsys):
    root = fixture(tmp_path / "repo")
    assert code_of(root) == ExitCode.CONFLICTS
    err = capsys.readouterr().err
    assert "CF-000003" in err and "N-000011" in err and "N-000012" in err
    assert not (root / ".sdd" / "export").exists()


def test_ac_7_11_the_override_is_visible_everywhere(tmp_path):
    _, result, files = export_fixture(tmp_path)
    assert result.meta["allow_open"] is True and result.meta["unsettled_ids"] == ["CF-000003"]
    assert files["MAP.md"].split("## Read first")[0].count("UNSETTLED") == 1
    for pack in ("packs/06-f2-keep--2-rules.md",):
        assert "UNSETTLED: CF-000003" in files[pack]


def test_a_settled_store_exports_without_the_override(tmp_path):
    root = fixture(tmp_path / "repo")
    record_adjudication(root / ".sdd", "CF-000003", "false")
    assert code_of(root) == ExitCode.OK
    assert "UNSETTLED" not in (root / ".sdd/export/MAP.md").read_text()


# -- AC-7.17 meta ---------------------------------------------------------------------------------

def test_ac_7_17_meta_validates_and_chars_add_up(tmp_path, capsys):
    root = fixture(tmp_path / "repo")
    capsys.readouterr()                                   # init's own line
    assert code_of(root, "--allow-open", "--json") == 0
    printed = json.loads(capsys.readouterr().out)
    stored = json.loads((root / ".sdd/export/export.meta.json").read_text())
    assert printed == stored
    from sdd_compiler.export.files import META_SCHEMA
    Draft202012Validator(META_SCHEMA).validate(stored)
    assert stored["chars"]["export_total"] == sum(stored["chars"]["packs"].values())
    assert stored["chars"]["packs"]["00-foundation.md"] == len(
        (root / ".sdd/export/packs/00-foundation.md").read_text())
    assert stored["schema_version"] == "export/1" and stored["compiler_version"] == __version__
    assert stored["counts"]["contracts"] == 1 and stored["counts"]["packs"] == 7
    assert stored["backward_needs"] == []


# -- AC-7.18, AC-7.19 -----------------------------------------------------------------------------

def test_ac_7_18_stale_specs_exit_2(tmp_path, capsys):
    root = fixture(tmp_path / "repo")
    (root / "sdd/specs/F1_share/spec.md").write_text("edited\n")
    assert code_of(root, "--allow-open") == ExitCode.INPUT
    err = capsys.readouterr().err
    assert "sdd/specs/F1_share/spec.md" in err and "run sddc compile first" in err
    assert not (root / ".sdd" / "export").exists()


def test_ac_7_19_a_directory_that_is_not_an_export_is_left_alone(tmp_path, capsys):
    root = fixture(tmp_path / "repo")
    target = tmp_path / "src_tree"
    target.mkdir()
    (target / "keep.py").write_text("print(1)\n")
    assert code_of(root, "--allow-open", "--out", str(target)) == ExitCode.USAGE
    assert (target / "keep.py").read_text() == "print(1)\n" and [p.name for p in target.iterdir()] == ["keep.py"]


def test_an_empty_or_earlier_export_directory_is_replaced_whole(tmp_path):
    root, result, _ = export_fixture(tmp_path)
    (result.out / "stale.txt").write_text("x")
    again = export(root, allow_open=True)
    assert "stale.txt" not in tree(again.out)
    empty = tmp_path / "empty"
    empty.mkdir()
    assert export(root, allow_open=True, out=empty).out == empty


# -- map content -----------------------------------------------------------------------------------

def test_map_reads_the_foundation_first_and_indexes_contracts_and_decisions(tmp_path):
    _, _, files = export_fixture(tmp_path)
    text = files["MAP.md"]
    assert "packs/00-foundation.md" in text.split("## Read first")[1].split("##")[0]
    assert "- CT-1.1 → pack 03" in text and "code block B-06" in text
    row = next(line for line in text.splitlines() if line.startswith("| 05 |"))
    assert row.split("|")[-3].strip() == "01"                          # F2's goal needs F1's
    assert "Mark code with `# spec: <id>`" in text


# -- AC-7.20 ------------------------------------------------------------------------------------------

def test_ac_7_20_the_planted_repository_compiles_and_exports(tmp_path):
    repo = tmp_path / "planted"
    shutil.copytree(Path(__file__).parent / "fixtures" / "planted" / "sdd", repo / "sdd")
    from sdd_compiler.commands import init
    init(repo)
    compile_graph(repo, backend=SmartFake(repo))
    graph = load_graph(repo / ".sdd")
    [contradiction] = [c for c in graph.conflicts.values() if c["kind"] == "contradiction"]
    with pytest.raises(SddcError) as excinfo:
        export(repo)
    assert excinfo.value.exit_code is ExitCode.CONFLICTS and contradiction["id"] in str(excinfo.value)
    record_adjudication(repo / ".sdd", contradiction["id"], "false", note="not a real conflict")
    result = export(repo)
    blocks = [json.loads(x) for x in (repo / ".sdd/blocks.jsonl").read_text().splitlines()]
    packs = "\n".join(t for k, t in tree(result.out).items() if k.startswith("packs/"))
    assert all(x["text"] in packs for x in blocks)                       # AC-7.1 on real data
    checklist = re.findall(r"^- \[ \] (\S+)", (result.out / "CHECKLIST.md").read_text(), re.M)
    assert sorted(checklist) == sorted(graph.nodes)                      # AC-7.9
    assert result.meta["counts"]["blocks_pending"] == 4                  # the four AC blocks that failed
    assert "no node (pending)" in packs and "pending" in (result.out / "MAP.md").read_text().split("## Read first")[0]


# -- AC-7.25 (checklist), AC-7.27 ---------------------------------------------------------------

def test_ac_7_25_checklist_items_are_ids_without_text(tmp_path):
    root, _, files = export_fixture(tmp_path)
    graph = load_graph(root / ".sdd")
    for line in files["CHECKLIST.md"].splitlines():
        if line.startswith("- [ ] "):
            node_id, _, rest = line[6:].partition(" · ")
            label = graph.nodes[node_id]["label"]
            assert rest == (label if label and label != node_id else ""), line


def test_ac_7_27_map_gives_each_pack_its_word_count_and_says_text_is_the_spec(tmp_path):
    _, _, files = export_fixture(tmp_path)
    rows = [line for line in files["MAP.md"].split("## Units in build order")[1]
            .split("## Needs")[0].splitlines() if line.startswith("| ") and "`" in line]
    assert rows
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        name = cells[1].strip("`")
        assert cells[-1] == str(len(files[f"packs/{name}"].split())), row
    assert "`## Text` is the specification" in files["MAP.md"]

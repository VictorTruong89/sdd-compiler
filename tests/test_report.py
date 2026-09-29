"""T18 — F6 §4.8, F4 §4.6: the end-of-run report and `sddc conflicts` (AC-6.10, AC-6.11, AC-4.16).

Tier: golden, unit.
"""
from __future__ import annotations

import os
from pathlib import Path

from sdd_compiler.report import conflict_groups, render_report
from sdd_compiler.views.render import conflicts_list

GOLDEN = Path(__file__).parent / "golden"


def node(node_id, text, file="specs/sharing.md", line=5):
    return {"id": node_id, "text": text, "family": "term:share_link", "layer": "L1",
            "source": {"file": file, "block_id": "B-000001", "lines": [line, line]},
            "status": "conflict", "terms": [], "keywords": [], "ambiguity": [],
            "canonical": {"quantities": []}, "conflict_ids": []}


def record(record_id, members, kind="contradiction", rationale="both set the lifetime of a share link",
           state="open"):
    return {"id": record_id, "kind": kind, "members": sorted(members), "rationale": rationale,
            "quotes": {m: f"quote from {m}" for m in members}, "state": state,
            "resolved_reason": None, "detected_run": "R-000002", "resolved_run": None,
            "judgment": "J-000400"}


class FakeGraph:
    def __init__(self, nodes, conflicts):
        self.nodes = {n["id"]: n for n in nodes}
        self.conflicts = {c["id"]: c for c in conflicts}
        self.terms = {}
        self.links = []
        self.reviews = {}


def golden(name, text):
    path = GOLDEN / name
    if os.environ.get("SDDC_UPDATE_GOLDEN") == "1":
        path.write_text(text, encoding="utf-8")
    assert path.exists(), f"missing golden {path}; run with SDDC_UPDATE_GOLDEN=1 and review it"
    assert text == path.read_text(encoding="utf-8")


SUMMARY = {
    "run": "R-000002", "files": ["specs/sharing.md"], "counts": {"new": 4, "changed": 0, "removed": 0},
    "pending": 37, "completed": 37, "failed": 0, "empty_blocks": 2, "empty": [],
    "nodes_formed": 52, "nodes_deleted": 0, "attention_items": 2, "stopped": None, "stop_reason": None,
    "model_calls": 6, "cost_usd": 0.1234, "replayed": 13, "alignments": [], "annotations_dropped": [],
    "conflicts": {"candidates": 44, "pairs_judged": 31, "pairs_replayed": 13, "unjudged_failed": 0,
                  "provisional": 1, "opened": 3, "closed": {"rejudged": 1, "member_deleted": 0},
                  "calls": 6, "incomplete": False, "unjudged": 0, "open": 3,
                  "by_relation": {"none": 38, "refines": 2, "depends_on": 1, "duplicates": 1,
                                  "subsumes": 0, "contradicts": 2},
                  "retrieval": {"nodes_checked": 52}},
}


def graph_with_three_conflicts():
    nodes = [node("N-000017", "A share link expires 30 days after it is created."),
             node("N-000042", "A share link is valid for one hour.", line=22),
             node("N-000051", "A share link never expires.", file="specs/api.md", line=9),
             node("N-000063", "Links expire after a month.", file="specs/api.md", line=14)]
    return FakeGraph(nodes, [
        record("CF-000001", ["N-000017", "N-000042"]),
        record("CF-000002", ["N-000042", "N-000051"]),              # shares N-000042 with CF-000001
        record("CF-000003", ["N-000017", "N-000063"], kind="duplication",
               rationale="the same rule, written twice"),
    ])


# -- AC-4.16 interlinked conflicts are one group ---------------------------------------------

def test_ac_4_16_records_that_share_a_member_are_grouped():
    graph = graph_with_three_conflicts()
    groups = conflict_groups(graph)
    assert [[r["id"] for r in group] for group in groups] == [
        ["CF-000001", "CF-000002", "CF-000003"]]        # all three chain through N-000017/N-000042

    apart = FakeGraph(list(graph.nodes.values()),
                      [record("CF-000001", ["N-000017", "N-000042"]),
                       record("CF-000002", ["N-000051", "N-000063"])])
    assert [[r["id"] for r in group] for group in conflict_groups(apart)] == [
        ["CF-000001"], ["CF-000002"]]


def test_f6_d9_contradictions_come_first_inside_a_group():
    graph = FakeGraph(list(graph_with_three_conflicts().nodes.values()), [
        record("CF-000001", ["N-000017", "N-000042"], kind="duplication"),
        record("CF-000002", ["N-000042", "N-000051"], kind="subsumption"),
        record("CF-000003", ["N-000017", "N-000063"], kind="contradiction"),
    ])
    [group] = conflict_groups(graph)
    assert [r["kind"] for r in group] == ["contradiction", "duplication", "subsumption"]


def test_a_resolved_record_is_not_listed():
    graph = FakeGraph([], [record("CF-000001", ["N-000017", "N-000042"], state="resolved")])
    assert conflict_groups(graph) == []
    assert "No open conflicts" in conflicts_list(graph)


# -- AC-6.10 the report names every conflict, with counts and exit 3 --------------------------

def test_ac_6_10_the_report_lists_the_conflicts_with_members_files_and_lines():
    text = render_report(SUMMARY, graph_with_three_conflicts(), exit_code=3)
    golden("report_conflicts.md", text)
    assert "exit 3" in text
    for part in ("CF-000001", "N-000017", "specs/sharing.md:5", "N-000042", "specs/sharing.md:22",
                 "both set the lifetime of a share link"):
        assert part in text, part


def test_ac_6_11_a_clean_run_says_so_and_names_no_conflicts():
    summary = {**SUMMARY, "conflicts": {**SUMMARY["conflicts"], "opened": 0, "open": 0,
                                        "by_relation": {**SUMMARY["conflicts"]["by_relation"],
                                                        "contradicts": 0, "duplicates": 0}}}
    text = render_report(summary, FakeGraph([], []), exit_code=0)
    golden("report_clean.md", text)
    assert "no conflicts" in text.lower() and "exit 0" in text


def test_ac_6_12_an_incomplete_check_says_how_many_pairs_were_left():
    summary = {**SUMMARY, "conflicts": {**SUMMARY["conflicts"], "incomplete": True, "unjudged": 12}}
    text = render_report(summary, graph_with_three_conflicts(), exit_code=5)
    assert "INCOMPLETE" in text and "12 pair(s) were not judged" in text
    assert "exit 5" in text


def test_the_report_shows_what_formed_no_node_and_what_was_dropped():
    """F3 D33, D35: a silent zero is a failure the report must show (I-59, I-67)."""
    summary = {**SUMMARY, "empty_blocks": 2, "failed": 1,
               "annotations_dropped": [{"block": "B-000009", "file": "specs/a.md", "lines": [3, 3],
                                        "role": "rationale", "quote": "…"}]}
    text = render_report(summary, FakeGraph([], []), exit_code=0)
    assert "2 formed no node" in text and "1 failed" in text
    assert "1 annotation(s) dropped" in text


def test_d38_the_report_counts_definitions_and_lists_the_unattached_ones():
    """F3 §4.8, D38: a definition that matched no term is shown with file and line, never dropped."""
    summary = {**SUMMARY, "definitions": {
        "attached": [{"term": "term:block", "block": "B-000001", "file": "specs/a.md", "lines": [3, 3],
                      "text": "A block is a unit."}],
        "unattached": [{"block": "B-000002", "file": "specs/a.md", "lines": [9, 9],
                        "text": "Both cannot hold.", "reason": "no_term"}]}}
    text = render_report(summary, FakeGraph([], []), exit_code=0)
    assert "1 definition(s) attached to terms · 1 not attached (F3 D38)" in text
    assert "specs/a.md:9  no_term  Both cannot hold." in text
    assert "definition" not in render_report(SUMMARY, FakeGraph([], []), exit_code=0)


# -- the commands (F6 §4.8, F4 §4.6) ----------------------------------------------------------

import json  # noqa: E402

import pytest  # noqa: E402

from sdd_compiler import commands  # noqa: E402
from sdd_compiler.errors import ExitCode  # noqa: E402
from sdd_compiler.llm import FakeBackend  # noqa: E402
from sdd_compiler.pipeline import compile_graph  # noqa: E402
from test_compile import EXPIRY, REVOKE, atom_answer, desc, no_conflicts  # noqa: E402


@pytest.fixture()
def compiled(tmp_path):
    spec = tmp_path / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\n{REVOKE}\n", encoding="utf-8")
    commands.init(tmp_path)
    compile_graph(tmp_path, backend=FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"),
                   desc("B-000002#1", REVOKE, "be revocable")]},
        {"relation": "contradicts", "direction": "symmetric",
         "rationale": "one demands expiry, the other revocation at will",
         "quotes": {"a": "share link", "b": "share link"}, "confidence": "high"},
    ]))
    return tmp_path


def test_compile_prints_the_report_and_exits_three(compiled, capsys):
    code = commands.compile_(compiled, as_json=False)
    out = capsys.readouterr().out
    assert code == ExitCode.CONFLICTS
    assert "CONFLICTS: 1 open (1 contradiction)" in out
    assert "one demands expiry, the other revocation at will" in out
    assert out.rstrip().endswith("exit 3")


def test_compile_json_carries_the_same_numbers(compiled, capsys):
    commands.compile_(compiled, as_json=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["conflicts"]["open"] == 1
    assert payload["conflicts"]["by_relation"]["contradicts"] == 1


def test_sddc_conflicts_lists_the_open_records(compiled, capsys):
    code = commands.conflicts(compiled)
    out = capsys.readouterr().out
    assert code == ExitCode.CONFLICTS                    # F6 §4.8: exit 3 while any is open
    assert "CF-000001" in out and "contradiction" in out
    assert "sdd/specs/F9_demo/spec.md:3" in out


def test_sddc_conflicts_json_gives_the_registry_and_the_records(compiled, capsys):
    commands.conflicts(compiled, as_json=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["registry"]["count"] == 2
    assert [r["id"] for r in payload["conflicts"]] == ["CF-000001"]
    assert payload["conflicts"][0]["members"] == ["N-000001", "N-000002"]
    assert [[r["id"] for r in group] for group in payload["groups"]] == [["CF-000001"]]


def test_sddc_conflicts_on_a_clean_graph_exits_zero(tmp_path, capsys):
    commands.init(tmp_path)
    assert commands.conflicts(tmp_path) == ExitCode.OK
    assert "No open conflicts" in capsys.readouterr().out


def test_d40_the_report_counts_replaced_contract_quotes():
    summary = {**SUMMARY, "contract_quotes_replaced": [
        {"atom": "B-000002#1", "what": "layer Q6", "quote": "x", "node": "CT-1.1"}]}
    assert "1 contract quote(s) not in the source, replaced by code (F3 D40)" in render_report(
        summary, FakeGraph([], []), exit_code=0)
    assert "contract quote" not in render_report(SUMMARY, FakeGraph([], []), exit_code=0)

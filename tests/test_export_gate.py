"""F7 §4.3 (real duplicates), §4.6 — the conflict gate and what each verdict does.

Covers AC-7.10, AC-7.12 (classification part), AC-7.13 (classification part), AC-7.23.
Tier: unit and contract.
"""
from __future__ import annotations

import pytest

from export_helpers import b, conflict, link, make_store, n
from sdd_compiler.export.gate import blocking, classify, excluded_blocks
from sdd_compiler.export.model import load_model


def store(tmp_path, conflicts, verdicts=(), extra_nodes=(), extra_blocks=()):
    blocks = [b("B-1", "sdd/specs/a.md", line=1), b("B-2", "sdd/specs/b.md", line=1), *extra_blocks]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2"), *extra_nodes]
    return make_store(tmp_path, blocks, nodes, conflicts=conflicts, verdicts=verdicts)


def model(tmp_path, *args, **kwargs):
    return load_model(store(tmp_path, *args, **kwargs))


def cf(kind, members=("N-000001", "N-000002"), cid="CF-000001"):
    return conflict(cid, kind, members)


def test_ac_7_10_an_unadjudicated_contradiction_blocks(tmp_path):
    m = model(tmp_path, [cf("contradiction")])
    assert [c["id"] for c in blocking(m)] == ["CF-000001"]


def test_ac_7_12_each_verdict_has_its_own_class(tmp_path):
    conflicts = [cf("contradiction", cid="CF-000001"),
                 conflict("CF-000002", "contradiction", ["N-000001", "N-000003"]),
                 conflict("CF-000003", "contradiction", ["N-000002", "N-000003"])]
    m = model(tmp_path, conflicts, verdicts=[("CF-000001", "false", None),
                                              ("CF-000002", "real", "A wins")],
              extra_nodes=[n("N-000003", "B-1")])
    classes = {c["id"]: classify(m, c) for c in m.open_conflicts()}
    assert classes == {"CF-000001": "dismissed", "CF-000002": "settled", "CF-000003": "unsettled"}
    assert [c["id"] for c in blocking(m)] == ["CF-000003"]


def test_ac_7_12_a_stale_verdict_is_unsettled(tmp_path):
    root = store(tmp_path, [cf("contradiction")], verdicts=[("CF-000001", "real", "A wins")])
    # the pair is judged again: a new judgment id on the record (F6 D14)
    import json
    path = root / ".sdd" / "conflicts.jsonl"
    record = json.loads(path.read_text().splitlines()[0])
    record["judgment"] = "J-000002"
    (root / ".sdd" / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n{"id": "J-000002"}\n')
    path.write_text(json.dumps(record) + "\n")
    m = load_model(root)
    assert [classify(m, c) for c in m.open_conflicts()] == ["unsettled"]


def test_a_resolved_conflict_does_not_count(tmp_path):
    m = model(tmp_path, [conflict("CF-000001", "contradiction", ["N-000001", "N-000002"],
                                  state="resolved")])
    assert blocking(m) == [] and m.open_conflicts() == []


@pytest.mark.parametrize("kind, klass", [("duplication", "same_as"), ("subsumption", "covered_by")])
def test_ac_7_13_duplication_and_subsumption_pass_the_gate(tmp_path, kind, klass):
    m = model(tmp_path, [cf(kind)])
    assert blocking(m) == []
    assert [classify(m, c) for c in m.open_conflicts()] == [klass]


@pytest.mark.parametrize("kind", ["duplication", "subsumption"])
def test_a_false_duplication_or_subsumption_is_dismissed(tmp_path, kind):
    m = model(tmp_path, [cf(kind)], verdicts=[("CF-000001", "false", None)])
    assert [classify(m, c) for c in m.open_conflicts()] == ["dismissed"]


# -- AC-7.23 -----------------------------------------------------------------------

def test_ac_7_23_the_later_block_of_a_real_duplicate_is_excluded(tmp_path):
    m = model(tmp_path, [cf("duplication")], verdicts=[("CF-000001", "real", "same rule")])
    assert m.excluded == {"B-2": "real_duplicate"}
    assert m.resolve("N-000002") == "N-000001"
    assert classify(m, m.open_conflicts()[0]) == "excluded"
    assert "N-000002" not in m.home and "N-000001" in m.home


def test_ac_7_23_unjudged_false_or_stale_keeps_both(tmp_path):
    for verdicts in ([], [("CF-000001", "false", None)]):
        m = model(tmp_path / str(len(verdicts)), [cf("duplication")], verdicts=verdicts)
        assert m.excluded == {}


def test_ac_7_23_a_block_with_one_non_duplicate_node_is_kept(tmp_path):
    m = model(tmp_path, [cf("duplication")], verdicts=[("CF-000001", "real", None)],
              extra_nodes=[n("N-000003", "B-2")])
    assert m.excluded == {}


def test_ac_7_23_a_subsumption_judged_real_excludes_nothing(tmp_path):
    m = model(tmp_path, [cf("subsumption")], verdicts=[("CF-000001", "real", None)])
    assert m.excluded == {}


def test_ac_7_23_a_duplicate_inside_one_block_excludes_nothing(tmp_path):
    root = make_store(tmp_path, [b("B-1")], [n("N-000001", "B-1"), n("N-000002", "B-1")],
                      conflicts=[cf("duplication")], verdicts=[("CF-000001", "real", None)])
    assert load_model(root).excluded == {}


def test_ac_7_23_a_chain_keeps_exactly_the_first(tmp_path):
    blocks = [b("B-1", "sdd/specs/a.md"), b("B-2", "sdd/specs/b.md"), b("B-3", "sdd/specs/c.md")]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2"), n("N-000003", "B-3")]
    conflicts = [conflict("CF-000001", "duplication", ["N-000001", "N-000002"]),
                 conflict("CF-000002", "duplication", ["N-000002", "N-000003"])]
    m = load_model(make_store(tmp_path, blocks, nodes, conflicts=conflicts,
                              verdicts=[("CF-000001", "real", None), ("CF-000002", "real", None)]))
    assert m.excluded == {"B-2": "real_duplicate", "B-3": "real_duplicate"}
    assert m.resolve("N-000003") == "N-000001"


def test_ac_7_23_a_link_to_the_excluded_node_points_at_the_kept_one(tmp_path):
    blocks = [b("B-1", "sdd/specs/a.md"), b("B-2", "sdd/specs/b.md"), b("B-3", "sdd/specs/c.md")]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2"), n("N-000003", "B-3")]
    m = load_model(make_store(
        tmp_path, blocks, nodes, links=[link("N-000003", "depends_on", "N-000002")],
        conflicts=[cf("duplication")], verdicts=[("CF-000001", "real", None)]))
    assert m.links() == [{**link("N-000003", "depends_on", "N-000001")}]

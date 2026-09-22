"""T13, T14 — indexes, `status` node counts, the map, family cards, generated views (F4 §4.4, §4.6).

Covers F4 AC-4.14, AC-4.15, AC-4.17, AC-4.18. Golden files live in tests/golden/.

Tier: unit, golden, property.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

import pytest

from sdd_compiler.store.graph import write_graph
from sdd_compiler.store.index import GraphIndex
from sdd_compiler.views.render import GENERATED_HEADER, family_card, family_label, map_counts, map_table
from worked_example import graph

GOLDEN = Path(__file__).parent / "golden"


# -- T13 indexes (F4 §4.4) ----------------------------------------------------------

def test_indexes_answer_the_f4_lookups():
    index = GraphIndex.build(graph())
    assert len(index.by_id) == 14
    assert index.by_family["term:file"] == ["N-000006", "N-000008"]
    assert index.by_layer["L3"] == ["N-000009", "N-000010"]
    assert index.by_status["conflict"] == ["N-000003", "N-000005"]
    assert index.by_term["term:share_link"][:2] == ["N-000001", "N-000002"]
    assert index.by_term["shared link"] == index.by_term["term:share_link"]      # an alias
    assert index.by_source["specs/sharing.md"][:3] == ["N-000001", "N-000002", "N-000003"]
    assert index.edges_out["N-000010"]["refines"] == ["N-000003"]
    assert index.edges_in["N-000003"]["refines"] == ["N-000010"]


def test_a_family_resolves_from_its_id_its_name_or_an_alias():
    index = GraphIndex.build(graph())
    for name in ("term:share_link", "share_link", "share link", "shared link", "Share Links"):
        assert index.family_of(name) == "term:share_link"
    assert index.family_of("global") == "(global)"
    with pytest.raises(KeyError):
        index.family_of("nothing like it")


def test_the_unplaced_row_of_the_map_opens_as_a_card():
    """M3 gate review: the map shows `(no family)` and the error message offered it, yet
    `sddc family "(no family)"` was refused — the drill-down broke on the row most worth reading."""
    g = graph()
    g.nodes["N-000013"] = {**g.nodes["N-000013"], "family": None}
    index = GraphIndex.build(g)
    for name in ("(no family)", "no family", "_unplaced"):
        assert index.family_of(name) is None
    assert "- N-000013" in family_card(g, None)
    # R12's real cards: with an unplaced node present, `broader: null` read as the family `None`.
    assert "**Kind of:**" not in family_card(g, "term:share_link")


# -- T14 map and family card (golden) --------------------------------------------------

def golden(name, text):
    """Compare with a reviewed golden file. `SDDC_UPDATE_GOLDEN=1` rewrites it — review the diff after."""
    path = GOLDEN / name
    if os.environ.get("SDDC_UPDATE_GOLDEN") == "1":
        path.write_text(text, encoding="utf-8")
    assert path.exists(), f"missing golden {path}; run with SDDC_UPDATE_GOLDEN=1 and review it"
    assert text == path.read_text(encoding="utf-8")


def test_ac_4_14_the_map_marks_the_conflicted_row_and_sorts_it_first():
    text = map_table(graph())
    golden("map_worked_example.md", text)
    rows = [line for line in text.splitlines() if line.startswith("| ") and "---" not in line][1:]
    assert rows[0].startswith("| share_link ")
    assert "4 ✗" in rows[0]                                 # L1: four nodes, one conflict among them


def test_ac_4_15_a_family_card_lists_members_by_layer_in_order():
    text = family_card(graph(), "term:share_link")
    golden("family_share_link.md", text)
    order = [line.split()[1] for line in text.splitlines() if line.startswith("### ")]
    assert order == ["L1", "L2", "L3", "L4", "L5", "C", "V", "In"]     # members, then scope (F4 D14)
    assert "N-000003 ✗" in text


def test_ac_4_18_map_counts_equal_the_records_on_random_graphs():
    rng = random.Random(4018)
    base = graph()
    for _ in range(50):
        g = graph()
        for node_id in list(g.nodes):
            if rng.random() < 0.3 and node_id not in ("N-000003", "N-000005"):
                layer = rng.choice(["L0", "L1", "L2", "L3", "L4", "L5", "C", "V", None])
                g.nodes[node_id] = {**g.nodes[node_id], "layer": layer}
        counts = map_counts(g)
        assert sum(sum(row.values()) for row in counts.values()) == len(g.nodes)
        for (family, layer), n in {(f, l): c for f, row in counts.items() for l, c in row.items()}.items():
            assert n == sum(1 for x in g.nodes.values() if (x["family"], x["layer"]) == (family, layer))
        assert rendered_counts(map_table(g)) == {
            (family_label(f), l or "—"): c for f, row in counts.items() for l, c in row.items()}
    assert map_counts(base)["term:share_link"]["L1"] == 4


def rendered_counts(table):
    """The counts a reader sees: parsed back from the rendered map, not from a helper.
    M3 gate review: the property was first checked on `map_counts`, which the map did not call."""
    lines = [l for l in table.splitlines() if l.startswith("| ")]
    header = [c.strip() for c in lines[0].split("|")[2:-1]]
    seen = {}
    for line in lines[1:]:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        for layer, cell in zip(header, cells[1:]):
            if cell:
                seen[(cells[0], layer)] = int(cell.split()[0])
    return seen


# -- AC-4.17 views are regenerated on every write, marked, and match the CLI ----------------

def test_ac_4_17_views_are_written_with_the_graph(tmp_path):
    store = tmp_path / ".sdd"
    (store / "lock").mkdir(parents=True)
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')
    g = graph()
    write_graph(store, g)
    views = store / "views"
    for path in [views / "map.md", views / "conflicts.md", views / "families" / "share_link.md",
                 views / "families" / "file.md", views / "families" / "_global.md"]:
        assert path.read_text(encoding="utf-8").startswith(GENERATED_HEADER), path
    assert map_table(g) in (views / "map.md").read_text(encoding="utf-8")
    assert "CF-000001" in (views / "conflicts.md").read_text(encoding="utf-8")


def test_a_family_that_disappears_loses_its_card(tmp_path):
    store = tmp_path / ".sdd"
    (store / "lock").mkdir(parents=True)
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')
    g = graph()
    write_graph(store, g)
    from sdd_compiler.store.graph import delete_node, load_graph
    g = load_graph(store)
    for node_id in ("N-000006", "N-000008"):
        delete_node(g, node_id, "R-000002")
    write_graph(store, g)
    assert not (store / "views" / "families" / "file.md").exists()


# -- T13 `status` node counts; T14 `sddc family` ------------------------------------------

import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

from sdd_compiler.commands import init  # noqa: E402

SRC = Path(__file__).resolve().parents[1] / "src"


def sddc(*args, cwd):
    env = dict(os.environ, PYTHONPATH=str(SRC))
    return subprocess.run([sys.executable, "-m", "sdd_compiler", *args], cwd=cwd, env=env,
                          capture_output=True, text=True)


@pytest.fixture()
def compiled(tmp_path):
    init(tmp_path)
    store = tmp_path / ".sdd"
    (store / "lock").mkdir()
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')
    write_graph(store, graph())
    return tmp_path


def test_t13_status_reports_the_graph(compiled):
    payload = json.loads(sddc("status", "--json", cwd=compiled).stdout)
    assert payload["graph"] == {"nodes": 14, "by_status": {"conflict": 2, "validated": 12},
                                "families": 2, "open_conflicts": 1, "attention_items": 0}
    text = sddc("status", cwd=compiled).stdout
    assert "14 nodes" in text and "2 families" in text and "1 open conflict" in text


def test_t14_family_prints_the_card_by_name_or_alias(compiled):
    for name in ("share_link", "shared link", "term:share_link"):
        result = sddc("family", name, cwd=compiled)
        assert result.returncode == 0, result.stderr
        assert result.stdout == family_card(graph(), "term:share_link")


def test_t14_family_json_lists_members_by_layer(compiled):
    payload = json.loads(sddc("family", "file", "--json", cwd=compiled).stdout)
    assert payload["family"] == "term:file"
    assert [m["id"] for m in payload["members"]["L1"]] == ["N-000006"]
    assert [m["id"] for m in payload["members"]["L2"]] == ["N-000008"]


def test_t14_an_unknown_family_is_an_input_error(compiled):
    result = sddc("family", "unicorn", cwd=compiled)
    assert result.returncode == 2
    assert "unicorn" in result.stderr and "share_link" in result.stderr


def test_a_constraint_scoped_to_a_layer_is_in_scope_for_the_family_card():
    """Review of the first golden: N-000014 is scoped to endpoints in L3, where share_link has two.
    F5 D9 (I-57): the layer narrows the named category; a layer alone would need a shared term."""
    card = family_card(graph(), "term:share_link")
    assert "### In scope from elsewhere (1)\n- N-000014 ✓ Every public endpoint must respond within 300 ms." in card
    assert "**In scope from elsewhere:** none" in family_card(graph(), "term:file")
    g = graph()
    g.nodes["N-000014"] = {**g.nodes["N-000014"], "terms": [],
                           "scope_selector": {"families": [], "layers": ["L3"], "terms": [], "categories": []}}
    assert "**In scope from elsewhere:** none" in family_card(g, "term:share_link")


# -- M3 gate review: what a first-time reader needs on a card (F4 D13 … D16) -----------------

def test_card_lines_follow_the_source_not_the_string_order_of_ids():
    """R12's `node` card listed AC-5.13, AC-5.14 before AC-5.2: ids sorted as strings (F4 D13)."""
    g = graph()
    for node_id, line, label in (("N-000013", 30, "AC-5.10"), ("N-000002", 20, "AC-5.8")):
        record = {**g.nodes.pop(node_id), "id": label, "label": label, "layer": "V"}
        record["source"] = {**record["source"], "lines": [line, line]}
        g.nodes[label] = record
    card = family_card(g, "term:share_link")
    assert card.index("- AC-5.8 ") < card.index("- AC-5.10 ")


def test_an_ambiguous_line_says_why():
    """A bare `?` tells the reader nothing to act on (F4 D16)."""
    g = graph()
    g.nodes["N-000002"] = {**g.nodes["N-000002"], "status": "ambiguous",
                           "ambiguity": [{"kind": "referential", "quote": "it", "detail": "x"},
                                         {"kind": "missing_actor", "quote": None, "detail": "x"}]}
    assert "- N-000002 ? (referential, missing_actor) A share link expires" in family_card(g, "term:share_link")


def test_a_card_names_its_broader_and_narrower_families():
    """R12: `checked_node`, `other_node` sat as one-node rows beside `node`, unconnected (F4 D15)."""
    g = graph()
    g.terms["term:share_link"] = {**g.terms["term:share_link"], "broader": "term:file"}
    assert "**Kind of:** file" in family_card(g, "term:share_link")
    assert "**Narrower families:** share_link (11)" in family_card(g, "term:file")
    assert "**Kind of:**" not in family_card(g, "term:file")


def test_global_and_unplaced_rows_come_after_the_families():
    rows = [l.split("|")[1].strip() for l in map_table(graph()).splitlines() if l.startswith("| ")][1:]
    assert rows == ["share_link", "file", "(global)"]


def test_a_card_line_drops_stray_inline_markdown_marks():
    """R12's real card showed "Given** 25 scoring…" and "pair_key` includes…" (F4 D12)."""
    g = graph()
    g.nodes["N-000002"] = {**g.nodes["N-000002"], "text": "Given** a `share link`, **then** it expires"}
    assert "- N-000002 ✓ Given a share link, then it expires" in family_card(g, "term:share_link")


def test_a_card_line_reads_a_table_row_as_cells():
    """R15: the S-rows are nodes now, and their text is the raw row (F4 D12)."""
    g = graph()
    g.nodes["N-000002"] = {**g.nodes["N-000002"],
                           "text": "| **S4 adjacent layer** | Same family, layer distance ≤ 1 | both layers |"}
    assert "- N-000002 ✓ S4 adjacent layer · Same family, layer distance ≤ 1 · both layers" in \
        family_card(g, "term:share_link")


def test_f4_q2_the_markdown_card_keeps_the_whole_claim_the_terminal_cuts_it(tmp_path):
    """F4 Q2 → D17: the 80-character cut hid R12's cap ("… the top max_pairs_per_node (…")."""
    g = graph()
    long = "The rest are ranked by score, then by node id, and the top max_pairs_per_node (default 10) are returned."
    g.nodes["N-000002"] = {**g.nodes["N-000002"], "text": long}
    assert long not in family_card(g, "term:share_link")
    assert "(default 10) are returned." in family_card(g, "term:share_link", width=None)
    store = tmp_path / ".sdd"
    (store / "lock").mkdir(parents=True)
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')
    write_graph(store, g)
    assert long in (store / "views" / "families" / "share_link.md").read_text(encoding="utf-8")

"""F7 §4.3–§4.4 — units, foundation, omitted headings, build order (D3, I-96).

Covers AC-7.5, AC-7.6, AC-7.7, AC-7.8 (unit part), AC-7.26. Tier: unit and property.
"""
from __future__ import annotations

import random
from collections import Counter
from itertools import permutations

from sdd_compiler.export.units import compute_needs, form_units, order_units


def block(bid, source, heading_path, line, kind="paragraph"):
    return {"id": bid, "source": source, "kind": kind, "heading_path": list(heading_path),
            "lines": [line, line], "text": f"text {bid}", "removed_run": None}


def test_ac_7_5_unit_key_is_source_and_first_two_headings():
    blocks = [block("B-1", "a.md", ["T"], 1), block("B-2", "a.md", ["T", "S"], 2),
              block("B-3", "a.md", ["T", "S", "Sub"], 3), block("B-4", "a.md", ["T", "S2"], 4)]
    units = form_units(blocks, foundation_globs=(), skip_headings=())
    by_blocks = {tuple(u.block_ids) for u in units.units}
    assert by_blocks == {("B-1",), ("B-2", "B-3"), ("B-4",)}
    assert units.foundation is None


def test_ac_7_5_foundation_files_form_one_unit_whatever_their_headings():
    blocks = [block("B-1", "sdd/specs/vision.md", ["V", "One"], 1),
              block("B-2", "sdd/specs/constitution.md", ["C", "Two"], 1),
              block("B-3", "sdd/specs/vision.md", ["V", "Three"], 9),
              block("B-4", "sdd/specs/F1/spec.md", ["F1", "S"], 1)]
    units = form_units(blocks, foundation_globs=("**/vision.md", "**/constitution.md"),
                       skip_headings=())
    assert units.foundation is not None
    assert units.foundation.block_ids == ["B-1", "B-3", "B-2"]       # glob order, then line
    assert [u.block_ids for u in units.units] == [["B-4"]]


def test_foundation_glob_matches_a_file_at_the_repository_root():
    units = form_units([block("B-1", "vision.md", ["V"], 1)], ("**/vision.md",), ())
    assert units.foundation is not None


def test_removed_blocks_are_not_live():
    gone = block("B-1", "a.md", ["T", "S"], 1)
    gone["removed_run"] = "R-000002"
    assert form_units([gone], (), ()).units == []


def test_ac_7_8_blocks_under_a_skipped_heading_are_omitted_and_counted():
    blocks = [block("B-1", "a.md", ["T", "S"], 1), block("B-2", "a.md", ["T", "9. Traceability"], 2),
              block("B-3", "a.md", ["T", "9. Traceability", "Sub"], 3)]
    units = form_units(blocks, (), ("Traceability",))
    assert [u.block_ids for u in units.units] == [["B-1"]]
    assert units.omitted == ["B-2", "B-3"]
    again = form_units(blocks, (), ())
    assert again.omitted == [] and len(again.units) == 2            # `skip_headings: []` keeps them


def test_a_unit_with_no_remaining_block_is_not_emitted():
    blocks = [block("B-1", "a.md", ["T", "Traceability"], 1)]
    assert form_units(blocks, (), ("Traceability",)).units == []


def test_excluded_blocks_leave_the_units_and_are_listed():
    blocks = [block("B-1", "a.md", ["T", "S"], 1), block("B-2", "a.md", ["T", "S"], 2)]
    units = form_units(blocks, (), (), excluded={"B-2"})
    assert units.units[0].block_ids == ["B-1"] and units.excluded == ["B-2"]


def file_units(spec):
    """spec: {file: number of sections} → units, several per file, in source order."""
    blocks = [block(f"B-{f}-{k}", f, ["T", f"S{k}"], k + 1) for f, n in spec.items() for k in range(n)]
    return form_units(blocks, (), ()).units


def backward_weight(order, needs):
    pos = {}
    for i, u in enumerate(order):
        pos.setdefault(u.source, i)
    return sum(w for (x, y), w in needs.items() if x[0] != y[0] and pos[y[0]] > pos[x[0]])


def test_ac_7_6_the_file_order_has_the_least_backward_weight_property():
    rng = random.Random(11)
    for _ in range(150):
        files = [f"{c}.md" for c in "abcdef"[:rng.randint(1, 6)]]
        units = file_units({f: rng.randint(1, 3) for f in files})
        needs = Counter()
        for x in units:
            for y in units:
                if x.source != y.source and rng.random() < 0.3:
                    needs[(x.key, y.key)] += rng.randint(1, 4)
        result = order_units(units, needs)
        assert sorted(u.key for u in result.units) == sorted(u.key for u in units)
        # each file's units together, in source order
        seen = [u.source for u in result.units]
        assert [f for i, f in enumerate(seen) if i == 0 or seen[i - 1] != f] == list(dict.fromkeys(seen))
        for f in files:
            mine = [u for u in result.units if u.source == f]
            assert mine == sorted(mine, key=lambda u: u.sort_key)
        best = min(backward_weight([u for g in perm for u in units if u.source == g], needs)
                   for perm in permutations(files))
        assert backward_weight(result.units, needs) == best


def test_ac_7_6_an_acyclic_relation_gives_a_topological_order_and_ties_follow_paths():
    units = file_units({"a.md": 1, "b.md": 1, "c.md": 1, "d.md": 1})
    assert [u.source for u in order_units(units, Counter()).units] == ["a.md", "b.md", "c.md", "d.md"]
    needs = Counter({(units[0].key, units[3].key): 1})                       # a needs d
    assert [u.source for u in order_units(units, needs).units] == ["b.md", "c.md", "d.md", "a.md"]


def test_ac_7_7_a_cycle_is_decided_by_its_votes_and_reported():
    units = file_units({"a.md": 2, "b.md": 1})
    needs = Counter({(units[0].key, units[2].key): 2, (units[1].key, units[2].key): 1,   # a needs b ×3
                     (units[2].key, units[0].key): 1})                                 # b needs a ×1
    result = order_units(units, needs)
    assert [u.source for u in result.units] == ["b.md", "a.md", "a.md"]
    assert result.backward == [(units[2].key, units[0].key, 1)]


def test_section_needs_inside_one_spec_are_not_reported():
    units = file_units({"a.md": 2})
    result = order_units(units, Counter({(units[0].key, units[1].key): 5}))
    assert [u.key for u in result.units] == [units[0].key, units[1].key] and result.backward == []


def test_many_files_use_the_greedy_pass_and_stay_deterministic():
    units = file_units({f"{i:02d}.md": 1 for i in range(12)})
    needs = Counter({(units[i].key, units[i + 1].key): 1 for i in range(11)})   # each needs the next
    first = order_units(units, needs)
    assert [u.source for u in first.units] == [f"{i:02d}.md" for i in reversed(range(12))]
    assert first.backward == [] and order_units(units, needs).units == first.units


def test_needs_count_depends_on_links_between_different_non_foundation_units():
    home = {"N-1": "X", "N-2": "Y", "N-3": "X", "N-4": "F", "N-5": "Y"}
    links = [{"from": "N-1", "type": "depends_on", "to": "N-2"},      # X needs Y
             {"from": "N-3", "type": "depends_on", "to": "N-5"},      # X needs Y again
             {"from": "N-1", "type": "depends_on", "to": "N-3"},      # same unit
             {"from": "N-1", "type": "depends_on", "to": "N-4"},      # foundation
             {"from": "N-2", "type": "refines", "to": "N-1"}]         # not depends_on
    assert compute_needs(links, home, foundation="F") == Counter({("X", "Y"): 2})


def test_ac_7_26_an_oversized_unit_splits_at_its_next_heading():
    from sdd_compiler.export.units import MAX_UNIT_CHARS
    big = "x" * (MAX_UNIT_CHARS // 2)
    blocks = [block("B-1", "a.md", ["T", "Big"], 1), block("B-2", "a.md", ["T", "Big", "One"], 2),
              block("B-3", "a.md", ["T", "Big", "One"], 3), block("B-4", "a.md", ["T", "Big", "Two"], 4),
              block("B-5", "a.md", ["T", "Flat"], 5), block("B-6", "a.md", ["T", "Flat"], 6),
              block("B-7", "a.md", ["T", "Flat"], 7)]
    for x in ("B-2", "B-4", "B-5", "B-6", "B-7"):
        next(b for b in blocks if b["id"] == x)["text"] = big
    units = form_units(blocks, (), ())
    assert [(u.headings, u.block_ids) for u in units.units] == [
        (("T", "Big"), ["B-1"]), (("T", "Big", "One"), ["B-2", "B-3"]), (("T", "Big", "Two"), ["B-4"]),
        (("T", "Flat"), ["B-5", "B-6", "B-7"])]


def test_ac_7_26_a_unit_under_the_limit_is_not_split():
    blocks = [block("B-1", "a.md", ["T", "S"], 1), block("B-2", "a.md", ["T", "S", "Sub"], 2)]
    assert [u.block_ids for u in form_units(blocks, (), ()).units] == [["B-1", "B-2"]]

"""T15 — F5 §4.2, §4.3: the seven candidate sources, their evidence, and the score (AC-5.1 … AC-5.9).

No test here calls a model: F5 makes no model calls at all.

Tier: unit, property.
"""
from __future__ import annotations

import random

from sdd_compiler.profile import DEFAULT_RETRIEVAL, RetrievalSettings
from sdd_compiler.retrieval.score import WEIGHTS, score_of
from sdd_compiler.retrieval.sources import evidence_for

SETTINGS = RetrievalSettings(**DEFAULT_RETRIEVAL)

TERMS = {
    "term:share_link": {"id": "term:share_link", "kind": "entity"},
    "term:file": {"id": "term:file", "kind": "entity"},
    "term:owner": {"id": "term:owner", "kind": "actor"},
    "term:endpoint": {"id": "term:endpoint", "kind": "category"},
    # F2 D16 records what a term is a kind of; R15 makes retrieval read it.
    "term:download_link": {"id": "term:download_link", "kind": "entity", "broader": "term:share_link"},
    "term:expired_link": {"id": "term:expired_link", "kind": "entity", "broader": "term:download_link"},
    "term:export": {"id": "term:export", "kind": "entity"},
    "term:export_archive": {"id": "term:export_archive", "kind": "entity", "broader": "term:export"},
    "term:workspace_export": {"id": "term:workspace_export", "kind": "entity", "broader": "term:export"},
    "term:invoice": {"id": "term:invoice", "kind": "entity"},
}


def node(node_id, *, family="term:share_link", layer="L1", terms=(), keywords=(), block="B-000001",
         quantities=(), selector=None, text="a claim", status="unchecked", role="subject"):
    return {
        "id": node_id, "family": family, "layer": layer, "text": text, "status": status,
        "terms": [{"term": t, "role": role, "quote": "x"} for t in terms],
        "keywords": list(keywords),
        "source": {"file": "specs/a.md", "block_id": block, "lines": [1, 1]},
        "canonical": {"quantities": list(quantities)},
        "scope_selector": selector, "judgments": [],
    }


def quantity(value, unit, norm_unit, norm_value):
    return {"value": value, "unit": unit, "quote": f"{value} {unit}",
            "normalized": {"value": norm_value, "unit": norm_unit}}


def sources(a, b, settings=SETTINGS):
    return {e["source"]: e for e in evidence_for(a, b, terms=TERMS, settings=settings)}


# -- the seven sources ---------------------------------------------------------------

def test_ac_5_1_same_family():
    found = sources(node("N-000001"), node("N-000002"))
    assert found["S1"]["detail"] == {"family": "term:share_link"}
    assert found["S1"]["points"] == 3.0
    assert "S1" not in sources(node("N-000001", family="(global)"), node("N-000002", family="(global)"))
    assert "S1" not in sources(node("N-000001", family=None), node("N-000002", family=None))


def test_ac_5_2_a_shared_entity_term_counts_and_an_actor_does_not():
    shared = sources(node("N-000001", family=None, terms=["term:file"]),
                     node("N-000002", family=None, terms=["term:file"]))
    assert shared["S2"]["detail"] == {"terms": ["term:file"]}
    assert shared["S2"]["points"] == 2.0
    actors = sources(node("N-000003", family=None, terms=["term:owner"]),
                     node("N-000004", family=None, terms=["term:owner"]))
    assert "S2" not in actors


def test_ac_5_2_points_are_capped_at_four():
    many = ["term:share_link", "term:file"]
    found = sources(node("N-000001", family=None, terms=many + ["term:endpoint"]),
                    node("N-000002", family=None, terms=many + ["term:endpoint"]))
    assert found["S2"]["points"] == 4.0                      # 2 entities × 2.0; the category is not one


def test_r15_a_narrower_term_meets_its_broader_one(terms=TERMS):
    """M4 gate I-73: the two sides of a real conflict name the same thing differently. `broader`
    (F2 D16) already records "a kind of"; S2 now follows the chain (F5 D11)."""
    found = sources(node("N-000001", family=None, terms=["term:share_link"]),
                    node("N-000002", family=None, terms=["term:download_link"]))
    assert found["S2"]["detail"] == {"terms": ["term:download_link → term:share_link"]}
    assert found["S2"]["points"] == 2.0
    deep = sources(node("N-000001", family=None, terms=["term:share_link"]),
                   node("N-000002", family=None, terms=["term:expired_link"]))
    assert "S2" in deep                                        # two steps up the chain
    assert "S2" not in sources(node("N-000001", family=None, terms=["term:file"]),
                               node("N-000002", family=None, terms=["term:download_link"]))


def test_r15_same_measured_property_needs_a_shared_word_not_a_shared_term():
    """M4 gate I-73: "5 GB" and "5 GiB" are the same limit written twice, but one node calls it an
    export archive and the other a workspace export, so S6's shared-term requirement killed it.
    A shared keyword is enough now — a quantity of one dimension in two claims about the same
    words is exactly the "30 days versus 1 hour" shape S6 exists for (F5 D11)."""
    a = node("N-000001", family="term:a", terms=["term:export_archive"], keywords=["export", "archive"],
             quantities=[quantity(5, "GB", "B", 5_000_000_000)])
    b = node("N-000002", family="term:b", terms=["term:workspace_export"], keywords=["export", "size"],
             quantities=[quantity(5, "GiB", "B", 5_368_709_120)])
    found = sources(a, b)
    assert found["S6"]["detail"] == {"dimension": "size", "values": ["5 GB", "5 GiB"]}
    assert found["S6"]["points"] == 2.5
    # Not every number with every other: no shared word, no S6.
    apart = node("N-000003", family="term:c", terms=["term:invoice"], keywords=["invoice"],
                 quantities=[quantity(9, "GB", "B", 9_000_000_000)])
    assert "S6" not in sources(a, apart)


def test_r19_two_kinds_of_one_thing_are_a_weaker_kind_of_match():
    """I-76: Q-TERM had already filed `export_archive` and `workspace_export` as kinds of
    `export` — siblings. S2 only followed the chain *between* two terms, so it never saw the
    shared parent, and the pair carrying the 5 GB/5 GiB clash scored on keywords alone (F5 D12)."""
    found = sources(node("N-000001", family=None, terms=["term:export_archive"]),
                    node("N-000002", family=None, terms=["term:workspace_export"]))
    assert "S2" not in found                                  # not the same term, and neither is above the other
    assert found["S8"]["detail"] == {"shared": ["term:export"],
                                     "terms": ["term:export_archive", "term:workspace_export"]}
    assert found["S8"]["points"] == 1.0                       # weaker than a real shared term (2.0)
    assert "S8" not in sources(node("N-000001", family=None, terms=["term:export_archive"]),
                               node("N-000002", family=None, terms=["term:invoice"]))
    # A term and its own parent stay S2's business, not S8's.
    direct = sources(node("N-000001", family=None, terms=["term:export"]),
                     node("N-000002", family=None, terms=["term:export_archive"]))
    assert "S2" in direct and "S8" not in direct


def test_ac_5_3_a_constraint_scope_covers_in_either_direction():
    selector = {"families": [], "layers": ["L3"], "terms": ["term:endpoint"],
                "categories": ["term:endpoint"]}
    constraint = node("N-000100", layer="C", family="(global)", selector=selector,
                      terms=["term:endpoint"], role="scope")
    covered = node("N-000009", layer="L3", family="term:share_link", terms=["term:endpoint"])
    assert sources(constraint, covered)["S3"]["detail"] == {"selector": selector}
    assert sources(covered, constraint)["S3"]["points"] == 2.0          # either direction
    # F5 D9: a layer alone is not a scope — the node shares no term or keyword with it.
    bare = node("N-000101", layer="C", family="(global)",
                selector={"families": [], "layers": ["L3"], "terms": [], "categories": []})
    assert "S3" not in sources(bare, node("N-000010", layer="L3", family=None))


def test_ac_5_4_adjacent_layers_of_one_family():
    found = sources(node("N-000001", layer="L1"), node("N-000002", layer="L2"))
    assert found["S4"]["detail"] == {"layers": ["L1", "L2"]} and found["S4"]["points"] == 1.0
    assert "S4" not in sources(node("N-000001", layer="L1"), node("N-000002", layer="L4"))
    assert "S4" not in sources(node("N-000001", layer="L1", family="term:a"),
                               node("N-000002", layer="L2", family="term:b"))
    assert "S4" not in sources(node("N-000001", layer="C"), node("N-000002", layer="V"))


def test_ac_5_5_shared_keywords_reach_the_minimum():
    two = sources(node("N-000001", keywords=["token", "expiry", "link"]),
                  node("N-000002", keywords=["expiry", "token"]))
    assert two["S5"]["detail"] == {"keywords": ["expiry", "token"]}
    assert two["S5"]["points"] == 1.0                                   # 0.5 each
    one = sources(node("N-000001", keywords=["token"]), node("N-000002", keywords=["token", "x"]))
    assert "S5" not in one


def test_ac_5_5_keyword_points_are_capped_at_two():
    shared = ["a", "b", "c", "d", "e", "f"]
    found = sources(node("N-000001", keywords=shared), node("N-000002", keywords=shared))
    assert found["S5"]["points"] == 2.0


def test_ac_5_6_two_quantities_of_one_dimension():
    a = node("N-000001", terms=["term:share_link"], quantities=[quantity(30, "day", "s", 2592000)])
    b = node("N-000002", terms=["term:share_link"], quantities=[quantity(1, "hour", "s", 3600)])
    found = sources(a, b)
    assert found["S6"]["detail"] == {"dimension": "time", "values": ["30 day", "1 hour"]}
    assert found["S6"]["points"] == 2.5
    other = node("N-000003", terms=["term:share_link"], quantities=[quantity(5, "MB", "B", 5000000)])
    assert "S6" not in sources(a, other)                                 # different dimension
    unrelated = node("N-000004", family=None, terms=[], keywords=["invoice"],
                     quantities=[quantity(1, "hour", "s", 3600)])
    assert "S6" not in sources(node("N-000005", family=None, terms=[], keywords=["backup"],
                                    quantities=[quantity(30, "day", "s", 2592000)]), unrelated)


def test_ac_5_7_same_source_block():
    found = sources(node("N-000001", block="B-000007"), node("N-000002", block="B-000007"))
    assert found["S7"]["detail"] == {"block_id": "B-000007"} and found["S7"]["points"] == 1.5
    assert "S7" not in sources(node("N-000001", block="B-1"), node("N-000002", block="B-2"))


def test_ac_5_8_a_node_alone_in_its_family_is_only_reachable_by_keywords_or_quantities():
    alone = node("N-000001", family="term:only_mine", terms=["term:mine"], block="B-1",
                 keywords=["alpha", "beta"])
    other = node("N-000002", family="term:other", terms=["term:theirs"], block="B-2",
                 keywords=["gamma"])
    assert evidence_for(alone, other, terms=TERMS, settings=SETTINGS) == []      # legitimately none
    sharing = node("N-000003", family="term:other", terms=["term:theirs"], block="B-3",
                   keywords=["alpha", "beta"])
    assert set(sources(alone, sharing)) <= {"S5", "S6"}


# -- the score explains itself (AC-5.9) -------------------------------------------------

def test_ac_5_9_points_sum_to_the_score_over_many_random_pairs():
    rng = random.Random(59)
    families = ["term:share_link", "term:file", "(global)", None]
    words = ["token", "expiry", "link", "file", "owner"]
    for _ in range(200):
        def rand(node_id):
            return node(node_id, family=rng.choice(families),
                        layer=rng.choice(["L0", "L1", "L2", "L3", "L4", "L5", "C", "V"]),
                        terms=rng.sample(list(TERMS), rng.randint(0, 3)),
                        keywords=rng.sample(words, rng.randint(0, 4)),
                        block=rng.choice(["B-1", "B-2"]),
                        quantities=[quantity(30, "day", "s", 2592000)] if rng.random() < 0.4 else [])
        evidence = evidence_for(rand("N-000001"), rand("N-000002"), terms=TERMS, settings=SETTINGS)
        score = score_of(evidence)
        assert score == round(sum(e["points"] for e in evidence), 4)
        assert all(e["points"] > 0 for e in evidence)
        assert [e["source"] for e in evidence] == sorted(e["source"] for e in evidence)


def test_the_weights_are_the_ones_the_spec_prints():
    assert WEIGHTS == {"S1": 3.0, "S2": 2.0, "S3": 2.0, "S4": 1.0, "S5": 0.5, "S6": 2.5, "S7": 1.5,
                       "S8": 1.0}

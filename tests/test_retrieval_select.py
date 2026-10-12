"""T15 — F5 §4.1, §4.3, §4.4: which nodes are checked, ranking, the cap, pair identity
(AC-5.10 … AC-5.14, CT-5.1, CT-5.3).

Tier: unit, property, contract.
"""
from __future__ import annotations

import random

from sdd_compiler.profile import DEFAULT_RETRIEVAL, RetrievalSettings
from sdd_compiler.retrieval.select import needs_checking, pair_key, propose
from test_retrieval_sources import TERMS, node

SETTINGS = RetrievalSettings(**DEFAULT_RETRIEVAL)


def graph_of(nodes):
    return {n["id"]: n for n in nodes}


# -- §4.1 which nodes are checked (AC-5.14) ---------------------------------------------

def test_ac_5_14_status_decides_what_is_checked():
    assert needs_checking(node("N-1", status="unchecked"))
    assert needs_checking(node("N-2", status="stale"))
    assert needs_checking(node("N-3", status="conflict"))            # judged again
    assert not needs_checking(node("N-4", status="validated"))
    ambiguous = node("N-5", status="ambiguous")
    assert needs_checking(ambiguous)                                  # never judged
    assert not needs_checking({**ambiguous, "last_checked_run": "R-000002"})


def test_i86_an_ambiguous_node_formed_by_the_atomizer_is_still_never_judged():
    """`judgments` lists the Q-ATOM/Q-DESC answers that formed the node, so it is never empty on a
    real graph; "never judged" (F5 §4.1) is about the check phase. R18: 416 of 937 nodes skipped."""
    formed = {**node("N-6", status="ambiguous"), "judgments": ["J-000001", "J-000002"]}
    assert needs_checking(formed)


def test_checking_order_is_source_then_line_then_id():
    nodes = [node("N-000003"), node("N-000001"), node("N-000002")]
    nodes[0]["source"] = {**nodes[0]["source"], "file": "specs/a.md", "lines": [9, 9]}
    nodes[1]["source"] = {**nodes[1]["source"], "file": "specs/b.md", "lines": [1, 1]}
    nodes[2]["source"] = {**nodes[2]["source"], "file": "specs/a.md", "lines": [9, 9]}
    result = propose(graph_of(nodes), terms=TERMS, settings=SETTINGS)
    assert result.checked == ["N-000002", "N-000003", "N-000001"]


# -- §4.4 pair identity (AC-5.12) --------------------------------------------------------

def test_ac_5_12_the_key_is_symmetric_and_follows_the_text():
    a, b = node("N-000001", text="one"), node("N-000002", text="two")
    assert pair_key(a, b) == pair_key(b, a)
    assert pair_key(a, b).startswith("sha256:")
    assert pair_key(a, {**b, "text": "two, edited"}) != pair_key(a, b)
    assert pair_key({**a, "text": "one, edited"}, b) != pair_key(a, b)


def test_ac_5_12_the_key_holds_over_random_texts():
    rng = random.Random(512)
    for _ in range(200):
        a = node("N-%06d" % rng.randint(1, 50), text="".join(rng.choices("abcdef", k=rng.randint(1, 9))))
        b = node("N-%06d" % rng.randint(51, 99), text="".join(rng.choices("abcdef", k=rng.randint(1, 9))))
        assert pair_key(a, b) == pair_key(b, a)
        assert (pair_key(a, b) == pair_key(a, {**b, "text": b["text"] + "!"})) is False


# -- §4.3 ranking and the cap (AC-5.10, AC-5.11, AC-5.13) --------------------------------

CAP_TEN = RetrievalSettings(**{**DEFAULT_RETRIEVAL, "max_pairs_per_node": 10})


def test_f5_d13_the_default_cap_is_six():
    """R20 (B): on R17's store, 10 gave 184 pairs and 6 gave 117 — every pair a human had judged
    real survived. The cap is where cost lives: one call per pair."""
    assert SETTINGS.max_pairs_per_node == 6


def test_ac_5_10_the_cap_keeps_the_ten_highest_and_the_counts_say_what_it_dropped():
    checked = node("N-000000", keywords=["shared", "words"])
    others = []
    for n in range(1, 26):
        # A descending score: the first few also share a block, then keywords, then family alone.
        others.append(node("N-%06d" % n, status="validated", block="B-000001" if n <= 5 else "B-other",
                           keywords=["shared", "words"] if n <= 12 else []))
    result = propose(graph_of([checked, *others]), terms=TERMS, settings=CAP_TEN)

    assert len(result.pairs) == 10
    assert [c["rank"] for c in result.pairs] == list(range(1, 11))
    scores = [c["score"] for c in result.pairs]
    assert scores == sorted(scores, reverse=True)
    assert [c["b"] for c in result.pairs][:5] == ["N-000001", "N-000002", "N-000003", "N-000004",
                                                  "N-000005"]                    # ties break by id
    counts = result.counts
    assert counts["nodes_checked"] == 1
    assert counts["candidates_proposed"] == 25
    assert counts["dropped_by_cap"] == 15
    assert counts["dropped_below_min_score"] == 0
    assert counts["pairs_capped"] == 10
    # AC-5.16's identity, on the proposals the run made.
    assert counts["candidates_proposed"] == (counts["pairs_capped"] + counts["dropped_below_min_score"]
                                             + counts["dropped_by_cap"])


def test_a_candidate_below_min_score_is_dropped_and_counted():
    a = node("N-000001", family="term:a", keywords=["x"], block="B-1")
    b = node("N-000002", family="term:b", keywords=["x"], block="B-2", status="validated")
    settings = RetrievalSettings(**{**DEFAULT_RETRIEVAL, "min_shared_keywords": 1})
    result = propose(graph_of([a, b]), terms=TERMS, settings=settings)
    assert result.pairs == []                                   # 0.5 < min_score 1.0
    assert result.counts["dropped_below_min_score"] == 1


def test_ac_5_13_a_node_is_never_its_own_candidate_and_a_pair_appears_once():
    nodes = [node("N-000001"), node("N-000002"), node("N-000003")]
    result = propose(graph_of(nodes), terms=TERMS, settings=SETTINGS)
    keys = [c["pair_key"] for c in result.pairs]
    assert len(keys) == len(set(keys)) == 3                     # 3 nodes, 3 unordered pairs
    assert all(c["a"] != c["b"] for c in result.pairs)
    assert all(c["a"] < c["b"] for c in result.pairs)           # unordered: stored by id


def test_ac_5_11_insertion_order_never_changes_the_result():
    rng = random.Random(511)
    nodes = [node("N-%06d" % n, family=rng.choice(["term:a", "term:b"]),
                  layer=rng.choice(["L1", "L2", "L4"]),
                  keywords=rng.sample(["token", "link", "file", "expiry"], 2),
                  block=rng.choice(["B-1", "B-2"])) for n in range(1, 13)]
    first = propose(graph_of(nodes), terms=TERMS, settings=SETTINGS)
    for _ in range(5):
        shuffled = nodes[:]
        rng.shuffle(shuffled)
        again = propose(graph_of(shuffled), terms=TERMS, settings=SETTINGS)
        assert again.pairs == first.pairs
        assert again.counts == first.counts


def test_ct_5_1_a_candidate_record_carries_what_the_contract_says():
    result = propose(graph_of([node("N-000001"), node("N-000002")]), terms=TERMS, settings=SETTINGS)
    [candidate] = result.pairs
    assert sorted(candidate) == ["a", "b", "evidence", "pair_key", "rank", "score"]
    assert candidate["evidence"] and all(
        sorted(e) == ["detail", "points", "source"] for e in candidate["evidence"])
    assert candidate["score"] == round(sum(e["points"] for e in candidate["evidence"]), 4)


def test_ct_5_3_the_counts_a_run_records():
    result = propose(graph_of([node("N-000001"), node("N-000002")]), terms=TERMS, settings=SETTINGS)
    assert sorted(result.counts) == ["candidates_proposed", "dropped_below_min_score",
                                     "dropped_by_cap", "nodes_checked", "pairs_capped", "replayed"]

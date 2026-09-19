"""F5 D9 · F4 D11 — when a constraint's scope selector covers a node (M3 gate review, I-57).

One rule, shared by the family card's "in scope" list (F4) and retrieval source S3 (F5), so the
view and retrieval cannot disagree.

Tier: unit.
"""
from __future__ import annotations

from sdd_compiler.model.scope import covers


def c_node(families=(), layers=(), terms=(), categories=(), uses=(), keywords=()):
    return {"id": "N-000100", "layer": "C", "family": "(global)",
            "terms": [{"term": t, "role": "scope", "quote": "x"} for t in uses],
            "keywords": list(keywords),
            "scope_selector": {"families": list(families), "layers": list(layers),
                               "terms": list(terms), "categories": list(categories)}}


def node(layer="L3", family="term:share_link", uses=(), keywords=()):
    return {"id": "N-000001", "layer": layer, "family": family,
            "terms": [{"term": t, "role": "subject", "quote": "x"} for t in uses], "keywords": list(keywords)}


def test_a_named_family_or_term_covers_the_node():
    assert covers(c_node(families=["term:share_link"]), node())
    assert covers(c_node(terms=["term:token"]), node(uses=["term:token"]))
    assert covers(c_node(categories=["term:api"]), node(uses=["term:api"]))
    assert not covers(c_node(families=["term:file"]), node())


def test_layers_narrow_a_named_scope():
    assert covers(c_node(categories=["term:api"], layers=["L3"]), node(layer="L3", uses=["term:api"]))
    assert not covers(c_node(categories=["term:api"], layers=["L3"]), node(layer="L1", uses=["term:api"]))


def test_a_layer_alone_needs_a_shared_term_or_keyword():
    """I-57: on R12, three layer-only constraints would have made ≈ 60 S3 pairs among 43 nodes.
    A layer-only scope is global within the layer, so it takes F5 D7's bar for `(global)`."""
    bare = c_node(layers=["L3"], uses=["term:endpoint"], keywords=["respond", "endpoint"])
    assert not covers(bare, node(layer="L3"))
    assert covers(bare, node(layer="L3", uses=["term:endpoint"]))
    assert covers(bare, node(layer="L3", keywords=["endpoint"]))
    assert not covers(bare, node(layer="L1", uses=["term:endpoint"]))


def test_an_empty_selector_covers_nothing_here():
    """A `(global)` constraint is F5 D7's case, not the selector's (F4 D11)."""
    assert not covers(c_node(), node(uses=["term:x"]))

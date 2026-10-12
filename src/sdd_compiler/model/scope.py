"""F2 D13 selector, read by F4's family card (D11) and F5's source S3 (D9): does a constraint cover a node?

⚑ F5 D9 (M3 gate review, I-57): a selector that **names** something — a family, a term or a
category — covers a node that matches it, and its layers, if any, narrow that match. A selector
with **layers only** is a global constraint within those layers, so it takes the bar F5 D7 sets for
`(global)` constraints: the node must also share a term or a keyword with the constraint. Measured
on R12: layer-only selectors alone would have proposed ≈ 60 pairs among 43 nodes. An empty
selector covers nothing here; `(global)` is F5 D7's case.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def covers(constraint: Mapping[str, Any], node: Mapping[str, Any]) -> bool:
    selector = constraint.get("scope_selector") or {}
    layers = set(selector.get("layers") or [])
    families = set(selector.get("families") or [])
    named = set(selector.get("terms") or []) | set(selector.get("categories") or [])
    node_terms = {t["term"] for t in node.get("terms") or []}
    if layers and node.get("layer") not in layers:
        return False
    if families or named:
        return node.get("family") in families or bool(named & node_terms)
    if layers:
        shared_terms = node_terms & {t["term"] for t in constraint.get("terms") or []}
        shared_words = set(node.get("keywords") or []) & set(constraint.get("keywords") or [])
        return bool(shared_terms or shared_words)
    return False

"""F2 §4.2 — the layers are constants (D8, P-7).

Their set and meanings live in code, not in the profile: a graph whose layers
mean different things in each project could not be compared, queried or checked
by the same rules. A profile may only rename a layer for display and give
section-heading hints, which are recorded as priors and never override an
answer (P-12).
"""
from __future__ import annotations

LAYERS: dict[str, str] = {
    "L0": "Intent — why the system exists; the outcome it serves",
    "L1": "Behavior — what an outside party observes, without naming protocol artefacts",
    "L2": "Structure — which components exist, what each owns, where they run",
    "L3": "Contract — an agreement between two named parties",
    "L4": "Data — shape, type, identity or lifecycle of stored or transferred data",
    "L5": "Logic — an internal rule or algorithm of one component",
    "C": "Constraints — a restriction over many nodes: budgets, invariants, policies",
    "V": "Verification — a test or check of other nodes",
}

#: Precedence order of the layer questions (F2 §4.3) and the layer each selects.
QUESTIONS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
LAYER_OF_QUESTION = {
    "Q1": "C", "Q2": "L0", "Q3": "L1", "Q4": "L2", "Q5": "L3", "Q6": "L4", "Q7": "L5",
}

#: The only per-layer settings a profile may supply.
PROFILE_LAYER_KEYS = ("display", "hints")

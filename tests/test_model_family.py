"""T9 — F2 §4.4 family: exactly one, by the first rule that applies (AC-2.6 … AC-2.11).

Tier: unit.
"""
from __future__ import annotations

from sdd_compiler.model.family import derive_family, term_links


def term(term_id, kind, role):
    return {"term": term_id, "kind": kind, "role": role, "quote": term_id.split(":")[1]}


def test_ac_2_6_an_entity_subject_is_the_family():
    result = derive_family(
        layer="L1", subject="share link",
        terms=[term("term:share_link", "entity", "subject")],
    )
    assert (result.family, result.rule) == ("term:share_link", "subject")
    assert result.ambiguity == []


def test_ac_2_7_the_system_as_subject_uses_the_first_entity_in_the_response():
    result = derive_family(
        layer="L1", subject="the system",
        terms=[term("term:owner", "actor", "response"), term("term:file", "entity", "response")],
    )
    assert (result.family, result.rule) == ("term:file", "response")


def test_ac_2_7_an_actor_subject_never_seeds_a_family():
    result = derive_family(
        layer="L1", subject="the owner",
        terms=[term("term:owner", "actor", "subject"), term("term:file", "entity", "response")],
    )
    assert (result.family, result.rule) == ("term:file", "response")


def test_ac_2_8_a_verification_spanning_families_takes_the_first_and_is_flagged():
    result = derive_family(
        layer="V", subject="the test", terms=[],
        verified_families=["term:upload", "term:share_link"],
    )
    assert (result.family, result.rule) == ("term:upload", "verification")
    assert result.flags == ["family_disputed"]


def test_ac_2_8_a_verification_within_one_family_is_not_flagged():
    result = derive_family(layer="V", subject="the test", terms=[],
                           verified_families=["term:upload", "term:upload"])
    assert result.flags == []


def test_ac_2_9_a_constraint_scoped_to_one_family_belongs_to_it():
    result = derive_family(layer="C", subject="every request", terms=[],
                           scope_families=["term:upload"])
    assert (result.family, result.rule) == ("term:upload", "constraint")


def test_ac_2_9_a_constraint_spanning_families_or_unscoped_is_global():
    two = derive_family(layer="C", subject="x", terms=[], scope_families=["term:a", "term:b"])
    none = derive_family(layer="C", subject="x", terms=[], scope_families=[])
    assert (two.family, two.rule) == ("(global)", "constraint")
    assert (none.family, none.rule) == ("(global)", "constraint")


def test_ac_2_10_nothing_resolves_so_the_family_is_null_and_ambiguous():
    result = derive_family(layer="L5", subject="it", terms=[])
    assert (result.family, result.rule) == (None, "fallback")
    assert [a["kind"] for a in result.ambiguity] == ["unresolved_term"]


def test_ac_2_10_a_pin_overrides_every_rule():
    result = derive_family(
        layer="L1", subject="share link",
        terms=[term("term:share_link", "entity", "subject")], pin="term:file",
    )
    assert (result.family, result.rule) == ("term:file", "pinned")
    assert result.flags == ["pinned_family"]


def test_the_subject_rule_comes_first_even_for_a_constraint():
    """F2 §4.4: "the first rule that applies" — rule 1 before rule 4 (F2 D9)."""
    result = derive_family(layer="C", subject="uploaded files",
                           terms=[term("term:file", "entity", "subject")],
                           scope_families=["term:a", "term:b"])
    assert (result.family, result.rule) == ("term:file", "subject")


def test_a_category_never_seeds_a_family():
    result = derive_family(layer="L2", subject="sharing",
                           terms=[term("term:sharing", "category", "subject")])
    assert result.family is None


def test_a_component_subject_names_the_family_only_as_a_last_resort():
    """F2 D19 (M3 gate, I-56): "exhaustive mode" had ≈ 5 claims and no family — a component
    never seeded one. It now does, after every other rule, so it absorbs only would-be nulls."""
    result = derive_family(layer="L1", subject="the mode",
                           terms=[term("term:exhaustive_mode", "component", "subject"),
                                  term("term:sharing", "category", "response")])
    assert (result.family, result.rule) == ("term:exhaustive_mode", "component")
    assert result.ambiguity == []
    mentioned = derive_family(layer="L1", subject="the mode",
                              terms=[term("term:exhaustive_mode", "component", "subject"),
                                     term("term:pair", "entity", "response")])
    assert mentioned.family == "term:pair"                  # response rule, as before


def test_a_verification_takes_what_it_verifies_before_its_given_clause_subject():
    """F2 D18 (M3 gate, I-56): nine F5 criteria sat in `node` because "Given two nodes…" named the
    subject, and rule 1 ran before rule 3. A test belongs with what it tests."""
    result = derive_family(layer="V", subject="two nodes",
                           terms=[term("term:node", "entity", "subject")],
                           verified_families=["term:candidate"])
    assert (result.family, result.rule) == ("term:candidate", "verification")
    unresolved = derive_family(layer="V", subject="two nodes", terms=[term("term:node", "entity", "subject")])
    assert (unresolved.family, unresolved.rule) == ("term:node", "subject")


def test_ac_2_11_mentioning_a_term_links_it_without_changing_the_family():
    terms = [term("term:share_link", "entity", "subject"), term("term:file", "entity", "response")]
    result = derive_family(layer="L1", subject="share link", terms=terms)
    links = term_links("N-000001", terms)

    assert result.family == "term:share_link"
    assert {(l["from"], l["type"], l["to"]) for l in links} == {
        ("N-000001", "uses_term", "term:share_link"),
        ("N-000001", "uses_term", "term:file"),
    }
    assert all(l["provenance"] == "code" and l["judgment"] is None for l in links)


def test_r4_a_seed_term_anywhere_names_the_family_before_null():
    """rel01 D32 R4: 20 of 84 gate nodes had no family; a mentioned entity is better than none."""
    result = derive_family(layer="L1", subject="it",
                           terms=[term("term:owner", "actor", "subject"), term("term:file", "entity", "trigger")])
    assert (result.family, result.rule) == ("term:file", "mention")
    assert result.ambiguity == []

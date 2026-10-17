"""T10 — forming nodes from pending blocks (F3 §4.5; AC-3.5, 3.9, 3.12, 3.14 … 3.16; F2 D12, D13).

Every model answer is scripted with the fake backend, in the order the pipeline
asks: Q-ATOM for a chunk, Q-DESC for its atoms, then Q-TERM when needed.

Tier: integration (the whole pipeline, in memory) and unit.
"""
from __future__ import annotations

import pytest

from sdd_compiler.atomize.forming import resolve_verifies, scope_selector
from sdd_compiler.atomize.pipeline import atomize_pending
from sdd_compiler.atomize.terms import similar_terms
from sdd_compiler.llm import CallBudget, FakeBackend
from sdd_compiler.model.schema import validate

EXPIRY = "A share link must expire 30 days after it is created."


def block(block_id, text, kind="paragraph", line=3, heading=("Sharing",)):
    return {"id": block_id, "text": text, "kind": kind, "heading_path": list(heading),
            "table_header": None, "source": "sdd/specs/F9_demo/spec.md",
            "lines": [line, line + text.count("\n")], "text_hash": f"sha256:{block_id}"}


def q_atom(*entries):
    """entries: (block_id, [(kind, [quotes]), …])"""
    return {"blocks": [
        {"block_id": block_id,
         "sentences": [{"quote": q, "role": kind} for kind, quotes in atoms for q in quotes],
         "atoms": [{"kind": kind, "quotes": quotes} for kind, quotes in atoms]}
        for block_id, atoms in entries
    ]}


NO = {"answer": "no", "quote": None}


def q_desc_entry(atom_id, subject="share link", response="expire 30 days after it is created",
                 q_yes=None, terms=None, modality="MUST", scope_layers=(), verifies_text=None,
                 decision=None, canonical=None):
    q_yes = q_yes if q_yes is not None else {"Q3": "expire 30 days after it is created"}
    answers = {f"Q{n}": dict(NO) for n in range(1, 8)}
    for question, quote in q_yes.items():
        answers[question] = {"answer": "yes", "quote": quote}
    return {
        "atom_id": atom_id,
        "canonical": canonical or {"state": None, "trigger": None, "scope": None,
                                   "subject": subject, "modality": modality, "response": response},
        "layer_answers": answers,
        "terms": terms if terms is not None else
                 [{"name": "share link", "kind": "entity", "role": "subject", "quote": "share link"}],
        "ambiguity": [],
        "scope_layers": list(scope_layers),
        "scope_description": None,
        "verifies_text": verifies_text,
        "decision": decision,
    }


def q_desc(*entries):
    return {"atoms": list(entries)}


def run(blocks, answers, **options):
    backend = FakeBackend(answers, budget=options.pop("budget", None))
    options.setdefault("run_id", "R-0002")
    return atomize_pending(blocks, backend, **options), backend


# -- AC-3.14 a node is formed ---------------------------------------------------

def test_ac_3_14_one_requirement_forms_one_valid_node():
    draft, backend = run([block("B-000001", EXPIRY)], [
        q_atom(("B-000001", [("requirement", [EXPIRY])])),
        q_desc(q_desc_entry("B-000001#1")),
    ])
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc"]   # empty registry: no Q-TERM

    [node] = draft.nodes.values()
    validate("node", node)
    assert node["id"] == "N-000001"
    assert (node["layer"], node["family"], node["family_rule"]) == ("L1", "term:share_link", "subject")
    assert node["last_checked_run"] is None and node["status"] == "unchecked"
    assert node["source"]["block_id"] == "B-000001" and node["source"]["spans"] == [[0, len(EXPIRY)]]
    assert node["canonical"]["quantities"][0]["normalized"] == {"value": 2_592_000, "unit": "s"}
    assert ("N-000001", "uses_term", "term:share_link") in {
        (l["from"], l["type"], l["to"]) for l in draft.links}
    assert draft.terms["term:share_link"]["status"] == "proposed"
    assert draft.completed == {"B-000001": "sha256:B-000001"}
    assert draft.stopped is None


def test_a_block_with_no_atoms_completes_without_nodes():
    draft, _ = run([block("B-000001", "This section explains the background.")], [
        {"blocks": [{"block_id": "B-000001",
                     "sentences": [{"quote": "This section explains the background.", "role": "context"}],
                     "atoms": []}]},
    ])
    assert draft.nodes == {}
    assert draft.completed == {"B-000001": "sha256:B-000001"}


# -- AC-3.15 term resolution ----------------------------------------------------------

REGISTRY = {"term:share_link": {"id": "term:share_link", "canonical": "share link",
                                "aliases": ["shared link"], "kind": "entity",
                                "definition": None, "defined_by": None, "status": "confirmed", "broader": None}}


def test_ac_3_15_an_alias_resolves_without_asking():
    text = "A shared link must expire 30 days after it is created."
    tags = [{"name": "shared link", "kind": "entity", "role": "subject", "quote": "shared link"}]
    draft, backend = run([block("B-000001", text)], [
        q_atom(("B-000001", [("requirement", [text])])),
        q_desc(q_desc_entry("B-000001#1", subject="shared link", terms=tags)),
    ], registry=REGISTRY)
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc"]
    [node] = draft.nodes.values()
    assert node["terms"][0]["term"] == "term:share_link"
    assert draft.terms == {}                                   # nothing new


SHARING = "A sharing link must expire 30 days after it is created."
SHARING_TAGS = [{"name": "sharing link", "kind": "entity", "role": "subject", "quote": "sharing link"}]


def test_ac_3_15_an_unsure_term_is_kept_separate_and_sent_for_review():
    draft, backend = run([block("B-000001", SHARING)], [
        q_atom(("B-000001", [("requirement", [SHARING])])),
        q_desc(q_desc_entry("B-000001#1", subject="sharing link", terms=SHARING_TAGS)),
        {"terms": [{"term_key": "term:sharing_link", "verdict": "unsure",
                    "target": None, "reason": "may be the share link"}]},
    ], registry=REGISTRY)
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc", "q-term"]
    assert "term:share_link" in backend.asked[2].prompt

    [node] = draft.nodes.values()
    assert node["terms"][0]["term"] == "term:sharing_link"
    assert "pending_review" in [a["kind"] for a in node["ambiguity"]]
    assert node["status"] == "ambiguous"
    [item] = [r for r in draft.reviews if r["type"] == "term_unsure"]
    assert item["subject"] == "term:sharing_link" and item["state"] == "open"
    validate("term", draft.terms["term:sharing_link"])


def test_q_term_same_must_name_one_of_the_candidates():
    bad = {"terms": [{"term_key": "term:sharing_link", "verdict": "same",
                      "target": "term:invented", "reason": "r"}]}
    good = {"terms": [{"term_key": "term:sharing_link", "verdict": "same",
                       "target": "term:share_link", "reason": "one thing"}]}
    draft, backend = run([block("B-000001", SHARING)], [
        q_atom(("B-000001", [("requirement", [SHARING])])),
        q_desc(q_desc_entry("B-000001#1", subject="sharing link", terms=SHARING_TAGS)),
        bad, good,
    ], registry=REGISTRY)
    assert [q.kind for q in backend.asked][-2:] == ["q-term", "q-term"]
    [item] = [r for r in draft.reviews if r["type"] == "term_same"]
    assert "term:share_link" in item["detail"]


def test_f3_d20_a_same_verdict_merges_at_once_and_can_be_undone():
    """F3 Q7 option b: the new name becomes an alias; nothing turns ambiguous."""
    draft, _ = run([block("B-000001", SHARING)], [
        q_atom(("B-000001", [("requirement", [SHARING])])),
        q_desc(q_desc_entry("B-000001#1", subject="sharing link", terms=SHARING_TAGS)),
        {"terms": [{"term_key": "term:sharing_link", "verdict": "same",
                    "target": "term:share_link", "reason": "one thing"}]},
    ], registry=REGISTRY)
    [node] = draft.nodes.values()
    assert node["terms"][0]["term"] == "term:share_link"
    assert node["family"] == "term:share_link"
    assert "pending_review" not in [a["kind"] for a in node["ambiguity"]]
    assert node["status"] == "unchecked"
    assert "term:sharing_link" not in draft.terms
    assert draft.terms["term:share_link"]["aliases"] == ["shared link", "sharing link"]
    [item] = [r for r in draft.reviews if r["type"] == "term_same"]
    assert item["subject"] == "term:share_link"
    assert "reject" in item["detail"].lower()


def test_f3_d20_a_later_tag_with_the_merged_name_resolves_without_asking():
    second = "A sharing link must be revocable."
    tags = [{"name": "sharing link", "kind": "entity", "role": "subject", "quote": "sharing link"}]
    draft, backend = run([block("B-000001", SHARING), block("B-000002", second, line=9)], [
        q_atom(("B-000001", [("requirement", [SHARING])])),
        q_desc(q_desc_entry("B-000001#1", subject="sharing link", terms=SHARING_TAGS)),
        {"terms": [{"term_key": "term:sharing_link", "verdict": "same",
                    "target": "term:share_link", "reason": "one thing"}]},
        q_atom(("B-000002", [("requirement", [second])])),
        q_desc(q_desc_entry("B-000002#1", subject="sharing link", response="be revocable",
                            q_yes={"Q3": second}, terms=tags)),
    ], registry=REGISTRY, block_batch=1)
    assert [q.kind for q in backend.asked].count("q-term") == 1
    assert {n["terms"][0]["term"] for n in draft.nodes.values()} == {"term:share_link"}


def test_similar_terms_share_a_word_or_most_letters():
    assert [t["id"] for t in similar_terms("sharing link", REGISTRY)] == ["term:share_link"]
    assert similar_terms("invoice", REGISTRY) == []


# -- AC-3.16 a block is all or nothing -------------------------------------------------

THREE = "Links must expire. Links must be revocable. Links must be logged."


def test_ac_3_16_one_failed_atom_drops_the_whole_block():
    quotes = ["Links must expire.", "Links must be revocable.", "Links must be logged."]
    link = [{"name": "link", "kind": "entity", "role": "subject", "quote": "Links"}]
    bad = q_desc_entry("B-000001#3", subject="links", q_yes={"Q3": "not in the block"}, terms=link)
    draft, _ = run([block("B-000001", THREE)], [
        q_atom(("B-000001", [("requirement", [q]) for q in quotes])),
        q_desc(*(q_desc_entry(f"B-000001#{n}", subject="links", q_yes={"Q3": quotes[n - 1]}, terms=link)
                 for n in (1, 2)), bad),
        q_desc(bad),
    ])
    assert draft.nodes == {}
    assert "B-000001" in draft.failed and "B-000001" not in draft.completed
    [item] = draft.reviews
    assert (item["type"], item["subject"]) == ("atomize_failed", "B-000001")


# -- AC-3.12 a T3 split re-asks Q-ATOM once ---------------------------------------------------

TWO_LAYERS = "The service stores each link. The API returns 404 for an expired link."


def test_ac_3_12_split_required_re_asks_q_atom_with_both_quotes():
    whole = [TWO_LAYERS]
    split = q_desc_entry("B-000001#1", subject="the service",
                         q_yes={"Q4": "The service stores each link",
                                "Q5": "The API returns 404 for an expired link"},
                         terms=[{"name": "link", "kind": "entity", "role": "response", "quote": "link"}])
    first, second = "The service stores each link.", "The API returns 404 for an expired link."
    link = [{"name": "link", "kind": "entity", "role": "response", "quote": "link"}]
    draft, backend = run([block("B-000001", TWO_LAYERS)], [
        q_atom(("B-000001", [("requirement", whole)])),
        q_desc(split),
        q_atom(("B-000001", [("requirement", [first]), ("requirement", [second])])),
        q_desc(q_desc_entry("B-000001#1", subject="the service", q_yes={"Q4": first}, terms=link),
               q_desc_entry("B-000001#2", subject="the API", q_yes={"Q5": second}, terms=link)),
    ])
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc", "q-atom", "q-desc"]
    assert "The service stores each link" in backend.asked[2].prompt
    assert "The API returns 404 for an expired link" in backend.asked[2].prompt
    assert sorted(n["layer"] for n in draft.nodes.values()) == ["L2", "L3"]


def test_r16_a_table_row_is_never_split_into_its_cells():
    """R16 (I-70): F3 D34 folds a row's atoms into one — but only on the first pass. The split
    re-ask (AC-3.12) then asked the model to separate the row's rule from its evidence column,
    and it obliged: every one of F5's seven source rows became two nodes, one of them a bare
    fragment ("the term ids", "the block id"). A row is one claim, so it is placed by its first
    yes and flagged, never re-asked (F3 D36)."""
    row = "| **S2 shared subject term** | Shares a term of kind `entity` | the term ids |"
    cells = ["Shares a term of kind `entity`", "the term ids"]
    split = q_desc_entry("B-000001#1", subject="the pair",
                         q_yes={"Q4": cells[0], "Q5": cells[1]},
                         terms=[{"name": "term", "kind": "entity", "role": "response", "quote": "term"}])
    draft, backend = run([block("B-000001", row, kind="table_row")], [
        q_atom(("B-000001", [("requirement", [cells[0]]), ("requirement", [cells[1]])])),
        q_desc(split),
    ])
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc"]      # no second Q-ATOM
    [node] = draft.nodes.values()                                      # one node, not one per cell
    assert "Shares a term of kind" in node["text"] and "the term ids" in node["text"]
    assert [a["kind"] for a in node["ambiguity"] if a["kind"] == "mixed_layers"] == ["mixed_layers"]


def test_i42_a_refused_split_forms_the_node_with_the_first_layer_flagged_mixed():
    """F3 D23: two refusals to split are evidence of one claim — form it, flag it, never fail it."""
    split = q_desc_entry("B-000001#1", subject="the service",
                         q_yes={"Q4": "The service stores each link",
                                "Q5": "The API returns 404 for an expired link"},
                         terms=[{"name": "link", "kind": "entity", "role": "response", "quote": "link"}])
    draft, _ = run([block("B-000001", TWO_LAYERS)], [
        q_atom(("B-000001", [("requirement", [TWO_LAYERS])])), q_desc(split),
        q_atom(("B-000001", [("requirement", [TWO_LAYERS])])), q_desc(split),
    ])
    assert draft.failed == {}
    [node] = draft.nodes.values()
    assert node["layer"] == "L2"                                   # the first yes (Q4)
    [flag] = [a for a in node["ambiguity"] if a["kind"] == "mixed_layers"]
    assert flag["quote"] == "The API returns 404 for an expired link"
    assert node["status"] == "ambiguous"
    validate("node", node)


# -- AC-3.9 an inferred node is flagged and reviewed ---------------------------------------------

def test_ac_3_9_an_inferred_node_is_ambiguous_and_has_a_review_item():
    injected = q_desc_entry("B-000001#1", response="expire after 30 days, encrypted with AES-256")
    draft, _ = run([block("B-000001", EXPIRY)], [
        q_atom(("B-000001", [("requirement", [EXPIRY])])), q_desc(injected),
    ])
    [node] = draft.nodes.values()
    assert node["flags"] == ["inferred"] and node["status"] == "ambiguous"
    [item] = draft.reviews
    assert (item["type"], item["subject"]) == ("inferred_node", node["id"])


# -- F2 D12 labels and adopted ids ---------------------------------------------------------------

def test_d12_a_single_node_block_adopts_its_id_and_a_split_one_labels_every_node():
    # CT labels: an AC-labelled block is always one verification atom (R8), so it cannot split.
    single = "- **CT-1.4** — the link must expire."
    double = "- **CT-1.5** — the link must expire. the link must be revocable."
    link = [{"name": "link", "kind": "entity", "role": "subject", "quote": "link"}]
    draft, _ = run([block("B-000001", single, kind="list_item"),
                    block("B-000002", double, kind="list_item", line=4)], [
        q_atom(("B-000001", [("requirement", ["the link must expire."])]),
               ("B-000002", [("requirement", ["the link must expire."]),
                             ("requirement", ["the link must be revocable."])])),
        q_desc(*(q_desc_entry(i, subject="the link", q_yes={"Q3": q}, terms=link)
                 for i, q in (("B-000001#1", "the link must expire."),
                              ("B-000002#1", "the link must expire."),
                              ("B-000002#2", "the link must be revocable.")))),
    ])
    by_label = sorted((n["id"], n["label"]) for n in draft.nodes.values())
    assert by_label == [("CT-1.4", "CT-1.4"), ("N-000001", "CT-1.5"), ("N-000002", "CT-1.5")]


# -- F2 D13 scope selector and verifies (AC-2.24, AC-2.25) --------------------------------------------

def test_ac_2_24_the_scope_selector_is_built_from_scope_terms_and_scope_layers():
    terms = [
        {"term": "term:upload", "kind": "entity", "role": "scope"},
        {"term": "term:api", "kind": "category", "role": "scope"},
        {"term": "term:owner", "kind": "actor", "role": "subject"},
    ]
    assert scope_selector(terms, ["L3"]) == {
        "families": ["term:upload"], "layers": ["L3"],
        "terms": ["term:api", "term:upload"], "categories": ["term:api"],
    }


def test_ac_2_24_a_constraint_scoped_to_one_family_joins_it():
    text = "Every upload request must be logged."
    tags = [{"name": "request", "kind": "event", "role": "response", "quote": "request"},
            {"name": "upload", "kind": "entity", "role": "scope", "quote": "upload"}]
    draft, _ = run([block("B-000001", text)], [
        q_atom(("B-000001", [("constraint", [text])])),
        q_desc(q_desc_entry("B-000001#1", subject="every request", response="be logged",
                            q_yes={"Q1": "Every upload request must be logged"}, terms=tags,
                            scope_layers=["L3"])),
    ])
    [node] = draft.nodes.values()
    assert node["layer"] == "C"
    assert node["scope_selector"]["families"] == ["term:upload"]
    assert (node["family"], node["family_rule"]) == ("term:upload", "constraint")


def test_f3_d33_a_block_whose_sentences_are_all_context_is_completed_and_recorded_empty():
    """The block is not a failure — nothing in it is a claim — but the run must say so (I-59)."""
    heading = "**Source | Rule | Evidence recorded**"
    draft, _ = run([block("B-000001", heading, kind="table_row")], [
        {"blocks": [{"block_id": "B-000001", "sentences": [{"quote": heading, "role": "definition"}],
                     "atoms": []}]},
    ])
    assert draft.nodes == {} and draft.failed == {}
    assert "B-000001" in draft.completed
    assert draft.empty == {"B-000001": {"block": "B-000001", "file": "sdd/specs/F9_demo/spec.md",
                                        "lines": [3, 3], "roles": ["definition"]}}


def node_stub(node_id, label=None, family=None, layer="L1", text="", file="a.md", block_id=None):
    return {"id": node_id, "label": label, "family": family, "layer": layer, "text": text,
            "source": {"file": file, "block_id": block_id or f"B-{node_id}", "spans": [[0, 1]]},
            "verifies": None}


def test_f2_d20_a_local_label_resolves_only_inside_its_own_file():
    """"then S4 contributes" verifies F5's S4 row — not a row "S4" in another spec."""
    nodes = {
        "N-000001": node_stub("N-000001", "S4", "term:candidate", file="f5.md"),
        "N-000002": node_stub("N-000002", "S4", "term:other", file="f9.md"),
        "AC-5.4": node_stub("AC-5.4", "AC-5.4", layer="V", text="Given two nodes, then S4 contributes.",
                            file="f5.md"),
    }
    verifies, _ = resolve_verifies(nodes, {"AC-5.4": None})
    assert verifies == {"AC-5.4": ["N-000001"]}


def test_f2_d20_a_local_label_on_two_blocks_of_one_file_resolves_to_nothing():
    nodes = {
        "N-000001": node_stub("N-000001", "D1", block_id="B-1"),
        "N-000002": node_stub("N-000002", "D1", block_id="B-2"),
        "N-000003": node_stub("N-000003", "S1", block_id="B-3"),
        "N-000004": node_stub("N-000004", "S1", block_id="B-3"),          # one block, two nodes
        "AC-1.1": node_stub("AC-1.1", layer="V", text="Given D1, then S1 holds."),
    }
    verifies, _ = resolve_verifies(nodes, {"AC-1.1": None})
    assert verifies == {"AC-1.1": ["N-000003", "N-000004"]}


def test_f2_d20_a_criterion_joins_the_family_of_the_row_it_cites():
    """End to end, the F5 shape: a table row "S4", then a criterion "Given two nodes …, then S4 …"."""
    row = "| **S4 adjacent layer** | Same family and layer distance ≤ 1 | both layers |"
    check = "- **AC-5.4** — **Given** two nodes of one family, **then** S4 contributes."
    draft, _ = run([block("B-000001", row, kind="table_row"), block("B-000002", check, line=9, kind="list_item")], [
        q_atom(("B-000001", [("requirement", ["Same family and layer distance ≤ 1"])]),
               ("B-000002", [("verification", ["**Given** two nodes of one family, **then** S4 contributes."])])),
        q_desc(q_desc_entry("B-000001#1", subject="candidate", q_yes={"Q1": "Same family and layer distance ≤ 1"},
                            terms=[{"name": "candidate", "kind": "data", "role": "subject", "quote": "Same family"}]),
               q_desc_entry("B-000002#1", subject="two nodes", response="S4 contributes", q_yes={},
                            terms=[{"name": "node", "kind": "entity", "role": "subject", "quote": "two nodes"}],
                            modality=None, verifies_text="S4")),
    ])
    row_node = next(n for n in draft.nodes.values() if n["layer"] != "V")
    criterion = draft.nodes["AC-5.4"]
    assert row_node["label"] == "S4"
    assert criterion["verifies"] == [row_node["id"]]
    assert (criterion["family"], criterion["family_rule"]) == ("term:candidate", "verification")


def test_ac_2_25_a_cited_label_resolves_to_every_node_carrying_it():
    nodes = {
        "N-000001": node_stub("N-000001", "AC-1.4", "term:table"),
        "N-000002": node_stub("N-000002", "AC-1.4", "term:table"),
        "N-000003": node_stub("N-000003", layer="V", text="The fixture test checks AC-1.4."),
        "N-000004": node_stub("N-000004", layer="V", text="It is tested."),
    }
    verifies, links = resolve_verifies(nodes, {"N-000003": None, "N-000004": None})
    assert verifies == {"N-000003": ["N-000001", "N-000002"], "N-000004": []}
    assert [(l["from"], l["type"], l["to"], l["provenance"]) for l in links] == [
        ("N-000003", "verifies", "N-000001", "code"), ("N-000003", "verifies", "N-000002", "code")]


def test_ac_2_25_a_verification_joins_the_family_of_what_it_verifies():
    target = "- **CT-1.4** — the table must carry its header."
    check = "The fixture test checks CT-1.4."
    table = [{"name": "table", "kind": "entity", "role": "subject", "quote": "table"}]
    draft, _ = run([block("B-000001", target, kind="list_item"), block("B-000002", check, line=9)], [
        q_atom(("B-000001", [("requirement", ["the table must carry its header."])]),
               ("B-000002", [("verification", [check])])),
        q_desc(q_desc_entry("B-000001#1", subject="the table", q_yes={"Q6": "the table must carry its header."},
                            terms=table),
               q_desc_entry("B-000002#1", subject="the fixture test", response="checks CT-1.4",
                            q_yes={}, terms=[], modality=None, verifies_text="CT-1.4")),
    ])
    verification = next(n for n in draft.nodes.values() if n["layer"] == "V")
    assert verification["verifies"] == ["CT-1.4"]
    assert (verification["family"], verification["family_rule"]) == ("term:table", "verification")
    validate("node", verification)


# -- AC-3.5 the call cap keeps completed chunks ------------------------------------------------------

def test_ac_3_5_the_call_cap_keeps_finished_blocks_and_leaves_the_rest_pending():
    other = "A share link must be revocable."
    draft, _ = run(
        [block("B-000001", EXPIRY), block("B-000002", other, line=5)],
        [q_atom(("B-000001", [("requirement", [EXPIRY])])), q_desc(q_desc_entry("B-000001#1"))],
        budget=CallBudget(max_calls=2), block_batch=1,
    )
    assert draft.stopped == "call_cap"
    assert list(draft.completed) == ["B-000001"]
    assert "B-000002" not in draft.failed
    assert len(draft.nodes) == 1


# -- layer hints ------------------------------------------------------------------------------------------

def test_a_profile_hint_matching_the_heading_is_recorded_not_obeyed():
    draft, _ = run([block("B-000001", EXPIRY, heading=("Data model",))], [
        q_atom(("B-000001", [("requirement", [EXPIRY])])), q_desc(q_desc_entry("B-000001#1")),
    ], layer_hints={"L4": {"display": None, "hints": ["## Data model"]}})
    [node] = draft.nodes.values()
    assert node["layer_hint"] == "L4"
    assert node["layer"] == "L1"


# -- term hygiene (F3 D19): families are terms, so terms must name things -----------------

from sdd_compiler.atomize.terms import fold_name, is_term_name  # noqa: E402


@pytest.mark.parametrize("name", ["AC-1.9", "D9", "F6", "P-6", "rel01 S21", "120 s timeout",
                                  "include_code_blocks: false", "they return only ok and reason now"])
def test_ids_values_and_clauses_are_not_terms(name):
    assert not is_term_name(name)


@pytest.mark.parametrize("name", ["share link", "block", "blocks.jsonl", "profile", "Claude Code"])
def test_names_of_things_are_terms(name):
    assert is_term_name(name)


@pytest.mark.parametrize(("name", "folded"), [
    ("blocks", "block"), ("Share Links", "share link"), ("status", "status"),
    ("process", "process"), ("analysis", "analysis"), ("entries", "entry"), ("runs", "run"),
])
def test_names_fold_to_the_singular(name, folded):
    assert fold_name(name) == folded


def test_a_plural_resolves_to_the_singular_term_without_asking():
    text = "Blocks must keep their ids."
    tags = [{"name": "blocks", "kind": "data", "role": "subject", "quote": "Blocks"},
            {"name": "AC-1.9", "kind": "external_reference", "role": "scope", "quote": "Blocks"}]
    registry = {"term:block": {"id": "term:block", "canonical": "block", "aliases": [],
                               "kind": "data", "definition": None, "defined_by": None, "status": "proposed", "broader": None}}
    draft, backend = run([block("B-000001", text)], [
        q_atom(("B-000001", [("requirement", [text])])),
        q_desc(q_desc_entry("B-000001#1", subject="blocks", response="keep their ids",
                            q_yes={"Q6": text}, terms=tags)),
    ], registry=registry)
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc"]
    [node] = draft.nodes.values()
    assert [t["term"] for t in node["terms"]] == ["term:block"]     # the id tag is dropped
    assert draft.terms == {}


def test_a_merge_into_a_term_merged_in_the_same_batch_follows_the_chain():
    """Live M2 gate, run 2: B was judged the same as A after A had merged away — KeyError."""
    from sdd_compiler.atomize.terms import resolve_terms
    tags = [{"name": "link token", "kind": "entity"}, {"name": "token link", "kind": "entity"}]
    backend = FakeBackend([{"terms": [
        {"term_key": "term:link_token", "verdict": "same", "target": "term:share_link", "reason": "r"},
        {"term_key": "term:token_link", "verdict": "same", "target": "term:link_token", "reason": "r"},
    ]}])
    result = resolve_terms(tags, REGISTRY, backend)
    assert result.by_tag == {"link token": "term:share_link", "token link": "term:share_link"}
    assert result.changed_terms["term:share_link"]["aliases"] == ["link token", "shared link", "token link"]
    assert result.new_terms == {}


# -- rel01 D33 R1: a kind of X is `narrower`, not `same` ------------------------------------

def test_r1_a_narrower_term_stays_separate_and_records_its_broader_term():
    """Live gate: "review item" merged into "item" — 9 of 16 `same` verdicts were kinds of."""
    from sdd_compiler.atomize.terms import resolve_terms
    registry = {"term:item": {"id": "term:item", "canonical": "item", "aliases": [], "kind": "entity",
                              "definition": None, "defined_by": None, "status": "confirmed", "broader": None}}
    backend = FakeBackend([{"terms": [{"term_key": "term:review_item", "verdict": "narrower",
                                       "target": "term:item", "reason": "a review item is a kind of item"}]}])
    result = resolve_terms([{"name": "review item", "kind": "entity"}], registry, backend)
    assert result.by_tag == {"review item": "term:review_item"}
    assert result.new_terms["term:review_item"]["broader"] == "term:item"
    assert result.reviews == [] and result.pending_review == set()
    assert "narrower" in backend.asked[0].prompt and "a kind of" in backend.asked[0].prompt


def test_r1_narrower_must_name_a_candidate():
    from sdd_compiler.atomize.terms import resolve_terms
    bad = {"terms": [{"term_key": "term:sharing_link", "verdict": "narrower", "target": "term:nope", "reason": "r"}]}
    good = {"terms": [{"term_key": "term:sharing_link", "verdict": "different", "target": None, "reason": "r"}]}
    backend = FakeBackend([bad, good])
    resolve_terms([{"name": "sharing link", "kind": "entity"}], REGISTRY, backend)
    assert len(backend.asked) == 2


# -- rel01 D33 R2: Q-DESC is shown the vocabulary ---------------------------------------------

def test_r2_the_description_question_lists_known_terms_and_the_kind_of_rule():
    from sdd_compiler.atomize.describe import DescribeItem, build_question
    from sdd_compiler.atomize.qatom import Atom
    item = DescribeItem("B-000001#1", Atom("B-000001", "requirement", [EXPIRY], [(0, len(EXPIRY))]),
                        block("B-000001", EXPIRY))
    prompt = build_question([item], None, vocabulary=["share link", "owner"]).prompt
    assert "- share link" in prompt and "- owner" in prompt
    assert "a kind of" in prompt.lower()


def test_r2_the_vocabulary_is_not_part_of_the_lock_key():
    from sdd_compiler.atomize.describe import build_question
    assert build_question([], None, vocabulary=["share link"]).prompt == build_question([], None).prompt


def test_r2_the_pipeline_offers_same_file_terms_first():
    from sdd_compiler.atomize.pipeline import vocabulary
    registry = {f"term:t{i}": {"id": f"term:t{i}", "canonical": f"t{i}", "aliases": [], "kind": "entity",
                               "definition": None, "defined_by": None, "status": "proposed", "broader": None} for i in range(5)}
    usage_total = {"term:t0": 9, "term:t1": 1, "term:t2": 5}
    usage_by_file = {"a.md": {"term:t1": 1}}
    assert vocabulary(registry, usage_total, usage_by_file, ["a.md"], limit=3) == ["t1", "t0", "t2"]


# -- rel01 D32: R3/R11 layer questions, R8 criteria, R9 non-claims ----------------------------

def test_r3_r11_layer_questions_carry_no_trigger_words():
    from sdd_compiler.atomize.describe import LAYER_QUESTIONS
    text = dict(LAYER_QUESTIONS)
    assert "every / all / never" not in text["Q1"]
    assert "inside" in text["Q3"].lower()


def test_r9_the_atomizer_is_shown_what_is_not_a_claim():
    from sdd_compiler.atomize.qatom import build_question
    prompt = build_question([], None).prompt
    for marker in ("Why:", "Rejected:", "open question", "title", "Given"):
        assert marker in prompt


def test_r8_an_acceptance_criterion_becomes_one_verification_node():
    """Live gate: AC blocks split into Given/When/Then fragments plus a stray tier-tag node (G-10)."""
    text = ("- **AC-1.5** — **Given** a list item, **when** ingested, **then** it is a block and its "
            "parent is recorded. → *unit.*")
    given, then, tier = "a list item", "it is a block and its parent is recorded", "unit"
    draft, backend = run([block("B-000001", text, kind="list_item")], [
        {"blocks": [{"block_id": "B-000001",
                     "sentences": [{"quote": text, "role": "verification"}],
                     "atoms": [{"kind": "requirement", "quotes": [given]},
                               {"kind": "requirement", "quotes": [then]},
                               {"kind": "verification", "quotes": [tier]}]}]},
        q_desc(q_desc_entry("B-000001#1", subject="a list item", response="is a block, its parent recorded",
                            q_yes={}, modality=None, verifies_text="list-item ingest",
                            terms=[{"name": "list item", "kind": "data", "role": "subject", "quote": "list item"}])),
    ])
    [node] = draft.nodes.values()
    assert node["id"] == "AC-1.5" and node["label"] == "AC-1.5"
    assert (node["kind"], node["layer"]) == ("verification", "V")
    assert [q.payload["atom_ids"] for q in backend.asked if q.kind == "q-desc"] == [["B-000001#1"]]


def test_r16_a_rationale_quote_that_is_not_verbatim_drops_the_annotation_not_the_run():
    """R16 (I-67): a run died after every model call was paid for. Q-ATOM had merged two source
    sentences into one `rationale` quote; `block_annotations` located quotes with a guard that
    raises, outside the re-ask path, so one decoration killed a $1.20 compile. An annotation is
    context, never a claim: an unlocatable one is dropped and counted (F3 D35)."""
    text = f"{EXPIRY} *Rejected:* a shorter life. That would break sharing."
    draft, _ = run([block("B-000001", text)], [
        {"blocks": [{"block_id": "B-000001",
                     "sentences": [{"quote": EXPIRY, "role": "requirement"},
                                   {"quote": "a shorter life would break sharing", "role": "rationale"},
                                   {"quote": "That would break sharing.", "role": "rationale"}],
                     "atoms": [{"kind": "requirement", "quotes": [EXPIRY]}]}]},
        q_desc(q_desc_entry("B-000001#1")),
    ])
    [node] = draft.nodes.values()
    assert [a["text"] for a in node["annotations"]] == ["That would break sharing."]
    assert draft.annotations_dropped == [
        {"block": "B-000001", "file": "sdd/specs/F9_demo/spec.md", "lines": [3, 3],
         "role": "rationale", "quote": "a shorter life would break sharing"}]


def test_r15_a_table_row_becomes_one_claim():
    """R15 (I-64): F5's S3 row came back as three atoms, one per cell — "A `C` node whose
    `scope_selector` covers the other node", "by the rule of D9", "the selector that matched" —
    so a rule became three fragment nodes in three families. A row is one rule (F3 D34)."""
    row = "| **S3 constraint scope** | A `C` node whose selector covers the other node | the selector |"
    cells = ["A `C` node whose selector covers the other node", "the selector"]
    draft, backend = run([block("B-000001", row, kind="table_row")], [
        {"blocks": [{"block_id": "B-000001",
                     "sentences": [{"quote": row, "role": "requirement"}],
                     "atoms": [{"kind": "requirement", "quotes": [cells[0]]},
                               {"kind": "requirement", "quotes": [cells[1]]}]}]},
        q_desc(q_desc_entry("B-000001#1", subject="candidate", response="covers the other node", q_yes={},
                            terms=[{"name": "candidate", "kind": "data", "role": "subject",
                                    "quote": "covers"}])),
    ])
    [node] = draft.nodes.values()
    assert node["label"] == "S3"
    assert node["text"] == " … ".join(cells)                 # both cells, in row order
    assert [q.payload["atom_ids"] for q in backend.asked if q.kind == "q-desc"] == [["B-000001#1"]]


# -- R13, R14 (after R6) --------------------------------------------------------------------

def test_r14_a_reversed_narrower_is_refused_and_re_asked():
    """R6: "backend" was judged narrower than "claude code backend" — backwards."""
    from sdd_compiler.atomize.terms import resolve_terms
    registry = {"term:claude_code_backend": {"id": "term:claude_code_backend", "canonical": "claude code backend",
                                             "aliases": [], "kind": "component", "definition": None, "defined_by": None,
                                             "status": "proposed", "broader": None}}
    reversed_ = {"terms": [{"term_key": "term:backend", "verdict": "narrower",
                            "target": "term:claude_code_backend", "reason": "r"}]}
    fixed = {"terms": [{"term_key": "term:backend", "verdict": "different", "target": None, "reason": "r"}]}
    backend = FakeBackend([reversed_, fixed])
    result = resolve_terms([{"name": "backend", "kind": "component"}], registry, backend)
    assert len(backend.asked) == 2
    assert "broader" in backend.asked[1].prompt
    assert result.new_terms["term:backend"]["broader"] is None


def test_r14_the_prompt_says_which_way_narrower_points():
    from sdd_compiler.atomize.terms import build_question
    prompt = build_question([], None).prompt
    assert "specific" in prompt and "general" in prompt


def test_r13_the_description_question_resolves_references_before_flagging():
    from sdd_compiler.atomize.describe import build_question
    prompt = build_question([], None).prompt
    assert "resolve" in prompt.lower() and "only when" in prompt.lower()


# -- F3 D41, F2 D22: an example becomes a verification node (AC-3.40, AC-2.30) ---------------

RULE = "The default metavar is the type name in uppercase."
EXAMPLE = "For example, an integer option appears as COUNT."
FLAG = "A flag has no metavar."


def metavar_answers(block_id, sentences, atoms):
    metavar = [{"name": "metavar", "kind": "data", "role": "subject", "quote": "metavar"}]
    return [
        {"blocks": [{"block_id": block_id,
                     "sentences": [{"quote": q, "role": r} for q, r in sentences],
                     "atoms": [{"kind": "requirement", "quotes": [q]} for q in atoms]}]},
        q_desc(*[q_desc_entry(f"{block_id}#{n}", subject="metavar", response="hold", q_yes={"Q3": q},
                              terms=metavar) for n, q in enumerate(atoms, start=1)]),
    ]


def test_ac_3_40_ac_2_30_an_example_becomes_a_verification_node_of_the_claim_before_it():
    """Round 14 (rel02): "for example, an integer option `--count` appears as `--count COUNT`" sat
    in the bullet of "the default metavar is the type name in uppercase", contradicting it. As an
    annotation the example was never compared with anything (F2 §4.1), so the compiler could not
    report it. Formed in code: the fake backend has no answer left for a third call."""
    text = f"{RULE} {EXAMPLE} {FLAG}"
    draft, backend = run([block("B-000001", text)], metavar_answers(
        "B-000001", [(RULE, "requirement"), (EXAMPLE, "example"), (FLAG, "requirement")], [RULE, FLAG]))
    assert [q.kind for q in backend.asked] == ["q-atom", "q-desc"]

    by_text = {n["text"]: n for n in draft.nodes.values()}
    assert sorted(by_text) == sorted([RULE, EXAMPLE, FLAG])
    example, rule = by_text[EXAMPLE], by_text[RULE]
    for node in draft.nodes.values():
        validate("node", node)
    assert (example["kind"], example["layer"]) == ("verification", "V")
    assert example["verifies"] == [rule["id"]]
    assert example["family"] == rule["family"] == "term:metavar"
    assert example["canonical"]["subject"] == "metavar" and example["canonical"]["response"] == EXAMPLE
    assert example["source"]["spans"] == [[text.index(EXAMPLE), text.index(EXAMPLE) + len(EXAMPLE)]]
    assert example["judgments"] == rule["judgments"] and example["terms"] == []
    assert not [a for n in draft.nodes.values() for a in n["annotations"] if a["role"] == "example"]
    assert ("verifies", rule["id"]) in {(l["type"], l["to"]) for l in draft.links if l["from"] == example["id"]}


def test_ac_3_40_an_example_that_comes_first_verifies_the_first_claim():
    text = f"{EXAMPLE} {RULE} {FLAG}"
    draft, _ = run([block("B-000001", text)], metavar_answers(
        "B-000001", [(EXAMPLE, "example"), (RULE, "requirement"), (FLAG, "requirement")], [RULE, FLAG]))
    by_text = {n["text"]: n for n in draft.nodes.values()}
    assert by_text[EXAMPLE]["verifies"] == [by_text[RULE]["id"]]


def test_ac_2_30_an_example_in_a_block_with_no_claim_forms_no_node():
    text = f"Some background. {EXAMPLE}"
    draft, backend = run([block("B-000001", text)], [
        {"blocks": [{"block_id": "B-000001",
                     "sentences": [{"quote": "Some background.", "role": "context"},
                                   {"quote": EXAMPLE, "role": "example"}],
                     "atoms": []}]},
    ])
    assert draft.nodes == {}
    assert draft.completed == {"B-000001": "sha256:B-000001"}
    assert [q.kind for q in backend.asked] == ["q-atom"]

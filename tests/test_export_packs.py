"""F7 §4.5 — the unit pack: Text with tags, then the lists.

Covers AC-7.14, AC-7.15, AC-7.21, AC-7.22 and the rendering halves of AC-7.11 … AC-7.13.
Tier: unit.
"""
from __future__ import annotations

from export_helpers import b, conflict, link, make_store, n, term
from sdd_compiler.export.model import load_model
from sdd_compiler.export.packs import build_packs

A, B = "sdd/specs/a.md", "sdd/specs/b.md"
SECTIONS = ("## Text", "## Claims to implement", "## Acceptance criteria", "## Constraints in scope",
            "## Related elsewhere", "## Conflicts", "## Terms")


def packs(tmp_path, blocks, nodes=(), allow_open=False, **kwargs):
    model = load_model(make_store(tmp_path, blocks, nodes, **kwargs))
    return build_packs(model, allow_open=allow_open)


def pack_for(result, source, fragment=""):
    for name, text in result.files.items():
        if f"— {source} ·" in text.splitlines()[0] and fragment in text.splitlines()[0]:
            return text
    raise AssertionError(f"no pack for {source}: {list(result.files)}")


def test_sections_appear_in_order_and_empty_ones_say_none(tmp_path):
    result = packs(tmp_path, [b("B-1", A, ("T", "S"))])
    text = pack_for(result, A)
    positions = [text.index(s) for s in SECTIONS]
    assert positions == sorted(positions)
    assert text.count("None.") == 6                                  # all but Text


def test_text_is_verbatim_with_tags_and_headings_re_emitted(tmp_path):
    blocks = [b("B-1", A, ("T", "S"), 1, "A link MUST expire."),
              b("B-2", A, ("T", "S", "Sub"), 3, "Pending words."),
              b("B-3", A, ("T", "S", "Sub"), 5, "No node here.", atomized_hash="sha256:x")]
    blocks[1]["atomized_hash"] = None                                # pending
    nodes = [n("N-000001", "B-1", modality="MUST", layer="L1", label="D5")]
    text = pack_for(packs(tmp_path, blocks, nodes), A)
    assert "A link MUST expire.\n↳ N-000001 requirement · MUST · L1 · D5\n" in text
    assert "### Sub\n" in text and text.count("### Sub") == 1
    assert "Pending words.\n↳ no node (pending)\n" in text
    assert "No node here.\n↳ no node\n" in text


def test_ac_7_15_a_table_renders_once_with_one_tag_line_per_row(tmp_path):
    head = "| ID | What |"
    blocks = [b("B-1", A, ("T", "S"), 1, "| 1 | one |", kind="table_row", table_header=head),
              b("B-2", A, ("T", "S"), 2, "| 2 | two |", kind="table_row", table_header=head),
              b("B-3", A, ("T", "S"), 3, "| 3 | three |", kind="table_row", table_header=head),
              b("B-4", A, ("T", "S"), 4, "```json\n{\"a\": 1}\n```", kind="code")]
    nodes = [n("N-000001", "B-2")]
    text = pack_for(packs(tmp_path, blocks, nodes), A)
    assert text.count(head) == 1
    assert "| ID | What |\n| --- | --- |\n| 1 | one |\n| 2 | two |\n| 3 | three |\n" in text
    assert "↳ row 1: no node\n↳ row 2: N-000001 requirement · MUST · L3\n↳ row 3: no node\n" in text
    assert "```json\n{\"a\": 1}\n```\n↳ no node\n" in text


def test_claims_list_needs_with_pack_numbers_and_decisions(tmp_path):
    blocks = [b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S"))]
    nodes = [n("N-000001", "B-1", text="First claim.", modality=None),
             n("N-000002", "B-2", text="Chosen one.", kind="decision",
               decision={"chosen": "use X", "rejected": [{"option": "Y", "reason": "slow"}],
                         "affects": []})]
    links = [link("N-000001", "depends_on", "N-000002")]
    result = packs(tmp_path, blocks, nodes, links=links)
    a = pack_for(result, A)
    assert "- [N-000001] requirement · — · L3 — First claim.\n  needs: N-000002 (pack 01)\n" in a
    bpack = pack_for(result, B)
    assert "- [N-000002] decision · MUST · L3 — Chosen one.\n  needs: none\n" in bpack
    assert "  chosen: use X\n  rejected: Y — slow\n" in bpack


def test_acceptance_criteria_name_tests(tmp_path):
    blocks = [b("B-1", A, ("T", "S")), b("B-2", A, ("T", "S"), 3)]
    nodes = [n("N-000001", "B-1"),
             n("AC-4.7", "B-2", kind="verification", layer="V", label="AC-4.7", text="Given x.")]
    links = [link("AC-4.7", "verifies", "N-000001")]
    text = pack_for(packs(tmp_path, blocks, nodes, links=links), A)
    assert "- [AC-4.7] Given x.\n  verifies: N-000001\n  test name: test_AC_4_7_…\n" in text
    assert "AC-4.7 requirement" not in text.split("## Claims to implement")[1].split("##")[0]


def test_ac_7_14_constraints_in_scope_and_broad_constraints(tmp_path):
    blocks = [b("B-0", "sdd/specs/vision.md", ("V",)), b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S"))]
    named = {"families": ["term:a"], "layers": [], "terms": [], "categories": []}
    empty = {"families": [], "layers": [], "terms": [], "categories": []}
    layers = {"families": [], "layers": ["L3"], "terms": [], "categories": []}
    nodes = [n("N-000001", "B-1", family="term:a"),
             n("N-000002", "B-2", layer="C", text="Covers a.", scope_selector=named, family="term:c"),
             n("N-000003", "B-2", layer="C", text="Applies everywhere.", scope_selector=empty,
               family="term:c"),
             n("N-000004", "B-2", layer="C", text="Every L3 thing.", scope_selector=layers,
               family="term:c", keywords=["thing"])]
    result = packs(tmp_path, blocks, nodes)
    a = pack_for(result, A)
    section = a.split("## Constraints in scope")[1].split("## Related")[0]
    assert "- [N-000002] (pack 02) Covers a." in section
    assert "Applies everywhere." not in section and "Every L3 thing." not in section
    assert "plus the broad constraints in pack 00" in section
    foundation = result.files["packs/00-foundation.md"].split("## Constraints in scope")[1]
    assert "- [N-000003] (pack 02) Applies everywhere." in foundation
    assert "- [N-000004] (pack 02) layers L3 — Every L3 thing." in foundation


def test_ac_7_21_a_contract_prints_its_fence_once_and_a_lead_line_elsewhere(tmp_path):
    fence = '```json\n{"id": 1}\n```'
    lead = "**CT-1.1 — Block record** (what a block is)"
    blocks = [b("B-1", A, ("T", "5. Contracts"), 1, lead), b("B-2", A, ("T", "5. Contracts"), 3, fence, kind="code")]
    nodes = [n("CT-1.1", "B-2", text=fence, layer="C", label="CT-1.1")]
    text = pack_for(packs(tmp_path, blocks, nodes), A)
    assert text.count('{"id": 1}') == 1
    assert f"- [CT-1.1] contract · C — {lead} (fence in Text)" in text


def test_ac_7_22_terms_listed_only_with_a_definition_or_aliases(tmp_path):
    blocks = [b("B-1", A, ("T", "S"))]
    used = [{"term": t, "role": "subject", "quote": "x"} for t in ("term:link", "term:alias", "term:plain")]
    nodes = [n("N-000001", "B-1", terms=used)]
    terms = [term("term:link", "A link is a URL.", aliases=["url", "address"]),
             term("term:alias", aliases=["nick"]), term("term:plain")]
    section = pack_for(packs(tmp_path, blocks, nodes, terms=terms), A).split("## Terms")[1]
    assert '- link (aliases: address, url) — defined: "A link is a URL."' in section
    assert "- alias (aliases: nick)\n" in section
    assert "plain" not in section


def test_ac_7_24_judged_links_are_ids_only_and_duplicates_keep_text(tmp_path):
    blocks = [b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S")), b("B-3", B, ("T", "S"), 3)]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2", text="Refined claim."),
             n("N-000003", "B-3", text="Twin text.")]
    links = [link("N-000001", "refines", "N-000002"), link("N-000001", "duplicates", "N-000003")]
    related = pack_for(packs(tmp_path, blocks, nodes, links=links), A) \
        .split("## Related elsewhere")[1].split("## Conflicts")[0]
    assert "- N-000001 refines N-000002 (pack 02)\n" in related
    assert "Refined claim." not in related
    assert "- N-000001 duplicates N-000003 (pack 02) Twin text." in related


def test_ac_7_13_a_duplication_is_same_as_not_a_conflict(tmp_path):
    blocks = [b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S"))]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2", text="Twin claim.")]
    result = packs(tmp_path, blocks, nodes, conflicts=[conflict("CF-000001", "duplication",
                                                                ["N-000001", "N-000002"])])
    a = pack_for(result, A)
    related = a.split("## Related elsewhere")[1].split("## Conflicts")[0]
    assert "- N-000001 same as N-000002 (pack 02) Twin claim." in related
    assert a.split("## Conflicts")[1].split("## Terms")[0].strip() == "None."


def test_ac_7_12_settled_unsettled_and_dismissed_contradictions(tmp_path):
    blocks = [b("B-1", A, ("T", "S")), b("B-2", B, ("T", "S"))]
    nodes = [n("N-000001", "B-1"), n("N-000002", "B-2"), n("N-000003", "B-2")]
    conflicts = [conflict("CF-000001", "contradiction", ["N-000001", "N-000002"]),
                 conflict("CF-000002", "contradiction", ["N-000001", "N-000003"]),
                 conflict("CF-000003", "contradiction", ["N-000002", "N-000003"])]
    verdicts = [("CF-000001", "real", "A holds."), ("CF-000002", "false", None)]
    result = packs(tmp_path, blocks, nodes, conflicts=conflicts, verdicts=verdicts, allow_open=True)
    for source in (A, B):
        section = pack_for(result, source).split("## Conflicts")[1].split("## Terms")[0]
        if source == A:
            assert "Settled: CF-000001" in section and "adjudication: A holds." in section
            assert "CF-000002" not in section and "UNSETTLED" not in section
        else:
            assert "Settled: CF-000001" in section
            assert "UNSETTLED: CF-000003" in section and "CF-000002" not in section
            assert 'N-000002 "quote of N-000002"' in section and "rationale: the rationale" in section

"""T19 — G4 §4: a human verdict per reported conflict, kept across runs (F6 AC-6.20).

Without this there is no M2 (precision): "how many reported conflicts a human judged real" is the
one number the 30 September close is about, and it cannot be reconstructed afterwards.

Tier: unit, contract.
"""
from __future__ import annotations

import json

import pytest

from sdd_compiler import commands
from sdd_compiler.conflicts.adjudicate import adjudications, record_adjudication, verdicts_for
from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.llm import FakeBackend
from sdd_compiler.pipeline import compile_graph
from sdd_compiler.store.graph import load_graph
from test_compile import EXPIRY, REVOKE, atom_answer, desc


def contradiction(rationale="one demands expiry, the other revocation at will"):
    return {"relation": "contradicts", "direction": "symmetric", "rationale": rationale,
            "quotes": {"a": "share link", "b": "share link"}, "confidence": "high"}


@pytest.fixture()
def compiled(tmp_path):
    spec = tmp_path / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\n{REVOKE}\n", encoding="utf-8")
    commands.init(tmp_path)
    compile_graph(tmp_path, backend=FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"),
                   desc("B-000002#1", REVOKE, "be revocable")]},
        contradiction(),
    ]))
    return tmp_path


def test_ac_6_20_a_verdict_is_recorded_with_what_it_judged(compiled):
    store = compiled / ".sdd"
    record = record_adjudication(store, "CF-000001", "real", note="the two rules cannot both hold",
                                 date="2026-09-21")
    assert record["id"] == "ADJ-000001"
    assert record["conflict"] == "CF-000001"
    assert record["verdict"] == "real"
    assert record["note"] == "the two rules cannot both hold"
    assert record["members"] == ["N-000001", "N-000002"]
    assert record["judgment"] == load_graph(store).conflicts["CF-000001"]["judgment"]
    assert record["date"] == "2026-09-21"

    [stored] = adjudications(store)
    assert stored == record
    assert (store / "adjudications.jsonl").read_text(encoding="utf-8").endswith("\n")


def test_a_second_verdict_is_appended_and_the_latest_one_counts(compiled):
    store = compiled / ".sdd"
    record_adjudication(store, "CF-000001", "real", date="2026-09-21")
    second = record_adjudication(store, "CF-000001", "false", note="on reflection, different scopes",
                                 date="2026-09-22")
    assert second["id"] == "ADJ-000002"
    assert len(adjudications(store)) == 2                      # history is kept, never rewritten
    assert verdicts_for(store)["CF-000001"]["verdict"] == "false"


def test_a_verdict_goes_stale_when_the_model_judges_the_pair_again(compiled):
    """F6 D14: an adjudication is about one model verdict. When the pair is judged again — an edit,
    `--no-replay` — the human's answer was about the old one, and M2 must not count it as fresh."""
    store = compiled / ".sdd"
    record_adjudication(store, "CF-000001", "real", date="2026-09-21")
    assert verdicts_for(store)["CF-000001"]["stale"] is False

    spec = compiled / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\nA share link must be revocable by its owner.\n",
                    encoding="utf-8")
    revoke = "A share link must be revocable by its owner."
    compile_graph(compiled, backend=FakeBackend([
        atom_answer(("B-000002", revoke)),
        {"atoms": [desc("B-000002#1", revoke, "be revocable by its owner")]},
        contradiction("still the same disagreement"),
    ]))
    state = verdicts_for(store)["CF-000001"]
    assert state["verdict"] == "real" and state["stale"] is True


def test_an_unknown_conflict_is_an_input_error(compiled):
    with pytest.raises(SddcError) as error:
        record_adjudication(compiled / ".sdd", "CF-000999", "real")
    assert error.value.exit_code == ExitCode.INPUT
    assert "CF-000999" in str(error.value)


def test_a_verdict_must_be_real_or_false(compiled):
    with pytest.raises(SddcError) as error:
        record_adjudication(compiled / ".sdd", "CF-000001", "maybe")
    assert error.value.exit_code == ExitCode.USAGE


# -- the command (G4 §4) ------------------------------------------------------------------

def test_sddc_conflicts_judge_records_and_reports(compiled, capsys):
    code = commands.conflicts(compiled, judge="CF-000001", verdict="real", note="both cannot hold")
    out = capsys.readouterr().out
    assert code == ExitCode.OK
    assert "CF-000001" in out and "real" in out
    assert [a["verdict"] for a in adjudications(compiled / ".sdd")] == ["real"]


def test_sddc_conflicts_shows_what_a_human_has_judged(compiled, capsys):
    commands.conflicts(compiled, judge="CF-000001", verdict="false", note="different scopes")
    capsys.readouterr()
    commands.conflicts(compiled, as_json=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["conflicts"][0]["adjudication"] == {"verdict": "false", "stale": False,
                                                       "note": "different scopes"}
    commands.conflicts(compiled)
    assert "judged false" in capsys.readouterr().out


def test_the_precision_numbers_are_countable_from_the_file(compiled):
    """M2 is "of the conflicts reported, how many a human agrees are real" — one line of counting."""
    store = compiled / ".sdd"
    record_adjudication(store, "CF-000001", "real", date="2026-09-21")
    judged = verdicts_for(store)
    assert sum(1 for v in judged.values() if v["verdict"] == "real" and not v["stale"]) == 1
    assert len(load_graph(store).conflicts) == 1

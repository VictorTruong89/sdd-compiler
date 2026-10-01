"""A fake backend that answers any question shape from the store's own blocks — enough to compile a
whole fixture repository with no model (F7 AC-7.20). Every atom is its whole block; every pair is
`none`, except the first pair asked, which is a contradiction."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sdd_compiler.llm import FakeBackend
from sdd_compiler.llm.base import Answer, Question

NO = {"answer": "no", "quote": None}


class SmartFake(FakeBackend):
    def __init__(self, root: Path) -> None:
        super().__init__([])
        self.root = Path(root)
        self.contradicted = False

    def _blocks(self) -> dict[str, dict[str, Any]]:
        lines = (self.root / ".sdd" / "blocks.jsonl").read_text().splitlines()
        return {r["id"]: r for r in map(json.loads, lines)}

    def ask(self, question: Question) -> Answer:
        self.asked.append(question)
        return Answer(data=getattr(self, "_" + question.kind.replace("-", "_"))(question),
                      backend="fake", model="fake")

    def _q_atom(self, q: Question) -> dict[str, Any]:
        blocks = self._blocks()
        return {"blocks": [{"block_id": i, "sentences": [{"quote": blocks[i]["text"], "role": "requirement"}],
                            "atoms": [{"kind": "requirement", "quotes": [blocks[i]["text"]]}]}
                           for i in q.payload["block_ids"]]}

    def _q_desc(self, q: Question) -> dict[str, Any]:
        blocks = self._blocks()
        atoms = []
        for atom_id in q.payload["atom_ids"]:
            text = blocks[atom_id.split("#")[0]]["text"]
            words = re.findall(r"[A-Za-z]{4,}", text)
            name = words[0].lower() if words else "thing"
            answers = {f"Q{n}": dict(NO) for n in range(1, 8)}
            answers["Q3"] = {"answer": "yes", "quote": text}
            atoms.append({"atom_id": atom_id,
                          "canonical": {"state": None, "trigger": None, "scope": None,
                                        "subject": name, "modality": "MUST", "response": "hold"},
                          "layer_answers": answers,
                          "terms": [{"name": name, "kind": "entity", "role": "subject", "quote": words[0]}]
                          if words else [],
                          "ambiguity": [], "scope_layers": [], "scope_description": None,
                          "verifies_text": None, "decision": None})
        return {"atoms": atoms}

    def _q_pair(self, q: Question) -> dict[str, Any]:
        pairs = []
        for pair_id in q.payload.get("pair_ids", []):
            quotes = {side: self._first_line(q.prompt, pair_id, node) for side, node
                      in zip("ab", pair_id.split("|"))}
            relation = "none" if self.contradicted else "contradicts"
            self.contradicted = True
            pairs.append({"pair_id": pair_id, "relation": relation, "direction": "symmetric",
                          "rationale": "the claims disagree" if relation != "none" else "independent",
                          "quotes": quotes, "confidence": "high"})
        return {"pairs": pairs}

    @staticmethod
    def _first_line(prompt: str, pair_id: str, node: str) -> str:
        """The first line of a claim's text in this pair's section of the prompt."""
        section = prompt.split(f"=== PAIR {pair_id} ===", 1)[1]
        body = section.split(f"--- CLAIM", 3)
        for part in body:
            if part.lstrip().startswith(("A: " + node, "B: " + node)):
                return part.split("text:\n", 1)[1].split("\n", 1)[0]
        raise AssertionError(f"{node} not in pair {pair_id}")

    def _q_term(self, q: Question) -> dict[str, Any]:
        return {"terms": [{"term_key": key, "verdict": "different", "target": None,
                           "reason": "a different thing"} for key in q.payload["term_keys"]]}

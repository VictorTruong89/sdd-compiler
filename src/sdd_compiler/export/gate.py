"""F7 §4.6 — the conflict gate and what each open conflict becomes in a pack."""
from __future__ import annotations

from typing import Any

from ..errors import ExitCode, SddcError
from .model import Model

#: settled / unsettled: contradictions · same_as / covered_by: kept as related text ·
#: excluded: a real duplicate, handled by excluding a block · dismissed: judged false.
CLASSES = ("settled", "unsettled", "same_as", "covered_by", "excluded", "dismissed")


def classify(model: Model, record: dict[str, Any]) -> str:
    verdict = model.verdicts.get(record["id"])
    current = verdict["verdict"] if verdict and not verdict["stale"] else None
    kind = record["kind"]
    if kind == "contradiction":
        return {"real": "settled", "false": "dismissed"}.get(current, "unsettled")
    if kind in ("duplication", "subsumption"):
        if current == "false":
            return "dismissed"
        if kind == "duplication":
            return "excluded" if current == "real" else "same_as"
        return "covered_by"
    raise SddcError(f"{record['id']} is an open {kind!r} conflict, which F7 does not know how to "
                    f"present", ExitCode.STORE)


def blocking(model: Model) -> list[dict[str, Any]]:
    """Open contradictions with no current human verdict (D4)."""
    return [c for c in model.open_conflicts() if classify(model, c) == "unsettled"]


def excluded_blocks(model: Model) -> dict[str, str]:
    return model.excluded

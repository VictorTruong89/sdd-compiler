"""F2 §5 — record contracts, checked before anything is written (F2 T3).

JSON Schema catches shape: missing fields, unknown enum values, wrong types.
The rules a schema cannot express are checked after it:

- a node's stored `status` equals `derive_status` of its facts (AC-2.14);
- `scope_selector` only on a `C` node, `verifies` only on a `V` node,
  `decision` only on a decision (AC-2.18);
- a null modality only where no obligation is stated, or with ambiguity
  `missing_modality` (F3 D14);
- a `judgment` link carries its judgment id and rationale (CT-2.3);
- a conflict record's members are at least two, sorted and distinct (CT-2.4).

Every rejection names the field, so a failed write says what to fix.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from .layers import LAYERS, QUESTIONS
from .status import derive_status

NODE_KINDS = ("requirement", "constraint", "assumption", "verification", "decision")
MODALITIES = ("MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY")
AMBIGUITY_KINDS = (
    "vague_term", "unbounded_quantity", "missing_actor", "missing_modality", "mixed_layers", "referential",
    "scope", "unresolved_term", "unplaceable", "inferred", "pending_review",
    "low_confidence_verdict",        # F6 CT-6.1: a judged verdict the model was unsure of
)
FAMILY_RULES = ("subject", "response", "verification", "constraint", "mention", "component", "pinned", "fallback")  # F2 D19: component
FLAGS = ("inferred", "pinned_family", "allocation_proposed", "family_disputed")
STATUSES = ("unchecked", "validated", "conflict", "ambiguous", "stale")
TERM_KINDS = ("entity", "data", "event", "actor", "component", "external_system",
              "category", "external_reference")
TERM_ROLES = ("subject", "response", "trigger", "state", "scope")
LINK_TYPES = ("uses_term", "refines", "allocated_to", "constrains", "verifies", "depends_on",
              "duplicates", "subsumes", "conflicts_with", "decides")
CONFLICT_KINDS = ("contradiction", "duplication", "subsumption", "ambiguity")

_STR = {"type": "string"}
_NSTR = {"type": ["string", "null"]}
_STRS = {"type": "array", "items": _STR}
_SPAN = {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}


def _obj(properties: dict[str, Any], optional: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [key for key in properties if key not in optional],
        "properties": properties,
    }


def _enum(values: tuple[str, ...], nullable: bool = False) -> dict[str, Any]:
    if nullable:
        return {"type": ["string", "null"], "enum": [*values, None]}
    return {"type": "string", "enum": list(values)}


_NUMBER = {"type": "number"}

NODE_SCHEMA = _obj({
    "id": {"type": "string", "pattern": r"^(N-\d{6,}|AC-\d+\.\d+|CT-\d+\.\d+)$"},
    "kind": _enum(NODE_KINDS),
    "source": _obj({"file": _STR, "block_id": _STR, "heading_path": _STRS, "lines": _SPAN,
                    "spans": {"type": "array", "items": _SPAN, "minItems": 1}}),
    "text": _STR,
    "canonical": _obj({
        "state": _NSTR, "trigger": _NSTR, "scope": _NSTR, "subject": _STR,
        "modality": _enum(MODALITIES, nullable=True), "response": _STR,
        "quantities": {"type": "array", "items": _obj({
            "value": _NUMBER, "unit": _STR, "quote": _STR,
            "normalized": {"oneOf": [{"type": "null"}, _obj({"value": _NUMBER, "unit": _STR})]},
        })},
    }),
    "terms": {"type": "array", "items": _obj({
        "term": {"type": "string", "pattern": r"^term:"}, "role": _enum(TERM_ROLES), "quote": _STR,
    })},
    "label": {"type": ["string", "null"], "pattern": r"^((AC|CT)-\d+\.\d+|[A-Z]{1,2}\d{1,3})$"},  # F2 D20
    "primary_term": _NSTR,
    "layer": _enum(tuple(LAYERS), nullable=True),
    "layer_answers": {
        "type": "object", "propertyNames": {"enum": list(QUESTIONS)},
        "additionalProperties": _obj({"answer": _enum(("yes", "no")), "quote": _NSTR}),
    },
    "layer_hint": _NSTR,
    "family": {"type": ["string", "null"], "pattern": r"^(term:.+|\(global\))$"},
    "family_rule": _enum(FAMILY_RULES),
    "components": _STRS,
    "scope_selector": {"oneOf": [{"type": "null"}, _obj({
        "families": _STRS, "layers": _STRS, "terms": _STRS, "categories": _STRS})]},
    "verifies": {"oneOf": [{"type": "null"}, _STRS]},
    "decision": {"oneOf": [{"type": "null"}, _obj({
        "chosen": _STR,
        "rejected": {"type": "array", "items": _obj({"option": _STR, "reason": _STR})},
        "affects": _STRS,
    })]},
    "annotations": {"type": "array", "items": _obj({
        "role": _enum(("rationale", "example")), "text": _STR,
        "spans": {"type": "array", "items": _SPAN}})},
    "keywords": _STRS,
    "ambiguity": {"type": "array", "items": _obj({
        "kind": _enum(AMBIGUITY_KINDS), "quote": _NSTR, "detail": _STR})},
    "conflict_ids": {"type": "array", "items": {"type": "string", "pattern": r"^CF-\d{6,}$"}},
    "related_conflict_nodes": _STRS,
    "stale_reasons": {"type": "array", "items": _obj({
        "link": {"type": "array", "items": _STR, "minItems": 3, "maxItems": 3},
        "since_run": _STR})},
    "last_checked_run": _NSTR,
    "flags": {"type": "array", "items": _enum(FLAGS)},
    "status": _enum(STATUSES),
    "judgments": _STRS,
})

TERM_SCHEMA = _obj({
    "id": {"type": "string", "pattern": r"^term:[a-z0-9_]+$"},
    "canonical": _STR, "aliases": _STRS, "kind": _enum(TERM_KINDS),
    "defined_by": _NSTR, "status": _enum(("confirmed", "proposed")),
    "broader": {"type": ["string", "null"], "pattern": r"^term:"},   # F2 D16: "a kind of"
})

LINK_SCHEMA = _obj({
    "from": _STR, "type": _enum(LINK_TYPES), "to": _STR,
    "provenance": _enum(("code", "judgment")), "judgment": _NSTR, "rationale": _NSTR,
    "quotes": _STRS,
})

CONFLICT_SCHEMA = _obj({
    "id": {"type": "string", "pattern": r"^CF-\d{6,}$"},
    "kind": _enum(CONFLICT_KINDS),
    "members": {"type": "array", "items": _STR, "minItems": 2},
    "rationale": _STR,
    "quotes": {"type": "object", "additionalProperties": _STR},
    "state": _enum(("open", "resolved")),
    "resolved_reason": _enum(("fixed", "member_deleted"), nullable=True),
    "detected_run": _STR, "resolved_run": _NSTR, "judgment": _STR,
})

SCHEMAS = {"node": NODE_SCHEMA, "term": TERM_SCHEMA, "link": LINK_SCHEMA,
           "conflict": CONFLICT_SCHEMA}
_VALIDATORS = {kind: Draft202012Validator(schema) for kind, schema in SCHEMAS.items()}


class RecordError(ValueError):
    """A record breaks its contract. The message names the record and the field."""


def validate(kind: str, record: Mapping[str, Any]) -> None:
    label = f"{kind} {record.get('id') or record.get('from') or '?'}"
    # `best_match` descends into `oneOf` branches, so a nullable object reports the
    # field inside it that failed rather than "not valid under any of the given schemas".
    first = best_match(_VALIDATORS[kind].iter_errors(record))
    if first is not None:
        where = "/".join(str(part) for part in first.absolute_path) or "<record>"
        raise RecordError(f"{label}: {where}: {first.message}")
    {"node": _node_rules, "link": _link_rules, "conflict": _conflict_rules}.get(
        kind, lambda _record, _label: None
    )(record, label)


def _node_rules(node: Mapping[str, Any], label: str) -> None:
    derived = derive_status(node)
    if node["status"] != derived:
        raise RecordError(
            f"{label}: status: stored {node['status']!r} but its facts derive {derived!r}"
        )
    if node["scope_selector"] is not None and node["layer"] != "C":
        raise RecordError(f"{label}: scope_selector is allowed only on a C node")
    if node["verifies"] is not None and node["layer"] != "V":
        raise RecordError(f"{label}: verifies is allowed only on a V node")
    if node["decision"] is not None and node["kind"] != "decision":
        raise RecordError(f"{label}: decision is allowed only on a decision node")
    if node["kind"] == "decision" and node["decision"] is None:
        raise RecordError(f"{label}: decision: a decision node needs chosen and rejected options")
    if (
        node["canonical"]["modality"] is None
        and node["kind"] in ("requirement", "constraint")
        and not any(entry["kind"] == "missing_modality" for entry in node["ambiguity"])
    ):
        raise RecordError(
            f"{label}: canonical/modality: null on a {node['kind']} without ambiguity "
            f"missing_modality (F3 D14)"
        )


def _link_rules(link: Mapping[str, Any], label: str) -> None:
    if link["provenance"] == "judgment" and not (link["judgment"] and link["rationale"]):
        raise RecordError(f"{label}: judgment: a judged link needs its judgment id and rationale")


def _conflict_rules(record: Mapping[str, Any], label: str) -> None:
    members = list(record["members"])
    if members != sorted(set(members)):
        raise RecordError(f"{label}: members must be sorted and distinct")

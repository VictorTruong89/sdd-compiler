"""Q-DESC — one atom in, its description out (F3 §4.2, §4.4; P-4, P-8).

The model supplies what needs language judgment: the canonical fields, the
answers to the seven layer questions, term tags, and ambiguity it notices. Code
supplies everything that can be computed, and checks the rest:

- **G5** the answer matches `q-desc/1` — else re-ask;
- **G2** every quote is anchored in the block by code — else re-ask. A `yes`
  layer answer must carry a quote, because placement (F2 §4.3) compares quote
  offsets to decide between layers;
- **G4 no injection** — a term, or any value containing a digit, that appears in
  the canonical fields but nowhere in the source marks the description
  `inferred`. A fact, not a failure: the node is written and flagged for review;
- **G6 weak words** — `profile.weak_words` in the quotes add `vague_term`;
- **quantities** are parsed from the quotes by `quantities.py`, never taken
  from the model; a vague amount adds `unbounded_quantity`.

G4's source (F3 D13): the atom's block **and its heading
path**, not only the atom's own quotes. Measured on 17 real atoms, the narrow
reading flagged 8, and every one was context resolution ("here" → "F1" from the
heading, a spec id from the next sentence), not invention (rel01 S21). A term
counts as present when its quote is anchored in the block, or its name or a
registered alias appears in the source; whether "shared link" and "share link"
are one term is Q-TERM's question (T10), not G4's.

Batched like Q-ATOM (rel01 D30): each atom's answer is checked alone and only a
failed atom is re-asked.
"""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from ..llm import Backend, Question
from .batch import ask_each
from .guards import GuardFailure, locate_quote
from .qatom import Atom
from .quantities import find_quantities

SCHEMA_VERSION = "q-desc/1"

#: Atoms per call. A description is long (seven layer answers, terms, fields), so
#: a big batch outruns the call timeout; ~25 atoms did at 120 s (rel01 S21).
DEFAULT_BATCH_SIZE = 8

MODALITIES = ("MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY")
TERM_KINDS = ("entity", "data", "event", "actor", "component", "external_system",
              "category", "external_reference")
TERM_ROLES = ("subject", "response", "trigger", "state", "scope")
#: The ambiguity kinds a model may propose. The others are found by code
#: (`vague_term` by G6, `unbounded_quantity`, `inferred`, `missing_modality`), by placement
#: (`unplaceable`, `unresolved_term`) or by term resolution (`pending_review`).
#: `vague_term` is G6's alone: offered it, Haiku flagged 17 of 20 real atoms,
#: on words such as "Storage" and "matches" (rel01 S21) — noise that would bury
#: the weak words the owner actually listed.
MODEL_AMBIGUITY = ("missing_actor", "referential", "scope")

#: F2 §4.3 / P-8. The order is the precedence order; the layer mapping is F2's.
LAYER_QUESTIONS = (
    ("Q1", "Does it restrict many parts of the system at once — a budget, an invariant, a policy "
           "that applies across features — rather than state one behaviour, rule or fact? "
           "(Judge the meaning, not words such as 'every' or 'never'.)"),
    ("Q2", "Can it only be judged by a business outcome, not by testing software?"),
    ("Q3", "Can someone outside the system check it just by using the system — its commands, "
           "outputs and files — without looking inside at internal data or algorithms, and "
           "without naming a protocol artefact (path, method, status code, field, event name)?"),
    ("Q4", "Is it about which component exists, owns or runs something?"),
    ("Q5", "Is it about an agreement between two named parties (API, event, message, file format)?"),
    ("Q6", "Is it about the shape, type, identity or lifecycle of data?"),
    ("Q7", "Is it an internal rule or algorithm, verifiable only white-box?"),
)

#: F2 D13: the layers a constraint's scope may name — a closed choice.
SCOPE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5")

_TEXT = {"type": "string"}
_NULLABLE_TEXT = {"type": ["string", "null"]}
#: R7 (rel01 D32): a canonical subject or response must say something.
_CLAIM_TEXT = {"type": "string", "pattern": r"\S"}
_ANSWER = {
    "type": "object", "additionalProperties": False, "required": ["answer", "quote"],
    "properties": {"answer": {"type": "string", "enum": ["yes", "no"]}, "quote": _NULLABLE_TEXT},
}

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["atoms"],
    "properties": {"atoms": {"type": "array", "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["atom_id", "canonical", "layer_answers", "terms", "ambiguity",
                     "scope_layers", "scope_description", "verifies_text", "decision"],
        "properties": {
            "atom_id": _TEXT,
            "canonical": {
                "type": "object", "additionalProperties": False,
                "required": ["state", "trigger", "scope", "subject", "modality", "response"],
                "properties": {
                    "state": _NULLABLE_TEXT, "trigger": _NULLABLE_TEXT, "scope": _NULLABLE_TEXT,
                    "subject": _CLAIM_TEXT, "response": _CLAIM_TEXT,
                    "modality": {"type": ["string", "null"], "enum": [*MODALITIES, None]},
                },
            },
            "layer_answers": {
                "type": "object", "additionalProperties": False,
                "required": [key for key, _ in LAYER_QUESTIONS],
                "properties": {key: _ANSWER for key, _ in LAYER_QUESTIONS},
            },
            "terms": {"type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["name", "kind", "role", "quote"],
                "properties": {
                    "name": _TEXT, "quote": _TEXT,
                    "kind": {"type": "string", "enum": list(TERM_KINDS)},
                    "role": {"type": "string", "enum": list(TERM_ROLES)},
                },
            }},
            "ambiguity": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["kind", "quote"],
                "properties": {"kind": {"type": "string", "enum": list(MODEL_AMBIGUITY)},
                               "quote": _NULLABLE_TEXT},
            }},
            "scope_layers": {"type": "array",
                             "items": {"type": "string", "enum": list(SCOPE_LAYERS)}},
            "scope_description": _NULLABLE_TEXT,
            "verifies_text": _NULLABLE_TEXT,
            "decision": {"type": ["object", "null"], "additionalProperties": False,
                         "required": ["chosen", "rejected"],
                         "properties": {
                             "chosen": _TEXT,
                             "rejected": {"type": "array", "items": {
                                 "type": "object", "additionalProperties": False,
                                 "required": ["option", "reason"],
                                 "properties": {"option": _TEXT, "reason": _TEXT}}},
                         }},
        },
    }}},
}

_INSTRUCTIONS = """\
You are describing atomic specification claims. Each atom below is one claim, given as
quotes from its source block. Answer for each atom, using its exact atom_id.

1. Canonical form. Rewrite the claim into these fields:
   [While <state>] [When <trigger> | If <unwanted condition>] [Where <scope>]
   the <subject> MUST | MUST NOT | SHOULD | SHOULD NOT | MAY <response>
   Use the claim's own words. Add nothing the quotes do not say: no values, names or
   conditions from general knowledge. Use null for absent parts. Use modality null only
   for an assumption, a decision or a verification that states no obligation.

2. Layer questions. Answer each yes or no, in order. For every yes, quote the words of the
   block that make it true. For no, the quote is null.
{layer_questions}
3. Terms. Tag the things the claim is about: short noun phrases of one to three words,
   singular, naming something the system or its users deal with ("share link", "block",
   "profile"). Never tag an id (AC-1.4, D9, F6), a number or value, a whole clause, or
   "the system". Use the same name every time for the same thing. For each: its name, its
   kind ({term_kinds}), its role in the canonical form ({term_roles}), and the quote where
   it appears.

4. Ambiguity. List only what a careful reader genuinely could not pin down:
   missing_actor (no one is named to do it), referential (an unresolved "it", "this",
   "they"), scope (unclear what it applies to). Quote it, or null. An empty list is normal.
   First resolve "it", "this", "they" from the same block text or its section; write the
   resolved thing as the subject. Flag referential only when neither names it.

5. For a constraint over a group, describe the scope in scope_description, tag the terms
   that name the group with role "scope", and list in scope_layers which layers it covers
   (L0 intent, L1 behaviour, L2 structure, L3 contracts such as APIs and file formats,
   L4 data, L5 internal logic), or [] if it is not limited to layers. For a verification,
   say what it verifies in verifies_text, citing ids such as AC-1.4 where the text does. For a decision, give the chosen
   option and each rejected option with its reason. Otherwise null.

Every quote must be copied from a block's "text", character for character. The
"section" line is context only: never quote it.
"""


@dataclass(frozen=True)
class DescribeItem:
    atom_id: str
    atom: Atom
    block: dict[str, Any]


@dataclass
class Description:
    """What Q-DESC and the guards established about one atom; node forming uses it."""

    atom_id: str
    block_id: str
    kind: str
    canonical: dict[str, Any]
    layer_answers: dict[str, dict[str, Any]]
    terms: list[dict[str, Any]]
    ambiguity: list[dict[str, Any]] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    scope_description: str | None = None
    scope_layers: list[str] = field(default_factory=list)
    verifies_text: str | None = None
    decision: dict[str, Any] | None = None


@dataclass
class DescribeOutcome:
    descriptions: dict[str, Description] = field(default_factory=dict)
    failures: dict[str, str] = field(default_factory=dict)
    judgments: dict[str, str] = field(default_factory=dict)      # atom id -> J id (with a lock)


def build_question(items: Sequence[DescribeItem], note: str | None = None,
                   vocabulary: Sequence[str] = ()) -> Question:
    parts = [_INSTRUCTIONS.format(
        layer_questions="".join(f"   {key}  {text}\n" for key, text in LAYER_QUESTIONS),
        term_kinds=", ".join(TERM_KINDS),
        term_roles=", ".join(TERM_ROLES),
    )]
    if items and vocabulary:
        # R2 (rel01 D33). Rendered only with items, so the instructions — and with them
        # the lock key (F3 D21) — do not change as the registry grows.
        parts.append(
            "\nTerms already in the graph. When a claim is about one of these things, tag it with\n"
            "exactly this name. A kind of X is not X: for a review item write \"review item\", not\n"
            "\"item\". Create a new name only when none of these names the thing.\n"
            + "".join(f"- {name}\n" for name in vocabulary)
        )
    if note:
        parts.append(f"\nThe previous answer was rejected. {note}\nTry again, carefully.\n")
    # Each block's text is sent once, however many of its atoms are asked about.
    blocks: dict[str, dict[str, Any]] = {}
    for item in items:
        blocks.setdefault(item.block["id"], item.block)
    for block in blocks.values():
        heading = " > ".join(block.get("heading_path") or []) or "(no heading)"
        parts.append(f"\n=== BLOCK {block['id']} ===\nsection: {heading}\ntext:\n{block['text']}\n")
    for item in items:
        quotes = "".join(f"  - {quote}\n" for quote in item.atom.quotes)
        parts.append(
            f"\n--- ATOM {item.atom_id} (from block {item.block['id']}) ---\n"
            f"kind: {item.atom.kind}\n"
            f"quotes:\n{quotes}"
        )
    return Question(
        kind="q-desc",
        schema_version=SCHEMA_VERSION,
        schema=SCHEMA,
        prompt="".join(parts),
        payload={"atom_ids": [item.atom_id for item in items]},
    )


def describe_atoms(
    items: Sequence[DescribeItem],
    backend: Backend,
    weak_words: Sequence[str],
    aliases: dict[str, list[str]],
    batch_size: int = DEFAULT_BATCH_SIZE,
    lock: Any | None = None,
    vocabulary: Sequence[str] = (),
) -> DescribeOutcome:
    """Describe atoms in batches, re-asking once for each atom whose answer failed a check."""
    outcome = DescribeOutcome()

    def accept(item: DescribeItem, payload: dict[str, Any]) -> None:
        outcome.descriptions[item.atom_id] = _describe(item, payload, weak_words, aliases)

    for start in range(0, len(items), batch_size):
        result = ask_each(
            items[start:start + batch_size],
            item_id=lambda item: item.atom_id,
            backend=backend,
            build_question=lambda items_, note: build_question(items_, note, vocabulary),
            list_key="atoms",
            id_key="atom_id",
            accept=accept,
            lock=lock,
            lock_input=lock_input,
        )
        outcome.failures.update(result.failures)
        outcome.judgments.update(result.judgments)
    return outcome


def lock_input(item: DescribeItem) -> dict[str, Any]:
    return {"kind": item.atom.kind, "quotes": list(item.atom.quotes),
            "block_text": item.block["text"],
            "heading_path": list(item.block.get("heading_path") or [])}


# -- checking one answer ------------------------------------------------------

def _describe(
    item: DescribeItem,
    payload: dict[str, Any],
    weak_words: Sequence[str],
    aliases: dict[str, list[str]],
) -> Description:
    """Apply G2 and the kind rules (re-ask on failure), then G4, G6 and quantities (facts)."""
    text = item.block["text"]
    own = list(item.atom.spans)
    slices = [text[start:end] for start, end in own]

    layer_answers = {}
    for key, _ in LAYER_QUESTIONS:
        answer = payload["layer_answers"][key]
        if answer["answer"] == "yes":
            if not (answer["quote"] or "").strip():
                raise GuardFailure(
                    f"layer answer {key} is 'yes' but gives no quote; a yes must quote the "
                    f"words of the block that make it true"
                )
            span = locate_quote(answer["quote"], text, own)
            layer_answers[key] = {"answer": "yes", "quote": answer["quote"].strip(), "span": span}
        else:
            layer_answers[key] = {"answer": "no", "quote": None, "span": None}

    terms = [
        {**term, "quote": term["quote"].strip(), "span": locate_quote(term["quote"], text, own)}
        for term in payload["terms"]
    ]

    canonical = dict(payload["canonical"])
    if item.atom.kind == "decision" and payload["decision"] is None:
        raise GuardFailure("a decision atom needs its chosen and rejected options; decision was null")
    if item.atom.kind == "verification" and not (payload["verifies_text"] or "").strip():
        raise GuardFailure("a verification atom needs verifies_text; it was empty")

    ambiguity: list[dict[str, Any]] = []
    for candidate in payload["ambiguity"]:
        quote = (candidate["quote"] or "").strip() or None
        if quote is not None:
            locate_quote(quote, text, own)
        _add(ambiguity, candidate["kind"], quote, "proposed by the model")

    quantities = []
    for piece in slices:
        found = find_quantities(piece)
        quantities.extend(quantity.as_record() for quantity in found.quantities)
        for vague in found.unbounded:
            _add(ambiguity, "unbounded_quantity", vague, "an amount with no bound")
    canonical["quantities"] = quantities

    if item.atom.kind in ("requirement", "constraint") and canonical["modality"] is None:
        # F3 D14: an obligation stated without "must"/"should" is under-specified,
        # not wrong. Flag it; never guess MUST on the author's behalf.
        _add(ambiguity, "missing_modality", None,
             f"a {item.atom.kind} with no modal verb (MUST, SHOULD, MAY …)")

    for word, quote in _weak_words(slices, weak_words):
        _add(ambiguity, "vague_term", quote, f"weak word '{word}'")

    injected = _injections(canonical, terms, text, item.block.get("heading_path") or [], aliases)
    for detail in injected:
        _add(ambiguity, "inferred", None, detail)

    return Description(
        atom_id=item.atom_id,
        block_id=item.atom.block_id,
        kind=item.atom.kind,
        canonical=canonical,
        layer_answers=layer_answers,
        terms=terms,
        ambiguity=ambiguity,
        flags=["inferred"] if injected else [],
        scope_description=payload["scope_description"],
        scope_layers=list(payload["scope_layers"]),
        verifies_text=payload["verifies_text"],
        decision=payload["decision"],
    )


def _add(ambiguity: list[dict[str, Any]], kind: str, quote: str | None, detail: str) -> None:
    if any(entry["kind"] == kind and entry["quote"] == quote and quote is not None
           for entry in ambiguity):
        return
    ambiguity.append({"kind": kind, "quote": quote, "detail": detail})


# -- G6 -----------------------------------------------------------------------

def _weak_words(slices: Sequence[str], weak_words: Sequence[str]) -> list[tuple[str, str]]:
    found = []
    for word in weak_words:
        pattern = re.compile(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", re.IGNORECASE)
        for piece in slices:
            match = pattern.search(piece)
            if match:
                found.append((word, match.group(0)))
                break
    return found


# -- G4 -----------------------------------------------------------------------

_VALUE_TOKEN = re.compile(r"[^\s,;:()\"'`]*\d[^\s,;:()\"'`]*")
_CANONICAL_TEXT = ("state", "trigger", "scope", "subject", "response")


def _injections(
    canonical: dict[str, Any],
    terms: list[dict[str, Any]],
    block_text: str,
    heading_path: Sequence[str],
    aliases: dict[str, list[str]],
) -> list[str]:
    """What the description asserts that its source — block and headings — does not contain."""
    source = _flat(" ".join([*heading_path, block_text]))
    problems = []

    for name in _CANONICAL_TEXT:
        value = canonical.get(name) or ""
        for token in _VALUE_TOKEN.findall(value):
            token = token.rstrip(".")
            if token and not _contains(source, token):
                problems.append(f"canonical {name} contains {token!r}, which the source does not")

    for term in terms:
        # G2 has already anchored the term's quote in the block, so a term is
        # grounded by construction; its *name* is checked only so that a name
        # the source never uses is visible. Renaming is Q-TERM's question.
        names = [term["name"], term["quote"], *aliases.get(term["name"], [])]
        if not any(_contains(source, name) for name in names):
            problems.append(f"term {term['name']!r} is not in the source")
    return problems


def _flat(text: str) -> str:
    """Lower-cased, whitespace-collapsed, without Markdown's inline code and emphasis marks."""
    return " ".join(text.replace("`", "").replace("*", "").split()).lower()


def _contains(source: str, fragment: str) -> bool:
    fragment = _flat(fragment)
    return re.search(r"(?<![\w.])" + re.escape(fragment) + r"(?!\d)", source) is not None

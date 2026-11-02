"""F3 §4.5, §4.8 — pending blocks in, a draft of the graph out.

Pending blocks are processed in `(source, first line)` order, in **chunks**
(⚑ F3 D18). One chunk goes through every model step — Q-ATOM, Q-DESC, the T3
split re-ask, Q-TERM — before any of it is kept. That is what makes the call cap
safe (AC-3.5): when the budget runs out mid-chunk, the finished chunks stand and
the interrupted one stays pending, whole. A backend failure — a usage limit, an
outage — stops the same way (I-43), so paid-for work is never thrown away.

A block is **all or nothing** (AC-3.16): one atom that fails its checks drops
every node of its block, and the block becomes an `atomize_failed` attention
item and stays pending. A block that yields no atoms completes.

The draft is in memory. F4 writes it in one transaction (T11), including each
completed block's `atomized_hash` (F1 D13).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..errors import ExitCode, SddcError
from ..llm import Backend
from ..model.family import term_links
from ..model.ids import IdCounter, adopt_human_ids, find_human_id, find_local_label, human_labels
from ..model.layers import LAYER_OF_QUESTION
from ..model.placement import Placement, place
from ..model.schema import validate
from .contracts import annotate, contract_atom
from .definitions import Definition, block_definitions
from .describe import DescribeItem, describe_atoms
from .align import NewAtom, align
from .forming import NodeDraft, block_annotations, example_pieces, layer_hint, resolve_verifies
from .placement_types import PlacedAtom
from .guards import GuardFailure, anchor_quotes
from .qatom import Atom, AtomizeOutcome, atomize_blocks
from .terms import TermResolution, normalize_name, resolve_terms

DEFAULT_BLOCK_BATCH = 20     # blocks per Q-ATOM call (measured, rel01 S20)
VOCABULARY_LIMIT = 100       # term names shown to Q-DESC (rel01 D33 R2)


@dataclass
class GraphDraft:
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    terms: dict[str, dict[str, Any]] = field(default_factory=dict)        # new or changed terms
    links: list[dict[str, Any]] = field(default_factory=list)
    reviews: list[dict[str, Any]] = field(default_factory=list)
    completed: dict[str, str] = field(default_factory=dict)              # block id -> atomized_hash
    alignments: list[dict[str, Any]] = field(default_factory=list)       # F3 §4.6, for the report
    failed: dict[str, str] = field(default_factory=dict)                 # block id -> reason
    empty: dict[str, dict[str, Any]] = field(default_factory=dict)       # completed, formed no node (D33)
    annotations_dropped: list[dict[str, Any]] = field(default_factory=list)   # F3 D35 (I-67)
    definitions: list[Definition] = field(default_factory=list)          # F3 D38, completed blocks
    definitions_dropped: list[dict[str, Any]] = field(default_factory=list)   # quote not in its block
    quotes_replaced: list[dict[str, Any]] = field(default_factory=list)  # F3 D40, contract quotes
    stopped: str | None = None                                            # "call_cap" | "backend"
    stop_reason: str | None = None
    counters: dict[str, int] = field(default_factory=dict)


@dataclass
class _Chunk:
    placed: dict[str, list[PlacedAtom]] = field(default_factory=dict)    # good blocks, in order
    annotations: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    failed: dict[str, str] = field(default_factory=dict)
    empty: dict[str, list[str]] = field(default_factory=dict)            # block id -> sentence roles
    definitions: dict[str, list[str]] = field(default_factory=dict)      # block id -> quotes (F3 D38)
    terms: TermResolution = field(default_factory=TermResolution)


def atomize_pending(
    blocks: Sequence[Mapping[str, Any]],
    backend: Backend,
    *,
    run_id: str,
    weak_words: Sequence[str] = (),
    layer_hints: Mapping[str, Mapping[str, Any]] | None = None,
    registry: Mapping[str, Mapping[str, Any]] | None = None,
    existing_nodes: Mapping[str, Mapping[str, Any]] | None = None,
    counters: Mapping[str, int] | None = None,
    block_batch: int = DEFAULT_BLOCK_BATCH,
    previous: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    lock: Any | None = None,
    contract_languages: Sequence[str] = (),
    all_blocks: Sequence[Mapping[str, Any]] | None = None,
) -> GraphDraft:
    """`previous`: a changed block's old nodes, which its new atoms are aligned to (F3 §4.6).
    `all_blocks`: every live block, where a contract finds its lead (F3 §4.5a); default `blocks`."""
    draft = GraphDraft()
    blocks = annotate(blocks, all_blocks if all_blocks is not None else blocks, contract_languages)
    node_ids = IdCounter("N-", start=(counters or {}).get("N", 0))
    review_ids = IdCounter("RV-", start=(counters or {}).get("RV", 0))
    known_terms: dict[str, Mapping[str, Any]] = dict(registry or {})
    existing = dict(existing_nodes or {})
    ordered = sorted(blocks, key=lambda b: (b["source"], b["lines"][0]))
    good_blocks: dict[str, Mapping[str, Any]] = {}
    atom_counts: dict[str, int] = {}
    node_drafts: list[NodeDraft] = []
    pending_reviews: list[dict[str, Any]] = []
    usage_total: dict[str, int] = {}
    usage_by_file: dict[str, dict[str, int]] = {}
    for node in existing.values():
        _count_usage(node["source"]["file"], [t["term"] for t in node["terms"]], usage_total, usage_by_file)

    for start in range(0, len(ordered), block_batch):
        chunk_blocks = ordered[start:start + block_batch]
        try:
            names = vocabulary(known_terms, usage_total, usage_by_file,
                               sorted({b["source"] for b in chunk_blocks}))
            chunk = _run_chunk(chunk_blocks, backend, weak_words, known_terms, lock, names)
        except SddcError as error:
            # I-43: a stop mid-run keeps every finished chunk (and its lock records);
            # only the interrupted chunk stays pending.
            if error.exit_code in (ExitCode.CALL_CAP, ExitCode.BACKEND):
                draft.stopped = "call_cap" if error.exit_code == ExitCode.CALL_CAP else "backend"
                draft.stop_reason = str(error)
                break
            raise

        by_id = {block["id"]: block for block in chunk_blocks}
        for block_id, reason in chunk.failed.items():
            draft.failed[block_id] = reason
            pending_reviews.append(_review("atomize_failed", block_id, reason, by_id[block_id]))

        for block_id, placed in chunk.placed.items():
            good_blocks[block_id] = by_id[block_id]
            atom_counts[block_id] = len(placed)
            found, dropped = block_definitions(by_id[block_id], chunk.definitions.get(block_id, []))
            draft.definitions += found
            draft.definitions_dropped += dropped
            if not placed:                           # F3 D33: completed, but nothing in it was a claim
                block = by_id[block_id]
                draft.empty[block_id] = {
                    "block": block_id, "file": block["source"], "lines": list(block["lines"]),
                    "roles": chunk.empty.get(block_id, [])}
        labels = human_labels(good_blocks, atom_counts)          # a duplicate label fails the build
        adopted = adopt_human_ids({b: good_blocks[b] for b in chunk.placed}, atom_counts)

        new_terms = {**chunk.terms.new_terms, **chunk.terms.changed_terms}
        known_terms.update(new_terms)
        draft.terms.update(new_terms)
        for item in chunk.terms.reviews:
            pending_reviews.append(_review(item["type"], item["subject"], item["detail"], None))

        for block_id, placed in chunk.placed.items():
            block = by_id[block_id]
            annotations, unlocatable = block_annotations(block, chunk.annotations.get(block_id, []))
            draft.annotations_dropped += unlocatable
            examples, annotations = example_pieces(block, placed, annotations)      # F3 D41
            placed = [*placed, *(piece for piece, _ in examples)]
            olds = list((previous or {}).get(block_id, []))
            aligned = align(olds, [
                NewAtom(n, " … ".join(block["text"][s:e] for s, e in piece.atom.spans),
                        piece.description.canonical["subject"], piece.description.canonical["response"])
                for n, piece in enumerate(placed)])
            for old_id, kind in aligned.dropped.items():
                draft.alignments.append({"block": block_id, "node": old_id, "kind": kind})
            for n, piece in enumerate(placed):
                kept, kind = aligned.assigned[n]
                # An aligned id beats an adopted one: identity across edits first (F3 D22).
                node_id = kept or adopted.get(block_id) or node_ids.next_id()
                if olds:
                    draft.alignments.append({"block": block_id, "node": node_id, "kind": kind})
                if node_id in existing or any(d.node_id == node_id for d in node_drafts):
                    raise SddcError(f"node id {node_id} is already in use (F2 §4.8)", ExitCode.INPUT)
                terms = _resolved_terms(piece, chunk.terms, known_terms)
                draft.quotes_replaced += [{**r, "node": node_id} for r in piece.description.replaced]
                node_drafts.append(NodeDraft(
                    node_id=node_id, placed=piece, block=block, terms=terms,
                    label=labels.get(block_id) or find_local_label(block),   # F2 D12, D20
                    layer_hint=layer_hint(block.get("heading_path") or [], layer_hints),
                    annotations=annotations,
                    pending_terms=sorted({t["term"] for t in terms} & chunk.terms.pending_review),
                    alignment=kind if kept else "new",
                    old=next((o for o in olds if o["id"] == kept), None),
                ))
            ids = [d.node_id for d in node_drafts[len(node_drafts) - len(placed):]]
            for piece, illustrated in examples:                     # F3 D41: cite the claim's id
                piece.description.verifies_text = ids[illustrated]
                _count_usage(block["source"], [t["term"] for t in terms], usage_total, usage_by_file)
            draft.completed[block_id] = block["text_hash"]

    _finish(draft, node_drafts, existing, run_id)
    for item in pending_reviews:
        draft.reviews.append({**item, "id": review_ids.next_id(), "opened_run": run_id})
    for node in draft.nodes.values():
        if "inferred" in node["flags"]:
            details = "; ".join(a["detail"] for a in node["ambiguity"] if a["kind"] == "inferred")
            draft.reviews.append({
                **_review("inferred_node", node["id"], details, None, node=node),
                "id": review_ids.next_id(), "opened_run": run_id,
            })
    draft.reviews = [_ordered_review(item) for item in draft.reviews]
    draft.counters = {"N": node_ids.value, "RV": review_ids.value}
    return draft


# -- one chunk: every model step ------------------------------------------------

def _run_chunk(
    blocks: Sequence[Mapping[str, Any]],
    backend: Backend,
    weak_words: Sequence[str],
    known_terms: Mapping[str, Mapping[str, Any]],
    lock: Any | None = None,
    names: Sequence[str] = (),
) -> _Chunk:
    chunk = _Chunk()
    aliases = {t["canonical"]: list(t.get("aliases", [])) for t in known_terms.values()}
    # F3 §4.5a: a contract is formed whole by code; only prose goes to Q-ATOM.
    prose = [block for block in blocks if "contract" not in block]
    atomized = atomize_blocks(prose, backend, lock=lock) if prose else AtomizeOutcome()
    atomized.atoms += [contract_atom(block) for block in blocks if "contract" in block]
    chunk.failed.update(atomized.failures)
    chunk.annotations.update(atomized.annotations)
    chunk.empty.update(atomized.empty)
    chunk.definitions.update(atomized.definitions)

    atoms_by_block = {block["id"]: [] for block in blocks if block["id"] not in chunk.failed}
    for atom in atomized.atoms:
        if atom.block_id in atoms_by_block:
            atoms_by_block[atom.block_id].append(atom)
    for block in blocks:
        if block["id"] in atoms_by_block:
            atoms_by_block[block["id"]] = one_criterion(block, atoms_by_block[block["id"]])
            if not one_claim_block(block):            # F3 D44: an atom keeps what it is about
                atoms_by_block[block["id"]] = keep_subjects(
                    block, atoms_by_block[block["id"]], atomized.sentences.get(block["id"], []))

    by_id = {block["id"]: block for block in blocks}
    atom_judgments = dict(atomized.judgments)
    placed = _describe_and_place(atoms_by_block, by_id, backend, weak_words, aliases, chunk.failed,
                                 lock, atom_judgments, names=names,
                                 # F3 D36 (R16, I-70): these blocks hold one claim by their own form,
                                 # so they are placed by the first yes and flagged, never re-asked.
                                 never_split={b for b in atoms_by_block if one_claim_block(by_id[b])})

    for block_id, split in list(placed.items()):
        if not isinstance(split, dict):
            continue
        # AC-3.12 — one more Q-ATOM for this block, naming the two claims to separate.
        note = (f"Your atoms mixed two claims that belong to different layers: "
                f"{split['first']['quote']!r} and {split['second']['quote']!r}. "
                f"Make them separate atoms.")
        again = atomize_blocks([by_id[block_id]], backend, note=note, lock=lock)
        if block_id in again.failures:
            chunk.failed[block_id] = again.failures[block_id]
            del placed[block_id]
            continue
        chunk.annotations[block_id] = again.annotations.get(block_id, [])
        chunk.definitions[block_id] = again.definitions.get(block_id, [])
        atom_judgments.update(again.judgments)
        # F3 D23 (I-42): this is the last chance. If the model again keeps one claim
        # across two layers — typically a bold title and its explanation — place it by
        # the first yes and flag it `mixed_layers`, rather than fail the block.
        again_atoms = keep_subjects(by_id[block_id], again.atoms, again.sentences.get(block_id, []))
        retried = _describe_and_place({block_id: again_atoms}, by_id, backend, weak_words, aliases,
                                      chunk.failed, lock, atom_judgments, accept_mixed=True,
                                      names=names)
        if block_id not in retried:
            del placed[block_id]
            continue
        placed[block_id] = retried[block_id]

    chunk.placed = {b: placed[b] for b in atoms_by_block if b in placed}
    tags = [tag for pieces in chunk.placed.values() for piece in pieces for tag in piece.description.terms]
    chunk.terms = resolve_terms(tags, known_terms, backend, lock=lock)
    return chunk


def _describe_and_place(
    atoms_by_block: Mapping[str, Sequence[Any]],
    by_id: Mapping[str, Mapping[str, Any]],
    backend: Backend,
    weak_words: Sequence[str],
    aliases: Mapping[str, list[str]],
    failed: dict[str, str],
    lock: Any | None = None,
    atom_judgments: Mapping[str, str] | None = None,
    accept_mixed: bool = False,
    names: Sequence[str] = (),
    never_split: set[str] | None = None,
) -> dict[str, Any]:
    """Block id → its placed atoms, or the split that stopped it. Failed blocks go to `failed`."""
    items = [
        DescribeItem(f"{block_id}#{n}", atom, by_id[block_id], contract="contract" in by_id[block_id],
                     lead=(by_id[block_id].get("contract") or {}).get("lead"))
        for block_id, atoms in atoms_by_block.items()
        for n, atom in enumerate(atoms, start=1)
    ]
    described = describe_atoms(items, backend, weak_words=list(weak_words), aliases=dict(aliases),
                               lock=lock, vocabulary=names)

    result: dict[str, Any] = {}
    for block_id, atoms in atoms_by_block.items():
        mine = [item for item in items if item.block["id"] == block_id]
        broken = [item.atom_id for item in mine if item.atom_id in described.failures]
        if broken:
            failed[block_id] = f"{broken[0]}: {described.failures[broken[0]]}"
            continue
        pieces = []
        for item in mine:
            description = described.descriptions[item.atom_id]
            placement = place(description.kind, description.layer_answers)
            if placement.split_required and (accept_mixed or block_id in (never_split or set())):
                split = placement.split_required
                placement = Placement(layer=LAYER_OF_QUESTION[split["first"]["question"]], ambiguity=[{
                    "kind": "mixed_layers", "quote": split["second"]["quote"],
                    "detail": f"{split['second']['question']} also answered yes, on words that do not "
                              f"overlap {split['first']['question']}'s; the model twice kept one claim",
                }])
            if placement.split_required:
                result[block_id] = placement.split_required
                break
            judgments = [j for j in ((atom_judgments or {}).get(block_id),
                                     described.judgments.get(item.atom_id)) if j]
            pieces.append(PlacedAtom(item.atom, description, placement, judgments))
        else:
            result[block_id] = pieces
    return result


def one_claim_block(block: Mapping[str, Any]) -> bool:
    """A block whose own form says it holds exactly one claim: a table row (F3 D34), a block
    labelled `AC-…` (F3 D28) or a contract (F3 D39)."""
    label = find_human_id(block)
    return (block.get("kind") == "table_row" or "contract" in block
            or bool(label and label.startswith("AC-")))


def one_criterion(block: Mapping[str, Any], atoms: Sequence[Atom]) -> list[Atom]:
    """One claim per block where the source's own form says so — enforced in code, not left to
    the prompt (the fragments' quotes are kept, in block order, so the node covers the whole):

    - a block labelled `AC-…` is one verification atom (R8, rel01 D32, F3 D28): in the M2 gate,
      criteria came back as Given / When / Then fragments plus a stray atom from the tier tag;
    - a **table row** is one atom of its own kind (R15, F3 D34): in R15, F5's `S3` row came back
      as one atom per cell, so one rule became three fragments in three families.
    """
    label = find_human_id(block)
    criterion = bool(label and label.startswith("AC-"))
    row = block.get("kind") == "table_row"
    if criterion:
        if len(atoms) <= 1 and all(atom.kind == "verification" for atom in atoms):
            return list(atoms)
    elif not row or not atoms:
        return list(atoms)
    kind = "verification" if criterion else atoms[0].kind
    pairs = sorted({(span, quote) for atom in atoms for span, quote in zip(atom.spans, atom.quotes)})
    folded = Atom(block_id=block["id"], kind=kind,
                  quotes=[quote for _, quote in pairs], spans=[span for span, _ in pairs])
    return row_sentences(block, folded) if row else [folded]


PRONOUNS = frozenset({"it", "its", "they", "their", "them", "this", "these", "that", "those"})


def keep_subjects(block: Mapping[str, Any], atoms: Sequence[Atom], sentences: Sequence[str]) -> list[Atom]:
    """F3 D44 (rel02 round 17): an atom keeps the words that say what it is about.

    Q-ATOM may quote a sentence's predicates and none of its subject: "Abort — <its causes> —
    yields …, writes …" became atoms with no cause in them (C17), and "…; it still prints its
    message" a node about "it" (C22). For each claim sentence of the answer: (a) an opening no atom
    covers leads every atom of the sentence; (b) otherwise an atom opening with a pronoun, not the
    sentence's first, is led by the first atom's first quote. Verbatim spans only, no model call."""
    text = block["text"]
    leads: dict[int, tuple[tuple[int, int], str]] = {}       # atom index -> its lead
    for sentence in sentences:
        try:
            [anchor] = anchor_quotes([sentence], text, [])
        except GuardFailure:
            continue                                         # not located: leave the atoms alone
        start, end = anchor.span
        inside = sorted((atom.spans[0][0], i) for i, atom in enumerate(atoms)
                        if atom.spans and start <= atom.spans[0][0] < end)
        if not inside:
            continue
        first_start, first_index = inside[0]
        opening = text[start:first_start]
        covered = any(s[0] < first_start and s[1] > start for atom in atoms for s in atom.spans)
        if opening.strip() and any(ch.isalnum() for ch in opening) and not covered:
            lead_text = opening.strip()
            lead_start = start + opening.index(lead_text)
            for _, i in inside:
                leads[i] = ((lead_start, lead_start + len(lead_text)), lead_text)
            continue
        first = atoms[first_index]
        for _, i in inside[1:]:
            words = atoms[i].quotes[0].strip("`*_ ").split()
            if words and words[0].lower().strip(",;:") in PRONOUNS:
                leads[i] = (first.spans[0], first.quotes[0])
    if not leads:
        return list(atoms)
    out = []
    for i, atom in enumerate(atoms):
        if i in leads:
            span, quote = leads[i]
            out.append(Atom(block_id=atom.block_id, kind=atom.kind,
                            quotes=[quote, *atom.quotes], spans=[span, *atom.spans]))
        else:
            out.append(atom)
    return out


def _cells(text: str) -> list[tuple[int, int]]:
    """The `(start, end)` of each cell of a table row, between unescaped `|` marks."""
    marks = [i for i, ch in enumerate(text) if ch == "|" and (i == 0 or text[i - 1] != "\\")]
    return [(a + 1, b) for a, b in zip(marks, marks[1:])]


def row_sentences(block: Mapping[str, Any], atom: Atom) -> list[Atom]:
    """F3 D43 (rel02 round 17): a cell that holds several quoted sentences is one claim per sentence.

    D34 folds a row because its cells are the parts of one rule; an interface table's `form` cell
    instead holds several sentences about the entry the first cell names, and folding them hid a
    contradicting sentence from retrieval. Every sentence after a cell's first becomes its own atom;
    each piece, and the row's remaining atom, is led by the first cell — its quotes, or its own text
    located in the block when the answer quoted none — so a piece keeps its subject. A row whose
    cells hold one quote each is returned unchanged (D34's case). No model call."""
    text = block["text"]
    cells = _cells(text)
    if len(cells) < 2:
        return [atom]

    def cell_of(span: tuple[int, int]) -> int:
        return next((i for i, (a, b) in enumerate(cells) if a <= span[0] < b), -1)

    pairs = list(zip(atom.spans, atom.quotes))
    by_cell: dict[int, list[tuple[tuple[int, int], str]]] = {}
    for span, quote in pairs:
        by_cell.setdefault(cell_of(span), []).append((span, quote))
    extra = [p for c, ps in sorted(by_cell.items()) if c > 0 for p in ps[1:]]
    if not extra:
        return [atom]
    key = by_cell.get(0)
    if not key:
        a, b = cells[0]
        stripped = text[a:b].strip()
        if not stripped:
            return [atom]
        start = text.index(stripped, a)
        key = [((start, start + len(stripped)), stripped)]
    rest = [p for p in pairs if p not in extra and p not in key]
    pieces = [key + rest] + [key + [p] for p in extra]
    return [Atom(block_id=atom.block_id, kind=atom.kind,
                 quotes=[q for _, q in piece], spans=[s for s, _ in piece]) for piece in pieces]


def vocabulary(
    registry: Mapping[str, Mapping[str, Any]],
    usage_total: Mapping[str, int],
    usage_by_file: Mapping[str, Mapping[str, int]],
    files: Sequence[str],
    limit: int = VOCABULARY_LIMIT,
) -> list[str]:
    """R2 (rel01 D33): the term names Q-DESC is shown — the chunk's own files' terms first,
    then the most used overall, then the rest; each group by use, then by id."""
    chosen: list[str] = []

    def take(ids: Any) -> None:
        for term_id in ids:
            if term_id in registry and term_id not in chosen and len(chosen) < limit:
                chosen.append(term_id)

    local: dict[str, int] = {}
    for name in files:
        for term_id, count in usage_by_file.get(name, {}).items():
            local[term_id] = local.get(term_id, 0) + count
    take(sorted(local, key=lambda t: (-local[t], t)))
    take(sorted(usage_total, key=lambda t: (-usage_total[t], t)))
    take(sorted(registry))
    return [registry[term_id]["canonical"] for term_id in chosen]


def _count_usage(file: str, terms: Sequence[str], total: dict[str, int],
                 by_file: dict[str, dict[str, int]]) -> None:
    for term in terms:
        total[term] = total.get(term, 0) + 1
        by_file.setdefault(file, {})[term] = by_file.setdefault(file, {}).get(term, 0) + 1


# -- after the last chunk: cross-node work and validation -----------------------

def _finish(draft: GraphDraft, drafts: list[NodeDraft], existing: Mapping[str, Mapping[str, Any]],
            run_id: str) -> None:
    for node_draft in drafts:
        if node_draft.layer != "V":
            draft.nodes[node_draft.node_id] = node_draft.record(run_id)

    verifications = [d for d in drafts if d.layer == "V"]
    if verifications:
        view = {**existing, **draft.nodes,
                **{d.node_id: {"label": d.label, "text": d.text, "family": None,
                               "source": {"file": d.block["source"], "block_id": d.block["id"]}}
                   for d in verifications}}
        verifies, links = resolve_verifies(
            view, {d.node_id: d.description.verifies_text for d in verifications})
        for node_draft in verifications:
            node_draft.verifies = verifies[node_draft.node_id]
            node_draft.verified_families = [
                view[target]["family"] for target in node_draft.verifies if view[target].get("family")
            ]
            draft.nodes[node_draft.node_id] = node_draft.record(run_id)
        draft.links += links

    draft.nodes = dict(sorted(draft.nodes.items()))
    for node in draft.nodes.values():
        draft.links += term_links(node["id"], node["terms"])
    draft.links.sort(key=lambda link: (link["from"], link["type"], link["to"]))

    for node in draft.nodes.values():
        validate("node", node)
    for term in draft.terms.values():
        validate("term", term)
    for link in draft.links:
        validate("link", link)


def _resolved_terms(piece: PlacedAtom, terms: TermResolution,
                    known: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    resolved = []
    for tag in piece.description.terms:
        term = terms.by_tag.get(normalize_name(tag["name"]))
        if term is None:          # not a term name (F3 D19): dropped
            continue
        if any(entry["term"] == term and entry["role"] == tag["role"] for entry in resolved):
            continue
        resolved.append({"term": term, "kind": known[term]["kind"], "role": tag["role"],
                         "quote": tag["quote"]})
    return resolved


def _review(kind: str, subject: str, detail: str, block: Mapping[str, Any] | None,
            node: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = None
    if block is not None:
        source = {"file": block["source"], "lines": list(block["lines"]), "quotes": []}
    elif node is not None:
        source = {"file": node["source"]["file"], "lines": node["source"]["lines"],
                  "quotes": [node["text"]]}
    return {"type": kind, "subject": subject, "detail": detail, "source": source,
            "state": "open", "closed_run": None}


def _ordered_review(item: Mapping[str, Any]) -> dict[str, Any]:
    """CT-3.3 key order."""
    keys = ("id", "type", "subject", "detail", "source", "state", "opened_run", "closed_run")
    return {key: item[key] for key in keys}

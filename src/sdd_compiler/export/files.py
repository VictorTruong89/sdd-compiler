"""F7 §4.7, §4.8, CT-7.4, CT-7.5 — `MAP.md`, `CHECKLIST.md` and `export.meta.json`."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .. import __version__
from ..ingest.identity import pending_status
from ..ingest.pipeline import BLOCKS_FILE, SOURCES_FILE
from ..profile import STORE_DIR
from .model import Model
from .packs import Packs, is_contract, lead_line
from .units import FOUNDATION_KEY

HOW_TO_USE = """\
1. Read pack 00 (the foundation) first, if there is one, then each pack in the order of the table above.
2. Every id in `CHECKLIST.md` must end in one of three states: implemented, tested, or listed as
   not done with a reason.
3. Mark code with `# spec: <id>` beside what satisfies an id. Name a test after the acceptance
   criterion's label (`test_AC_4_7_…`) or the node id.
4. Fields named *derived* (layer, modality, kind, relation) were assigned by the compiler. The
   verbatim text of a block wins over them.
5. A block tagged `no node` carries spec text that formed no claim; read it, it is still the spec.\
"""

_STORE_FILES = (BLOCKS_FILE, SOURCES_FILE, "terms.jsonl", "conflicts.jsonl", "adjudications.jsonl",
                "profile.yaml")


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _short(text: str, limit: int = 80) -> str:
    line = _one_line(text)
    return line if len(line) <= limit else line[:limit] + "…"


# -- CHECKLIST.md -------------------------------------------------------------------------------

def checklist(model: Model, packs: Packs) -> tuple[str, int]:
    out = ["# Checklist", "",
           "Every id below must end implemented, tested, or listed as not done with a reason.", ""]
    count = 0
    by_unit: dict[Any, list[dict[str, Any]]] = {}
    for node_id, key in model.home.items():
        by_unit.setdefault(key, []).append(model.graph.nodes[node_id])
    for unit in packs.order:
        nodes = sorted(by_unit.get(unit.key, []),
                       key=lambda x: (x["source"]["file"], x["source"]["lines"][0], x["id"]))
        out += [f"## Pack {packs.numbers[unit.key]} — {packs.names[unit.key]}", ""]
        for node in nodes:
            text = lead_line(model, node) or node["id"] if is_contract(model, node) else node["text"]
            out.append(f"- [ ] {node['id']} · {node['kind']} · {node['canonical']['modality'] or '—'} · "
                       f"{node['layer'] or '—'} · {node['label'] or '—'} · {_short(text)}")
            count += 1
        if not nodes:
            out.append("None.")
        out.append("")
    return "\n".join(out), count


# -- MAP.md ----------------------------------------------------------------------------------------

def map_md(model: Model, packs: Packs, meta: dict[str, Any], pending: list[str],
           allow_open: bool) -> str:
    assert model.units is not None
    out = ["# Map", ""]
    if allow_open and packs.unsettled:
        out += [f"> ⚠ UNSETTLED: {len(packs.unsettled)} contradiction(s) have no current human verdict "
                f"({', '.join(packs.unsettled)}). The export was made with `--allow-open`; "
                f"treat them as open questions, not as spec.", ""]
    if pending:
        out += [f"> ⚠ {len(pending)} block(s) are pending (not yet atomized) and carry no node; "
                f"they are still printed verbatim.", ""]
    if model.units.foundation is None:
        out += ["> ⚠ No foundation pack: no file matches `export.foundation_globs`.", ""]

    out += ["## Read first", ""]
    if model.units.foundation:
        sources = sorted({model.blocks[i]["source"] for i in model.units.foundation.block_ids})
        out.append(f"`packs/{packs.names[FOUNDATION_KEY]}` — {', '.join(sources)} "
                   f"({len(model.units.foundation.block_ids)} blocks).")
    else:
        out.append("None.")
    out += ["", "## Units in build order", "",
            "| Pack | File | Source · heading | Blocks | Claims | AC | Needs |",
            "|---|---|---|---|---|---|---|"]
    by_unit: dict[Any, list[dict[str, Any]]] = {}
    for node_id, key in model.home.items():
        by_unit.setdefault(key, []).append(model.graph.nodes[node_id])
    needs_of: dict[Any, set[Any]] = {}
    for x, y in model.needs:
        needs_of.setdefault(x, set()).add(y)
    for unit in packs.order:
        nodes = by_unit.get(unit.key, [])
        kinds: dict[str, int] = {}
        for node in nodes:
            if node["kind"] != "verification":
                kinds[node["kind"]] = kinds.get(node["kind"], 0) + 1
        label = "foundation" if unit.key == FOUNDATION_KEY else \
            f"{unit.source} · {' › '.join(unit.headings) or '(root)'}"
        needs = ", ".join(sorted(packs.numbers[k] for k in needs_of.get(unit.key, ()))) or "—"
        out.append(f"| {packs.numbers[unit.key]} | `{packs.names[unit.key]}` | {label} | "
                   f"{len(unit.block_ids)} | {', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) or '—'} | "
                   f"{sum(1 for x in nodes if x['layer'] == 'V')} | {needs} |")
    if not packs.order:
        out.append("| — | — | — | — | — | — | — |")

    out += ["", "## Needs against the order", ""]
    out += [f"- pack {b['from']} needs pack {b['to']} ({b['links']} link{'s' if b['links'] != 1 else ''})"
            for b in meta["backward_needs"]] or ["None."]

    out += ["", "## Contracts", ""]
    rows = set()
    for node_id, key in model.home.items():
        node = model.graph.nodes[node_id]
        for label in {node["label"], node["id"]}:
            if label and re.match(r"^CT-\d", label):
                rows.add((0, label, f"- {label} → pack {packs.numbers[key]}"))
    for unit in packs.order:
        for block_id in unit.block_ids:
            block = model.blocks[block_id]
            if block["kind"] == "code":
                rows.add((1, block_id, f"- code block {block_id} "
                          f"({block['source']}:{block['lines'][0]}-{block['lines'][1]}) → "
                          f"pack {packs.numbers[unit.key]}"))
    out += [line for _, _, line in sorted(rows)] or ["None."]

    out += ["", "## Decisions", ""]
    rows = []
    for node_id, key in sorted(model.home.items()):
        node = model.graph.nodes[node_id]
        if node["kind"] == "decision":
            rows.append(f"- {node['label'] or node['id']} ({node['id']}) → pack {packs.numbers[key]}")
    out += rows or ["None."]

    out += ["", "## How to use", "", HOW_TO_USE, "", "## Counts", ""]
    counts = meta["counts"]
    out += [f"- {name.replace('_', ' ')}: {value}" for name, value in counts.items()]
    return "\n".join(out) + "\n"


# -- export.meta.json --------------------------------------------------------------------------------

_INT = {"type": "integer", "minimum": 0}
META_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["schema_version", "compiler_version", "store_hash", "profile_export", "allow_open",
                 "counts", "unsettled_ids", "excluded_blocks", "backward_needs", "chars"],
    "properties": {
        "schema_version": {"const": "export/1"},
        "compiler_version": {"type": "string"},
        "store_hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "profile_export": {"type": "object", "additionalProperties": False,
                           "required": ["foundation_globs", "skip_headings"],
                           "properties": {"foundation_globs": {"type": "array", "items": {"type": "string"}},
                                          "skip_headings": {"type": "array", "items": {"type": "string"}}}},
        "allow_open": {"type": "boolean"},
        "counts": {"type": "object", "additionalProperties": False,
                   "required": ["packs", "blocks", "blocks_omitted", "blocks_excluded", "blocks_no_node",
                                "blocks_pending", "nodes", "nodes_omitted", "contracts",
                                "checklist_items", "unsettled_contradictions"],
                   "properties": {k: _INT for k in (
                       "packs", "blocks", "blocks_omitted", "blocks_excluded", "blocks_no_node",
                       "blocks_pending", "nodes", "nodes_omitted", "contracts", "checklist_items",
                       "unsettled_contradictions")}},
        "unsettled_ids": {"type": "array", "items": {"type": "string"}},
        "excluded_blocks": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["block", "reason"],
            "properties": {"block": {"type": "string"},
                           "reason": {"enum": ["skip_heading", "real_duplicate"]}}}},
        "backward_needs": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["from", "to", "links"],
            "properties": {"from": {"type": "string"}, "to": {"type": "string"},
                           "links": {"type": "integer", "minimum": 1}}}},
        "chars": {"type": "object", "additionalProperties": False,
                  "required": ["source_markdown", "export_total", "packs"],
                  "properties": {"source_markdown": _INT, "export_total": _INT,
                                 "packs": {"type": "object", "additionalProperties": _INT}}},
    },
}


def store_hash(store: Path) -> str:
    """sha256 over the store files the export reads, in sorted path order (path, then bytes)."""
    store = Path(store)
    paths = [store / name for name in _STORE_FILES if (store / name).exists()]
    for folder in ("nodes", "edges"):
        paths += sorted((store / folder).glob("*.jsonl"))
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(store).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return "sha256:" + digest.hexdigest()


def pending_blocks(model: Model, packs: Packs) -> tuple[list[str], list[str]]:
    """(pending, no_node) among the printed blocks that carry no node."""
    profile = model.profile
    with_node = {model.graph.nodes[i]["source"]["block_id"] for i in model.home}
    pending, plain = [], []
    for block_id in sorted(packs.rendered_blocks):
        if block_id in with_node:
            continue
        block = model.blocks[block_id]
        if pending_status(block, profile.include_code_blocks, profile.skip_headings,
                          profile.contract_languages):
            pending.append(block_id)
        else:
            plain.append(block_id)
    return pending, plain


def build_meta(model: Model, packs: Packs, checklist_items: int, allow_open: bool, pending: list[str],
               no_node: list[str]) -> dict[str, Any]:
    assert model.units is not None
    store = model.root / STORE_DIR
    omitted = [{"block": i, "reason": "skip_heading"} for i in model.units.omitted]
    excluded = [{"block": i, "reason": "real_duplicate"} for i in model.units.excluded]
    sources = [r["path"] for r in _read_sources(store)]
    source_chars = sum(len(_read_text(model.root / p)) for p in sources)
    sizes = {name.removeprefix("packs/"): len(text) for name, text in packs.files.items()}
    assert model.order is not None
    backward = [{"from": packs.numbers[x], "to": packs.numbers[y], "links": n}
                for x, y, n in model.order.backward]
    return {
        "schema_version": "export/1",
        "compiler_version": __version__,
        "store_hash": store_hash(store),
        "profile_export": {"foundation_globs": list(model.profile.export.foundation_globs),
                           "skip_headings": list(model.profile.skip_headings)},
        "allow_open": allow_open,
        "counts": {
            "packs": len(packs.files),
            "blocks": sum(1 for b in model.blocks.values() if not b["removed_run"]),
            "blocks_omitted": len(omitted), "blocks_excluded": len(excluded),
            "blocks_no_node": len(no_node), "blocks_pending": len(pending),
            "nodes": len(model.graph.nodes), "nodes_omitted": len(model.omitted_nodes),
            "contracts": sum(1 for i in model.home if is_contract(model, model.graph.nodes[i])),
            "checklist_items": checklist_items,
            "unsettled_contradictions": len(packs.unsettled),
        },
        "unsettled_ids": packs.unsettled,
        "excluded_blocks": sorted(omitted + excluded, key=lambda e: e["block"]),
        "backward_needs": backward,
        "chars": {"source_markdown": source_chars, "export_total": sum(sizes.values()), "packs": sizes},
    }


def _read_sources(store: Path) -> list[dict[str, Any]]:
    from ..store.jsonl import read_jsonl
    return read_jsonl(store / SOURCES_FILE)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

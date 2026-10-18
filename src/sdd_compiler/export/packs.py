"""F7 §4.5, CT-7.1, CT-7.3 — one Markdown pack per unit: the text first, the lists after (D6)."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from ..ingest.identity import pending_status
from ..model.scope import covers
from .gate import classify
from .model import Model
from .units import FOUNDATION_KEY, Unit, UnitKey

CLAIM_KINDS = ("requirement", "constraint", "decision", "assumption")
_CONTRACT_ID = re.compile(r"^CT-\d+\.\d+$")
SECTIONS = ("Text", "Claims to implement", "Acceptance criteria", "Constraints in scope",
            "Related elsewhere", "Conflicts", "Terms")


@dataclass
class Packs:
    files: dict[str, str]                                   # "packs/00-foundation.md" → text
    numbers: dict[UnitKey, str]
    names: dict[UnitKey, str]                               # unit → file name under packs/
    order: list[Unit]                                       # build order, foundation first
    rendered_blocks: dict[str, str] = field(default_factory=dict)   # block id → pack file
    unsettled: list[str] = field(default_factory=list)


def number_units(model: Model) -> tuple[list[Unit], dict[UnitKey, str], dict[UnitKey, str]]:
    assert model.units is not None
    order = ([model.units.foundation] if model.units.foundation else [])
    assert model.order is not None
    order += model.order.units
    last = len(order) - 1 if model.units.foundation else len(order)
    width = max(2, len(str(last)))
    numbers, names, taken = {}, {}, set()
    for i, unit in enumerate(order):
        number = str(i if model.units.foundation else i + 1).zfill(width)
        numbers[unit.key] = number
        if unit.key == FOUNDATION_KEY:
            names[unit.key] = f"{number}-foundation.md"
            continue
        base = f"{number}-{_spec_slug(unit.source)}--{_section_slug(unit.headings)}"
        name, k = base, 1
        while name in taken:
            k += 1
            name = f"{base}-{k}"
        taken.add(name)
        names[unit.key] = f"{name}.md"
    return order, numbers, names


def _slug(text: str, limit: int | None = None) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].strip("-") if limit else slug


def _spec_slug(source: str) -> str:
    path = PurePosixPath(source)
    return _slug(path.parent.name if path.name == "spec.md" and path.parent.name else path.stem)


def _section_slug(headings: tuple[str, ...]) -> str:
    heading = headings[-1] if headings else "root"                  # CT-7.1: the key's last heading
    return _slug(heading, 40) or "root"


# -- text helpers -------------------------------------------------------------------------

def is_contract(model: Model, node: dict[str, Any]) -> bool:
    return bool(_CONTRACT_ID.match(node["id"])) and model.node_block(node["id"])["kind"] == "code"


def lead_line(model: Model, node: dict[str, Any]) -> str | None:
    """The first line of the nearest earlier non-code block of the same source that starts with
    `**<id>` (verbatim), or None."""
    block = model.node_block(node["id"])
    best = None
    for other in model.blocks.values():
        if other["source"] != block["source"] or other["kind"] == "code" or other["removed_run"]:
            continue
        if other["lines"][0] < block["lines"][0] and other["text"].lstrip("> ").startswith(f"**{node['id']}") \
                and (best is None or other["lines"][0] > best["lines"][0]):
            best = other
    return best["text"].lstrip("> ").split("\n", 1)[0] if best else None


def shown(model: Model, node: dict[str, Any]) -> str:
    """Node text for a list line; a contract's fence stays in Text (D12)."""
    if is_contract(model, node):
        lead = lead_line(model, node)
        return (lead + " " if lead else "") + "(fence in Text)"
    return node["text"].replace("\n", "\n    ")


_RUN_ID = re.compile(r"^N-(\d+)$")


def _label(node: dict[str, Any]) -> str | None:
    return node["label"] if node["label"] and node["label"] != node["id"] else None


def tag(nodes: list[dict[str, Any]]) -> str:
    """D15 — ids only, a label in parentheses, three or more consecutive unlabelled `N-` ids as a range."""
    out: list[str] = []
    run: list[str] = []

    def flush() -> None:
        out.extend([f"{run[0]}–{run[-1]}"] if len(run) >= 3 else run)
        run.clear()

    for node in nodes:
        match = _RUN_ID.match(node["id"])
        if _label(node) or not match:
            flush()
            out.append(f"{node['id']} ({_label(node)})" if _label(node) else node["id"])
            continue
        previous = _RUN_ID.match(run[-1]) if run else None
        if previous and not (int(match.group(1)) == int(previous.group(1)) + 1
                             and len(match.group(1)) == len(previous.group(1))):
            flush()
        run.append(node["id"])
    flush()
    return ", ".join(out)


def _test_name(node: dict[str, Any]) -> str:
    return "test_" + re.sub(r"[^A-Za-z0-9]", "_", node["label"] or node["id"]) + "_…"


# -- building ---------------------------------------------------------------------------------

def build_packs(model: Model, allow_open: bool = False) -> Packs:
    assert model.units is not None
    order, numbers, names = number_units(model)
    globals_ = _global_constraints(model)
    global_pack = numbers[order[0].key] if order else None
    context = _Context(model, numbers, allow_open, globals_, global_pack)
    files, rendered = {}, {}
    for unit in order:
        text = _render_pack(context, unit)
        files[f"packs/{names[unit.key]}"] = text
        for block_id in unit.block_ids:
            rendered[block_id] = f"packs/{names[unit.key]}"
    unsettled = sorted(c["id"] for c in model.open_conflicts() if classify(model, c) == "unsettled")
    return Packs(files, numbers, names, order, rendered, unsettled)


@dataclass
class _Context:
    model: Model
    numbers: dict[UnitKey, str]
    allow_open: bool
    globals_: list[dict[str, Any]]
    global_pack: str | None


def _is_global(node: dict[str, Any]) -> bool:
    """A broad `C` node (D14): its selector names no family, term or category — empty, or layers only."""
    selector = node["scope_selector"] or {}
    return node["layer"] == "C" and not (selector.get("families") or selector.get("terms")
                                         or selector.get("categories"))


def _global_constraints(model: Model) -> list[dict[str, Any]]:
    return [model.graph.nodes[i] for i in sorted(model.home) if _is_global(model.graph.nodes[i])]


def _nodes_of(model: Model, unit: Unit) -> list[dict[str, Any]]:
    """Nodes homed in the unit, in source order."""
    nodes = [model.graph.nodes[i] for i, key in model.home.items() if key == unit.key]
    return sorted(nodes, key=lambda x: (x["source"]["file"], x["source"]["lines"][0], x["id"]))


def _render_pack(ctx: _Context, unit: Unit) -> str:
    model = ctx.model
    nodes = _nodes_of(model, unit)
    number = ctx.numbers[unit.key]
    if unit.key == FOUNDATION_KEY:
        sources = sorted({model.blocks[b]["source"] for b in unit.block_ids})
        title = f"# Pack {number} — foundation · {', '.join(sources)}"
    else:
        title = f"# Pack {number} — {unit.source} · {' › '.join(unit.headings) or '(root)'}"
    kinds = Counter(x["kind"] for x in nodes)
    acs = sorted(x["label"] or x["id"] for x in nodes if x["layer"] == "V"
                 and (x["label"] or x["id"]).startswith("AC-"))
    counts = (f"blocks {len(unit.block_ids)} · nodes {len(nodes)}"
              + (f" ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))})" if nodes else "")
              + f" · AC labels: {', '.join(acs) if acs else 'none'}")
    sections = [_text(ctx, unit), _claims(ctx, nodes), _criteria(ctx, nodes),
                _scope(ctx, unit, nodes), _related(ctx, nodes), _conflicts(ctx, nodes),
                _terms(ctx, nodes)]
    out = [title, counts, ""]
    for name, body in zip(SECTIONS, sections):
        out += [f"## {name}", body.rstrip("\n") if body.strip() else "None.", ""]
    return "\n".join(out)


def _nodes_by_block(model: Model) -> dict[str, list[dict[str, Any]]]:
    by_block: dict[str, list[dict[str, Any]]] = {}
    for node_id in sorted(model.home):
        node = model.graph.nodes[node_id]
        by_block.setdefault(node["source"]["block_id"], []).append(node)
    return by_block


def _text(ctx: _Context, unit: Unit) -> str:
    model = ctx.model
    by_block = _nodes_by_block(model)
    out: list[str] = []
    previous: list[str] = []
    i = 0
    ids = unit.block_ids
    while i < len(ids):
        block = model.blocks[ids[i]]
        path = block["heading_path"]
        if path != previous:
            common = 0
            while common < min(len(path), len(previous)) and path[common] == previous[common]:
                common += 1
            for depth in range(common, len(path)):
                out += [f"{'#' * min(depth + 1, 6)} {path[depth]}", ""]
            previous = path
        if block["kind"] == "table_row" and block["table_header"]:
            j = i
            while j + 1 < len(ids) and model.blocks[ids[j + 1]]["kind"] == "table_row" \
                    and model.blocks[ids[j + 1]]["table_header"] == block["table_header"] \
                    and model.blocks[ids[j + 1]]["heading_path"] == path:
                j += 1
            rows = [model.blocks[x] for x in ids[i:j + 1]]
            columns = block["table_header"].strip().strip("|").count("|") + 1
            out += [block["table_header"], "|" + " --- |" * columns, *[r["text"] for r in rows]]
            for number, row in enumerate(rows, 1):
                out.append(f"↳ row {number}: {_tag_line(model, row, by_block.get(row['id'], []))}")
            i = j + 1
        else:
            out += [block["text"], f"↳ {_tag_line(model, block, by_block.get(block['id'], []))}"]
            i += 1
        out.append("")
    return "\n".join(out)


def _tag_line(model: Model, block: dict[str, Any], nodes: list[dict[str, Any]]) -> str:
    if nodes:
        return tag(nodes)
    profile = model.profile
    pending = pending_status(block, profile.include_code_blocks, profile.skip_headings,
                             profile.contract_languages)
    return "no node (pending)" if pending else "no node"


def _claims(ctx: _Context, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    out = []
    targets: dict[str, list[str]] = {}
    for link in model.links():
        if link["type"] == "depends_on":
            targets.setdefault(link["from"], []).append(link["to"])
    for node in nodes:
        if _is_example(node):                                        # D17: beside the claims, no text
            out.append(f"- [{node['id']}] example of {', '.join(sorted(node['verifies'] or [])) or 'none'}")
            continue
        if node["kind"] not in CLAIM_KINDS:
            continue
        needs = [f"{t}" + (f" (pack {ctx.numbers[model.home[t]]})" if model.home.get(t) not in
                           (None, model.home[node['id']]) else "") for t in sorted(set(targets.get(node["id"], [])))]
        tail = (f" · {_label(node)}" if _label(node) else "") + (f" · needs {', '.join(needs)}" if needs else "")
        if is_contract(model, node):                                 # D12: the lead line points at the fence
            out.append(f"- [{node['id']}] contract · {node['layer'] or '—'}{tail} — {shown(model, node)}")
        else:                                                        # D15: no node text; it is in Text
            out.append(f"- [{node['id']}] {node['kind']} · {node['canonical']['modality'] or '—'} · "
                       f"{node['layer'] or '—'}{tail}")
        if node["kind"] == "decision" and node["decision"]:
            out.append(f"  chosen: {node['decision']['chosen']}")
            rejected = "; ".join(f"{r['option']} — {r['reason']}" for r in node["decision"]["rejected"])
            out.append(f"  rejected: {rejected or 'none'}")
    return "\n".join(out)


def _is_example(node: dict[str, Any]) -> bool:
    """F7 D17: a `V` node formed from an example sentence (F3 D41) carries the flag `example`."""
    return "example" in (node.get("flags") or [])


def _criteria(ctx: _Context, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    verifies: dict[str, list[str]] = {}
    for link in model.links():
        if link["type"] == "verifies":
            verifies.setdefault(link["from"], []).append(link["to"])
    out = []
    for node in nodes:
        if node["layer"] != "V" or _is_example(node):                 # D17: an example is not a criterion
            continue
        ids = sorted(set(verifies.get(node["id"], [])) | set(node["verifies"] or []))
        out += [f"- [{node['label'] or node['id']}] {shown(model, node)}",
                f"  verifies: {', '.join(ids) if ids else 'none'}",
                f"  test name: {_test_name(node)}"]
    return "\n".join(out)


def _scope(ctx: _Context, unit: Unit, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    lines = []
    if ctx.global_pack is not None and ctx.numbers[unit.key] == ctx.global_pack:
        for node in ctx.globals_:
            layers = (node["scope_selector"] or {}).get("layers") or []
            scope = f"layers {', '.join(layers)} — " if layers else ""
            lines.append(f"- [{node['id']}] (pack {ctx.numbers[model.home[node['id']]]}) {scope}"
                         f"{shown(model, node)}")
    else:
        for node_id, key in sorted(model.home.items()):
            constraint = model.graph.nodes[node_id]
            if key == unit.key or constraint["layer"] != "C" or _is_global(constraint):
                continue
            if any(covers(constraint, node) for node in nodes):
                lines.append(f"- [{node_id}] (pack {ctx.numbers[key]}) {shown(model, constraint)}")
    if ctx.globals_ and ctx.numbers[unit.key] != ctx.global_pack:
        lines.append(f"plus the broad constraints in pack {ctx.global_pack}")
    return "\n".join(lines)


def _related(ctx: _Context, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    mine = {n["id"] for n in nodes}
    here = model.home[nodes[0]["id"]] if nodes else None
    rows: list[tuple[str, str, str, str]] = []              # (a, relation, z, other)
    with_text = {"duplicates", "same as", "covered by"}     # D14: judged refines/subsumes are ids only
    for link in model.links():
        if link["type"] not in ("refines", "subsumes", "duplicates"):
            continue
        a, z = link["from"], link["to"]
        if a in mine and model.home.get(z) not in (None, here):
            rows.append((a, link["type"], z, z))
        elif z in mine and model.home.get(a) not in (None, here):
            rows.append((a, link["type"], z, a))
    for record in model.open_conflicts():
        klass = classify(model, record)
        if klass not in ("same_as", "covered_by"):
            continue
        members = sorted({model.resolve(m) for m in record["members"]})
        if len(members) != 2 or any(m not in model.home for m in members):
            continue
        a, z = members
        relation = "same as" if klass == "same_as" else "covered by"
        if a in mine:
            rows.append((a, relation, z, z))
        if z in mine:
            rows.append((z, relation, a, a))
    out = []
    for a, relation, z, other in sorted(set(rows)):
        where = "this pack" if model.home[other] == here else f"pack {ctx.numbers[model.home[other]]}"
        text = f" {shown(model, model.graph.nodes[other])}" if relation in with_text else ""
        out.append(f"- {a} {relation} {z} ({where}){text}")
    return "\n".join(out)


def _conflicts(ctx: _Context, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    mine = {n["id"] for n in nodes}
    out = []
    for record in model.open_conflicts():
        klass = classify(model, record)
        if klass not in ("settled", "unsettled"):
            continue
        members = sorted({model.resolve(m) for m in record["members"]})
        if len(members) < 2 or not (mine & set(members)) or any(m not in model.home for m in members):
            continue
        word = "Settled" if klass == "settled" else "UNSETTLED"
        quotes = " vs ".join(f'{m} "{record["quotes"].get(m, "")}"' for m in members)
        out.append(f"- {word}: {record['id']} — {quotes}")
        out.append(f"  rationale: {record['rationale']}")
        note = (model.verdicts.get(record["id"]) or {}).get("note")
        if klass == "settled" and note:
            out.append(f"  adjudication: {note}")
    return "\n".join(out)


def _terms(ctx: _Context, nodes: list[dict[str, Any]]) -> str:
    model = ctx.model
    used = {t["term"] for n in nodes for t in n["terms"] if t["term"] in model.graph.terms}
    out = []
    listed = (model.graph.terms[t] for t in used
              if model.graph.terms[t]["definition"] or model.graph.terms[t]["aliases"])   # D14
    for term in sorted(listed, key=lambda t: (t["canonical"], t["id"])):
        line = f"- {term['canonical']}"
        if term["aliases"]:
            line += f" (aliases: {', '.join(sorted(term['aliases']))})"
        if term["definition"]:
            line += f' — defined: "{term["definition"]}"'
        out.append(line)
    return "\n".join(out)

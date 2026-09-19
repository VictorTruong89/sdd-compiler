"""The six rel01 commands (build-plan B2, amended by I-38), thin over the pipeline."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import ExitCode, SddcError
from .ingest import pipeline
from .pipeline import compile_graph
from .store.graph import load_graph
from .store.index import GraphIndex, counts as graph_counts
from .views.render import family_card, family_label
from .profile import STORE_DIR, profile_path, render_default_profile


def init(root: Path, as_json: bool = False) -> int:
    """Create `.sdd/` and a default profile. AC-1.25: never overwrite one."""
    path = profile_path(root)
    if path.exists():
        raise SddcError(
            f"{path} already exists — edit it, or delete {STORE_DIR}/ to start over",
            ExitCode.USAGE,
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_default_profile(), encoding="utf-8", newline="\n")
    _say(f"initialized {path.parent}", {"created": str(path)}, as_json)
    return ExitCode.OK


def compile_(root: Path, paths: list[str] | None = None, as_json: bool = False,
             replay: bool = True) -> int:
    """rel01's one command: ingest, atomize what is pending, write the graph (B1)."""
    result = compile_graph(root, paths=paths, replay=replay)
    s = result.summary()
    counts = s["counts"]
    _say(
        f"{s['run']}: {len(s['files'])} file(s) · {counts['new']} new · {counts['changed']} changed · "
        f"{counts['removed']} removed · {s['pending']} pending → {s['completed']} atomized, "
        f"{s['failed']} failed · {s['nodes_formed']} node(s) formed, {s['nodes_deleted']} deleted · "
        f"{s['attention_items']} attention item(s) · {s['model_calls']} model call(s), "
        f"${s['cost_usd']:.2f}, {s['replayed']} answer(s) replayed from the lock"
        + (f" · alignments: " + ", ".join(
            f"{k} {n}" for k, n in sorted(
                {k: sum(1 for a in s["alignments"] if a["kind"] == k)
                 for k in {a["kind"] for a in s["alignments"]}}.items()))
           if s["alignments"] else "")
        + (f" · STOPPED ({s['stopped']}): {s['stop_reason']} — what finished is written, "
           f"the rest stays pending" if s["stopped"] else ""),
        s,
        as_json,
    )
    return result.exit_code


def ingest(root: Path, paths: list[str] | None = None, as_json: bool = False) -> int:
    """Only the ingest phase (F1 CT-1.6): no model calls."""
    result = pipeline.ingest(root, paths=paths, command="ingest")
    counts = result.counts
    _say(
        f"{result.run_id}: {len(result.files)} file(s) · "
        f"{counts['new']} new · {counts['changed']} changed · "
        f"{counts['unchanged']} unchanged · {counts['removed']} removed",
        {"run": result.run_id, "files": result.files, "counts": counts},
        as_json,
    )
    return ExitCode.OK


def status(root: Path, as_json: bool = False) -> int:
    payload = pipeline.status(root)
    payload["graph"] = dict(graph_counts(load_graph(Path(root) / STORE_DIR)))   # T13 (F4 §4.4)
    counts, g = payload["counts"], payload["graph"]
    _say(
        f"{counts['sources']} source(s) · {counts['blocks']} blocks · "
        f"{counts['pending']} pending (run {payload['run'] or 'none yet'}) · "
        f"{g['nodes']} nodes · {g['families']} families · "
        f"{g['open_conflicts']} open conflict{'s' if g['open_conflicts'] != 1 else ''} · "
        f"{g['attention_items']} attention item(s)",
        payload,
        as_json,
    )
    return ExitCode.OK


def family(root: Path, name: str, as_json: bool = False) -> int:
    """T14 — one family's card (F4 §4.6); `--json` gives the members by layer."""
    graph = load_graph(Path(root) / STORE_DIR)
    index = GraphIndex.build(graph)
    try:
        found = index.family_of(name)
    except KeyError:
        known = sorted(family_label(f) for f in index.by_family)
        raise SddcError(
            f"no family named {name!r}; families: {', '.join(known[:20]) or 'none yet'}"
            + (" …" if len(known) > 20 else ""),
            ExitCode.INPUT,
        ) from None
    if as_json:
        members: dict[str, list[dict]] = {}
        for node_id in index.by_family[found]:
            node = index.by_id[node_id]
            members.setdefault(node["layer"] or "—", []).append(
                {"id": node_id, "status": node["status"], "text": node["text"]})
        print(json.dumps({"family": found, "members": members}, ensure_ascii=False))
    else:
        print(family_card(graph, found, index=index), end="")
    return ExitCode.OK


def _say(text: str, payload: dict, as_json: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False) if as_json else text)

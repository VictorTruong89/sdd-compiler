"""The six rel01 commands (build-plan B2, amended by I-38), thin over the pipeline."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import ExitCode, SddcError
from .ingest import pipeline
from .pipeline import compile_graph
from .conflicts.adjudicate import record_adjudication, verdicts_for
from .report import conflict_groups, render_report
from .store.graph import load_graph, registry_of
from .store.index import GraphIndex, counts as graph_counts
from .views.render import conflicts_list, family_card, family_label
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
    """rel01's one command: ingest, atomize what is pending, check for conflicts, report (B1)."""
    result = compile_graph(root, paths=paths, replay=replay)
    summary = result.summary()
    if as_json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        graph = load_graph(Path(root) / STORE_DIR)
        print(render_report(summary, graph, result.exit_code), end="")
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


def export_(root: Path, out: Path | None = None, allow_open: bool = False,
            as_json: bool = False) -> int:
    """F7 — write the agent export from the compiled store. No model call."""
    from .export.pipeline import export
    result = export(root, out=out, allow_open=allow_open)
    counts = result.meta["counts"]
    _say(f"exported {counts['packs']} packs · {counts['nodes']} nodes · "
         f"{counts['unsettled_contradictions']} unsettled contradiction(s) · {result.out}",
         result.meta, as_json)
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


def conflicts(root: Path, as_json: bool = False, judge: str | None = None,
              verdict: str | None = None, note: str | None = None) -> int:
    """T18 — every open conflict (F4 §4.6, F6 §4.8): grouped, contradictions first.
    T19 — `sddc conflicts judge CF-… --verdict real|false` records a human verdict (G4 §4).
    Exit `3` while any conflict is open, so a CI step can gate on it."""
    store = Path(root) / STORE_DIR
    if judge is not None:
        if verdict is None:
            raise SddcError("judging a conflict needs --verdict real|false", ExitCode.USAGE)
        record = record_adjudication(store, judge, verdict, note=note)
        # F6 D21: the id alone means nothing outside its store — name the file (`sddc conflicts
        # judge` is the one place a person meets an adjudication id).
        _say(f"{store / 'adjudications.jsonl'}  {record['id']}: {record['conflict']} judged "
             f"{record['verdict']}" + (f" — {record['note']}" if record["note"] else ""),
             record, as_json)
        return ExitCode.OK

    graph = load_graph(store)
    groups = conflict_groups(graph)
    judged = verdicts_for(store)
    if as_json:
        print(json.dumps({
            "registry": registry_of(graph),
            "groups": [[{"id": r["id"], "kind": r["kind"], "members": r["members"]} for r in group]
                       for group in groups],
            "conflicts": [{**record, "adjudication": judged.get(record["id"])}
                          for group in groups for record in group],
        }, ensure_ascii=False))
    else:
        text = conflicts_list(graph)
        for conflict_id, state in sorted(judged.items()):
            mark = f" — judged {state['verdict']}" + (" (stale: judged again since)"
                                                      if state["stale"] else "")
            text = text.replace(f"**{conflict_id}**", f"**{conflict_id}**{mark}", 1)
        print(text, end="")
    return ExitCode.CONFLICTS if groups else ExitCode.OK


def _say(text: str, payload: dict, as_json: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False) if as_json else text)

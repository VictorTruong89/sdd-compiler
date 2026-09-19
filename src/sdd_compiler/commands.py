"""The five rel01 commands (build-plan B2), thin over the pipeline."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import ExitCode, SddcError
from .ingest import pipeline
from .pipeline import compile_graph
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
    counts = payload["counts"]
    _say(
        f"{counts['sources']} source(s) · {counts['blocks']} blocks · "
        f"{counts['pending']} pending (run {payload['run'] or 'none yet'})",
        payload,
        as_json,
    )
    return ExitCode.OK


def _say(text: str, payload: dict, as_json: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False) if as_json else text)

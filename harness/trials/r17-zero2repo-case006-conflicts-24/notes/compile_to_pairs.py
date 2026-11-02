"""Compile up to pair-picking only: atomize the changed blocks, propose the pairs, judge none.

    python3 notes/compile_to_pairs.py work/compile-planted       (Haiku calls for atomizing only)

Runs the compiler's own `compile_graph` unchanged, with two wrappers from outside: `propose` is
recorded (the pairs the check phase would judge, written to <store>/pairs-proposed.json), and the
first `judge_batch` call raises the compiler's own call-cap error, so the check phase stops the way
F6 §4.7 defines: the atomized nodes and terms are written, every pair stays unjudged and every
node keeps its `unchecked`/`stale` status, so a later `sddc compile` judges them. No compiler file
is changed. The owner approved this step on 2026-10-30 ("compile up to pair-picking and rank the 24").
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
from sdd_compiler import pipeline                                  # noqa: E402
from sdd_compiler.conflicts import pipeline as conflicts_pipeline  # noqa: E402
from sdd_compiler.errors import ExitCode, SddcError                # noqa: E402

root = Path(sys.argv[1]).resolve()
recorded = {}
_propose = conflicts_pipeline.propose


def propose(nodes, **kw):
    out = _propose(nodes, **kw)
    recorded["pairs"] = out.pairs
    recorded["counts"] = out.counts
    recorded["checked"] = out.checked
    return out


def judge_batch(*args, **kw):
    raise SddcError("stopped before judging (compile_to_pairs.py)", ExitCode.CALL_CAP)


conflicts_pipeline.propose = propose
conflicts_pipeline.judge_batch = judge_batch
result = pipeline.compile_graph(root)
(root / "pairs-proposed.json").write_text(json.dumps(
    {"counts": recorded.get("counts"), "checked": recorded.get("checked"),
     "pairs": [{k: p[k] for k in ("a", "b", "score", "pair_key")} for p in recorded.get("pairs", [])]},
    indent=1) + "\n")
print(json.dumps({"summary": result.summary(), "pairs": len(recorded.get("pairs", [])),
                  "retrieval": recorded.get("counts")}, default=str))

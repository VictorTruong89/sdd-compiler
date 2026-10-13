"""Size and shape of DevEval's specifications, as packaged for Harbor. No model call.

    python3 -I spec_stats.py download/deveval

One row per repository, read from its `*-implementation` task: the words in each of the four specification
documents named in its `repo_config.json`, the words of the instruction the agent receives, and how many
source files the task removes (`RUN rm -rf` lines in the Dockerfile) out of the files named in the
repository's `code_file_DAG`. Words are whitespace-separated tokens.
"""
import json
import re
import statistics
import sys
from pathlib import Path

DOCS = ("PRD.md", "UML_class.md", "UML_sequence.md", "architecture_design.md")
KEYS = ("PRD", "UML_class", "UML_sequence", "architecture_design")


def words(p: Path) -> int:
    return len(p.read_text(errors="replace").split()) if p.is_file() else 0


def main(root: Path) -> None:
    rows = []
    for task in sorted(root.glob("*-implementation")):
        repo = task / "environment" / "deveval_source_repo"
        cfg = json.loads((repo / "repo_config.json").read_text()) if (repo / "repo_config.json").is_file() else {}
        # the documents sit in docs/ or at the repository root; repo_config.json says where
        doc = {d: words(repo / cfg.get(k, d)) for d, k in zip(DOCS, KEYS)}
        other_docs = sorted(p.name for p in (repo / "docs").glob("*") if p.name not in DOCS) if (repo / "docs").is_dir() else []
        removed = re.findall(r'^RUN rm -rf "([^"]+)"', (task / "environment" / "Dockerfile").read_text(), re.M)
        dag = cfg.get("code_file_DAG", {})
        dag_files = set(dag) | {f for deps in dag.values() for f in deps}
        tests = sum(1 for p in repo.rglob("*") if p.is_file() and ("unit_tests" in p.parts or "acceptance_tests" in p.parts))
        rows.append({"repo": task.name.removesuffix("-implementation"), **doc, "spec_total": sum(doc.values()),
                     "instruction": words(task / "instruction.md"), "removed": len(removed),
                     "dag_files": len(dag_files), "test_files": tests, "other_docs": other_docs})
    head = ["repo", *DOCS, "spec_total", "instruction", "removed", "dag_files", "test_files"]
    print(" | ".join(head))
    for r in rows:
        print(" | ".join(str(r[h]) for h in head), "|", ",".join(r["other_docs"]))
    for h in head[1:]:
        xs = [r[h] for r in rows]
        print(f"{h}: min {min(xs)} median {statistics.median(xs)} mean {statistics.mean(xs):.1f} max {max(xs)}")
    print("repositories:", len(rows))


if __name__ == "__main__":
    main(Path(sys.argv[1]))

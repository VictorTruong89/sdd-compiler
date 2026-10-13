"""Size and shape of what a Doc2Feat-Bench task gives the agent. No model call.

    python -I spec_stats.py download/data/verified.jsonl [download/data/full.jsonl ...]

Reads the datasets as exported from Hugging Face (see TRIAL.md §6). Words are whitespace-separated
tokens; a "documentation file" is one `diff --git` section of the input diff.
"""
import json
import statistics
import sys
from collections import Counter


def med(xs):
    return statistics.median(xs) if xs else None


def files_of(diff: str) -> list[str]:
    return [line.split(" b/", 1)[-1] for line in diff.splitlines() if line.startswith("diff --git ")]


def as_list(v):
    return json.loads(v) if isinstance(v, str) else (v or [])


def report(path: str) -> None:
    rows = [json.loads(line) for line in open(path)]
    print(f"== {path}: {len(rows)} tasks")
    print("repos:", dict(Counter(r["repo"] for r in rows).most_common()))
    for field in ("problem_statement", "mask_doc_diff", "feature_patch", "test_patch"):
        vals = [r[field] if isinstance(r[field], str) else json.dumps(r[field]) for r in rows]
        words = [len(v.split()) for v in vals]
        lines = [len(v.splitlines()) for v in vals]
        print(f"{field}: words min {min(words)} median {med(words)} mean {statistics.mean(words):.2f} "
              f"max {max(words)} | lines median {med(lines)} max {max(lines)}")
    same = sum(1 for r in rows if isinstance(r["mask_doc_diff"], str) and r["mask_doc_diff"] in r["problem_statement"])
    print("problem_statement contains mask_doc_diff verbatim:", same, "of", len(rows))
    nfiles = [len(files_of(r["problem_statement"])) for r in rows]
    print(f"documentation files in the input: min {min(nfiles)} median {med(nfiles)} max {max(nfiles)}; "
          f"distribution {dict(sorted(Counter(nfiles).items()))}")
    added = [sum(1 for line in r["problem_statement"].splitlines() if line.startswith("+") and not line.startswith("+++"))
             for r in rows]
    print(f"added documentation lines: min {min(added)} median {med(added)} max {max(added)}")
    ext = Counter(f.rsplit(".", 1)[-1] if "." in f else "(none)" for r in rows for f in files_of(r["problem_statement"]))
    print("documentation file types:", dict(ext.most_common(8)))
    f2p = [len(as_list(r["FAIL2PASS"])) for r in rows]
    p2p = [len(as_list(r["PASS2PASS"])) for r in rows]
    print(f"FAIL2PASS tests: min {min(f2p)} median {med(f2p)} max {max(f2p)} | "
          f"PASS2PASS tests: min {min(p2p)} median {med(p2p)} max {max(p2p)}")
    code_files = [len(files_of(r["feature_patch"])) for r in rows]
    print(f"files in the reference code patch: median {med(code_files)} max {max(code_files)}")
    aug = sum(1 for r in rows if r.get("augmentations"))
    print("tasks with a non-empty augmentations field:", aug)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)

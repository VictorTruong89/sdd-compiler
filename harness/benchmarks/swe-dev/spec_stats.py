"""Size and shape of SWE-Dev's task input (the PRD and the code context), test split. No model call.

    python3 -I spec_stats.py download/data/dataset/test

One JSON file per sample, in `easy/` and `hard/`. Per split: words and lines of the `PRD` text, how
many source files the model is shown (`file_code`) and their words, how many files the reference
changes (`GT_file_code`), how many packages the samples come from, and how many PRDs contain a
docstring section. Words are whitespace-separated tokens.
"""
import json
import statistics
import sys
from pathlib import Path


def words(text) -> int:
    return len(text.split()) if isinstance(text, str) else 0


def summary(name: str, xs: list) -> str:
    return f"  {name}: min {min(xs)} median {statistics.median(xs)} mean {statistics.mean(xs):.1f} max {max(xs)}"


def main(root: Path) -> None:
    for split in sorted(p for p in root.iterdir() if p.is_dir()):
        prd_w, prd_l, shown_n, shown_w, gt_n, tests_w = [], [], [], [], [], []
        packages, keys, has_doc = set(), set(), 0
        files = sorted(split.glob("*.json"))
        for f in files:
            d = json.loads(f.read_text(encoding="utf-8"))
            keys |= set(d)
            prd = d.get("PRD", "")
            prd_w.append(words(prd))
            prd_l.append(len(prd.splitlines()))
            shown = d.get("file_code") or {}
            shown_n.append(len(shown))
            shown_w.append(sum(words(c) for c in shown.values()))
            gt_n.append(len(d.get("GT_file_code") or {}))
            tc = d.get("test_code")
            tests_w.append(sum(words(c) for c in tc.values()) if isinstance(tc, dict) else words(tc))
            packages.add(d.get("package_name"))
            has_doc += '"""' in prd
        print(f"{split.name}: {len(files)} samples, {len(packages)} packages")
        print(summary("PRD words", prd_w))
        print(summary("PRD lines", prd_l))
        print(summary("source files shown", shown_n))
        print(summary("words of source shown", shown_w))
        print(summary("files in the reference", gt_n))
        print(summary("words of test code", tests_w))
        print(f"  PRDs containing a docstring block: {has_doc}")
        print("  keys:", sorted(keys))


if __name__ == "__main__":
    main(Path(sys.argv[1]))

"""Trial 1: size and shape of ProjectEval's specifications. No model, no network.

    python3 -I spec_stats.py download/ProjectEval/data/project_eval_project.json

Words are whitespace-separated tokens of the text (for JSON fields: of the JSON text, so keys and
punctuation count). Good enough to tell a sentence from a document; not a token count.
"""
import json
import statistics
import sys
from collections import Counter

projects = json.load(open(sys.argv[1], encoding="utf-8"))


def words(value):
    return len((value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)).split())


print("id type     prompt_words checklist_words checklist_functions tests skeleton_files")
for p in projects:
    functions = sum(len(page["function"]) for page in p["nl_checklist"])
    tests = sum(len(page["function"]) for page in p["testcode"])
    print(f'{p["project_id"]:>2} {p["project_type"]:<8} {words(p["nl_prompt"]):>12} '
          f'{words(p["nl_checklist"]):>15} {functions:>19} {tests:>5} {len(p["skeleton"]):>14}')

prompt = [words(p["nl_prompt"]) for p in projects]
checklist = [words(p["nl_checklist"]) for p in projects]
print("projects:", len(projects), dict(Counter(p["project_type"] for p in projects)))
print("prompt words    min/median/max:", min(prompt), statistics.median(prompt), max(prompt))
print("checklist words min/median/max:", min(checklist), statistics.median(checklist), max(checklist))
print("checklist functions:", sum(len(pg["function"]) for p in projects for pg in p["nl_checklist"]))
print("tests:", sum(len(pg["function"]) for p in projects for pg in p["testcode"]))

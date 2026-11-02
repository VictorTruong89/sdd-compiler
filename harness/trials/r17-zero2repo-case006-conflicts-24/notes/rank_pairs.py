"""Rank each planted pair with the compiler's own scoring, from both ends. No model call.

    python3 notes/rank_pairs.py work/compile-planted          -> notes/pair_ranks.json, table on stdout

For each kept item: the node(s) whose text holds the side-A phrase and the side-B phrase
(`PHRASES` in notes/plant.py; a shorter `FIND` override where the atomizer split the phrase);
for each A/B node pair, the rank of the other end in each node's ranked candidate list (F5 §4.3:
score, then node id; below `min_score` dropped), the score and the sources that fired, and
whether `compile_to_pairs.py` recorded the pair among the proposed pairs. A pair is proposed when
either rank is within `max_pairs_per_node` (F5 D14).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "src"))
sys.path.insert(0, str(HERE))
from plant import FIND, KEPT, PHRASES                             # noqa: E402
from sdd_compiler.profile import load_profile                     # noqa: E402
from sdd_compiler.retrieval.score import score_of                 # noqa: E402
from sdd_compiler.retrieval.sources import evidence_for, keyword_counts   # noqa: E402


root = Path(sys.argv[1]).resolve()
nodes = {}
for f in (root / ".sdd/nodes").glob("*.jsonl"):
    for line in f.read_text().splitlines():
        if line.strip():
            n = json.loads(line)
            nodes[n["id"]] = n
terms = {}
for line in (root / ".sdd/terms.jsonl").read_text().splitlines():
    if line.strip():
        t = json.loads(line)
        terms[t["id"]] = t
settings = load_profile(root).retrieval
cap = settings.max_pairs_per_node
rarity = keyword_counts(nodes.values())          # F5 D16, as `propose` counts it
proposed = {frozenset((p["a"], p["b"])) for p in json.loads((root / "pairs-proposed.json").read_text())["pairs"]}


def ranking(node_id):
    node, rows = nodes[node_id], []
    for other in nodes.values():
        if other["id"] == node_id:
            continue
        ev = evidence_for(node, other, terms=terms, settings=settings, keyword_counts=rarity)
        if ev and score_of(ev) >= settings.min_score:
            rows.append((score_of(ev), other["id"]))
    rows.sort(key=lambda r: (-r[0], r[1]))
    return {oid: i for i, (_, oid) in enumerate(rows, 1)}, len(rows)


def holding(text):
    return sorted(i for i, n in nodes.items() if text and text in n["text"])


cache, out = {}, {}
for item in KEPT:
    a_text, b_text = FIND.get(item, (None, None))
    a_nodes = holding(a_text or PHRASES[item][0])
    b_nodes = holding(b_text or PHRASES[item][1])
    rows = []
    for a in a_nodes:
        for b in b_nodes:
            for x in (a, b):
                cache.setdefault(x, ranking(x))
            ev = evidence_for(nodes[a], nodes[b], terms=terms, settings=settings, keyword_counts=rarity)
            rows.append({"a": a, "b": b, "score": score_of(ev) if ev else 0.0,
                         "sources": [e["source"] for e in ev],
                         "rank_from_b": cache[b][0].get(a), "of_b": cache[b][1],
                         "rank_from_a": cache[a][0].get(b), "of_a": cache[a][1],
                         "proposed": frozenset((a, b)) in proposed,
                         "family_a": nodes[a]["family"], "family_b": nodes[b]["family"]})
    out[item] = {"a_nodes": a_nodes, "b_nodes": b_nodes, "pairs": rows}
    best = max(rows, key=lambda r: (r["proposed"], r["score"]), default=None)
    if best is None:
        print(f"{item}  NODE NOT FOUND  A={a_nodes} B={b_nodes}")
        continue
    print(f"{item}  {'PROPOSED' if best['proposed'] else 'missed  '}  {best['a']}~{best['b']}  "
          f"score {best['score']:4.1f} {'+'.join(best['sources']) or '-'}  "
          f"rank from B {best['rank_from_b']}/{best['of_b']}, from A {best['rank_from_a']}/{best['of_a']}  "
          f"families {best['family_a']} | {best['family_b']}")
(HERE / "pair_ranks.json").write_text(json.dumps({"cap": cap, "min_score": settings.min_score, "items": out},
                                                 indent=1) + "\n")
print("proposed", sum(any(r["proposed"] for r in v["pairs"]) for v in out.values()), "of", len(KEPT), "cap", cap)

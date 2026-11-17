#!/bin/bash
# Round 28 helper (no model call): score every done run of the three case trials not yet in notes/scores.json,
# and list the done runs not yet in notes/readings.txt (to read).
cd "$(dirname "$0")/../.."
for c in case005 case011 case001; do
  T=r28-zero2repo-$c-conflicts-gaps
  todo=$(python3 - "$T" <<'PY'
import json,sys,csv
T=sys.argv[1]
try: s=json.load(open(f'{T}/notes/scores.json'))
except Exception: s={}
done=[r['run_id'] for r in csv.DictReader(open(f'{T}/queue.tsv'),delimiter='\t') if r['status']=='done']
print(' '.join(f'{T}/runs/{r}' for r in done if r not in s))
PY
)
  [ -n "$todo" ] && (cd $T && python3 notes/score.py $(echo $todo | sed "s#$T/##g") | cut -c1-140)
  python3 - "$T" "$c" <<'PY'
import sys,csv
T,c=sys.argv[1:]
read={l.split('|')[0].strip() for l in open(f'{T}/notes/readings.txt') if l.strip() and not l.startswith('#')}
done=[r['run_id'] for r in csv.DictReader(open(f'{T}/queue.tsv'),delimiter='\t') if r['status']=='done']
print(c,'to read:',' '.join(r.replace(f'r28-{c}-','') for r in done if r.replace(f'r28-{c}-','') not in read))
PY
done

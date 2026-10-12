import json, sys
f = sys.argv[1]
d = json.load(open(f))
c = d.get('conflicts', {})
print({k: d.get(k) for k in ['run','pending','completed','failed','empty_blocks','nodes_formed',
                         'model_calls','cost_usd','replayed','stopped','annotations_dropped']})
print({k: c.get(k) for k in ['candidates','pairs_judged','pairs_replayed','unjudged','unjudged_failed',
                             'suppressed','opened','open','incomplete','stopped']})
print('stop reason:', (d.get('stop_reason') or c.get('stop_reason') or '')[:200])

"""Probes for round 21: which value a built prosecheck takes on each candidate. No model call.

    bash notes/probe.sh <app-dir> [C01 G01 ...]        (runs this file in a container with no network)

Round 21 (new for case016; the method of ../r20-zero2repo-case010-gaps/notes/probe.py). Written from
the spec (PRD, Interface Contract), the answer key and the public surface only, never from the hidden
tests. The public surface is black-box: `python3 <app>/scripts/detect.py` and `node <app>/hooks/<hook>.js`
(the paths the Interface Contract fixes), each in a fresh process with a throwaway config folder. Each
probe prints its own reading:
  - "upstream": the value the original spec states (side A for a conflict, the removed fact for a gap);
  - "alternative": side B, or the alternative of a gap (notes/sides.py);
  - "other: …": anything else.
"not built" = the probe program itself failed (a missing file, a crash): it reads neither value.
Output: one JSON object {item: {"built": ..., "evidence": ...}}. The reading is never detection;
flagging and naming are read from NOTES.md.
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap

APP = sys.argv[1] if len(sys.argv) > 1 else "/app"

PRELUDE = r'''
import glob, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
APP = %r
DET = os.path.join(APP, "scripts", "detect.py")
HOOKS = os.path.join(APP, "hooks")
TMP = tempfile.mkdtemp()
CFG = os.path.join(TMP, "cfg")
os.makedirs(CFG)
T = ("The library opened at nine on most weekdays. Staff kept the reading room quiet, though the children's corner "
     "was louder after school let out and parents gathered near the desk to talk about homework, buses, and the weather. "
     "A new roof went on last spring. Funding came from the county budget and a small grant from a local trust that has "
     "supported the building since it was built.")
SLOP = ("In today's fast-paced world, we delve into the rich tapestry of innovation. I hope this helps! Experts argue that "
        "this pivotal journey will unlock a vibrant landscape of opportunity. It's worth noting that the future looks bright. "
        "In conclusion, this comprehensive guide serves as a testament to the power of seamless collaboration, fostering "
        "growth and highlighting synergy across every team.")

def det(args, inp=b"", cwd=None):
    p = subprocess.run([sys.executable, DET] + args, input=inp, capture_output=True, timeout=60, cwd=cwd or TMP)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

def rep(text):
    rc, o, e = det([], text.encode("utf-8"))
    return json.loads(o)

def nums(text):
    return {k.split("_", 1)[0] for k, v in rep(text).items() if k != "_metrics" and isinstance(v, dict) and v.get("count")}

def score(text):
    return rep(text)["_metrics"]["ai_tell_score"]

def fpath(name, text, binary=False):
    p = os.path.join(TMP, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(text if binary else text.encode("utf-8"))
    return p

def hook(name, ev, env=None, cfg=None):
    e = dict(os.environ, CLAUDE_CONFIG_DIR=cfg or CFG)
    e.pop("CLAUDE_PLUGIN_ROOT", None)
    e.pop("PROSECHECK_DEFAULT_MODE", None)
    e.update(env or {})
    p = subprocess.run(["node", os.path.join(HOOKS, name)], input=json.dumps(ev).encode(), capture_output=True,
                       timeout=120, cwd=TMP, env=e)
    return p.stdout.decode("utf-8", "replace")

def prompt(text, sid="s1", env=None, **kw):
    ev = {"prompt": text, "session_id": sid}
    ev.update(kw)
    out = hook("prosecheck-tracker.js", ev, env)
    try:
        return json.loads(out).get("reason") or ""
    except Exception:
        return out

def write(path, sid="s1"):
    return hook("prosecheck-guard.js", {"tool_name": "Write", "tool_input": {"file_path": path, "content": ""},
                                         "session_id": sid, "cwd": TMP})

def nudge(out):
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""

def say(up, alt, info=""):
    print("upstream" if up else "alternative" if alt else "other: " + str(info)[:200])
'''

PROBES = {
    # ---- conflicts (upstream = side A)
    "C01": "a, b = score(T), score(T + ' It may perhaps rain, and it could possibly snow.'); say(a == b, a != b, (a, b))",
    "C02": ("a = score(T + '\\n\\nOne team met early. Another group argued about the budget for most of the long afternoon. Everyone left.')\n"
            "b = score(T + '\\n\\nThe team met early. The team argued about the budget for most of the long afternoon. The team left.')\n"
            "say(a == b, a != b, (a, b))"),
    "C03": "a, b = score(T + '\\n'), score(T + '   \\n'); say(a == b, a != b, (a, b))",
    "C04": ("W = ' '.join(['Field note %d: the river rose by %d centimetres near bridge %d after the storm, so the crew checked '\n"
            "     'the gauges, logged the reading, and walked back along the levee before noon.' % (i, i * 3 + 7, i + 2) for i in range(1, 9)])\n"
            "W = 'Experts argue the data matter. We delve into them. ' + W\n"
            "m = rep(W)['_metrics']; c = m['confidence']\n"
            "say(c == 'moderate', c == 'high', (c, m.get('words'), len(W.split())))"),
    "C05": ("rc, o, e = det(['--ci'], b'One short line. A second sentence follows here. The third sentence is the longest of these three by far.')\n"
            "ci = json.loads(o)['_metrics'].get('score_ci', 'absent'); say(ci is None, isinstance(ci, list), ci)"),
    "C06": "s = score(T + ' As an AI language model, I cannot browse.'); say(s < 45, s >= 45, s)",
    "C07": "rc, o, e = det(['--bogus']); say(rc == 2, rc == 1, rc)",
    "C08": ("f1, f2 = fpath('a.md', T + ' We delve into it.'), fpath('b.md', T)\n"
            "rc, o, e = det([f1, f2]); n = {k.split('_', 1)[0] for k, v in json.loads(o).items() if k != '_metrics' and v.get('count')}\n"
            "say('1' in n, '1' not in n, (rc, sorted(n)))"),
    "C09": "rc, o, e = det(['--help']); say(rc == 0 and o.startswith('usage: detect.py'), rc == 0 and not o.strip() and 'usage' in e, (rc, o[:40], e[:40]))",
    "C10": ("n = nums('Intro sentence here.\\n\\n> We delve into the tapestry.\\n> It was vibrant and crucial.\\n\\nThe end came quietly.')\n"
            "say('1' not in n, '1' in n, sorted(n))"),
    "C11": "n = nums(T + ' However, the plan held.'); say('37' not in n, '37' in n, sorted(n))",
    "C12": "n = nums(T + ' The shop is open from 9 to 5 every day.'); say('15' not in n, '15' in n, sorted(n))",
    "C13": "n = nums(T + ' See https://example.org/page?utm_source=example.com for details.'); say('65' not in n, '65' in n, sorted(n))",
    "C14": "k = {kk for kk, v in rep(T + ' We left early, no regrets.').items() if isinstance(v, dict) and v.get('count')}; say('17_tailing_negation' not in k, '17_tailing_negation' in k, sorted(k))",
    "C15": "rc, o, e = det(['--clean'], 'Bonjour\\u00a0! Il est 9\\u00a0h.\\n'.encode()); say('\\u00a0!' in o, 'Bonjour !' in o, repr(o))",
    "C16": "rc, o, e = det(['--clean'], b'line one  \\nline two\\n'); say(o == 'line one\\nline two\\n', o == 'line one  \\nline two\\n', repr(o))",
    "C17": ("names = ['f%02d.md' % i for i in range(12)]\n"
            "for nm in names: fpath(nm, SLOP)\n"
            "body = '*** Begin Patch\\n' + ''.join('*** Add File: %s\\n+x\\n' % nm for nm in names) + '*** End Patch\\n'\n"
            "ctx = nudge(hook('prosecheck-guard.js', {'tool_name': 'apply_patch', 'tool_input': {'command': body}, 'session_id': 's1', 'cwd': TMP}))\n"
            "k = sum(1 for nm in names if nm in ctx); say(k == 12, k == 10, k)"),
    "C18": ("for i in range(25): write(fpath('w%02d.md' % i, T + ' Entry %d.' % i))\n"
            "r = prompt('/prosecheck show'); k = len(re.findall(r'(?m)^\\s*w\\d\\d\\.md - ', r)); say(k == 20, k == 25, k)"),
    "C19": ("write(fpath('aged.md', T), sid='old')\n"
            "past = time.time() - 3 * 86400\n"
            "for f in glob.glob(os.path.join(CFG, '.prosecheck-ledger*')): os.utime(f, (past, past))\n"
            "hook('prosecheck-activate.js', {'session_id': 'new'})\n"
            "r = prompt('/prosecheck show', sid='old'); say('aged.md' in r, 'aged.md' not in r, r[:80])"),
    "C20": ("prompt('/prosecheck lite'); r = prompt('/prosecheck status', env={'PROSECHECK_DEFAULT_MODE': 'strict'})\n"
            "say(re.search(r'\\blite\\b', r) and not re.search(r'\\bstrict\\b', r), re.search(r'\\bstrict\\b', r), r)"),
    "C21": ("prompt('please stop prosecheck now'); r = prompt('/prosecheck status')\n"
            "say(re.search(r'\\bfull\\b', r) and not re.search(r'\\boff\\b', r), re.search(r'\\boff\\b', r), r)"),
    "C22": ("tp = fpath('t.jsonl', json.dumps({'type': 'assistant', 'message': {'id': 'm1', 'content': [{'type': 'text', 'text': (T + ' ' + T)[:300]}],\n"
            "  'usage': {'output_tokens': 5, 'cache_read_input_tokens': 7}}}) + '\\n')\n"
            "r = prompt('/prosecheck stats', transcript_path=tp); say('session prose ai_tell_score' in r, 'assistant turns' in r and 'session prose ai_tell_score' not in r, r[:120])"),
    "C23": ("row = lambda i: json.dumps({'type': 'assistant', 'message': {'id': 'm%d' % i, 'content': [{'type': 'text', 'text': 'hi'}], 'usage': {'output_tokens': 1}}})\n"
            "old = fpath('named/old.jsonl', '\\n'.join(row(i) for i in range(3)) + '\\n'); os.utime(old, (1e9, 1e9))\n"
            "os.makedirs(os.path.join(CFG, 'projects', 'p'))\n"
            "open(os.path.join(CFG, 'projects', 'p', 'new.jsonl'), 'w').write(row(9) + '\\n')\n"
            "r = prompt('/prosecheck stats', transcript_path=old); m = re.search(r'assistant turns: (\\d+)', r)\n"
            "k = m and int(m.group(1)); say(k == 3, k == 1, r[:120])"),
    "C25": "a, b = score(T), score(T + ' We fixed it fast, no fluff.'); say(a != b, a == b, (a, b))",
    "C26": ("a = score(T + '\\n\\nThe roof, new last spring, still leaks a little at the corner, so a bucket stays there.')\n"
            "b = score(T + '\\n\\nThe roof \\u2014 new last spring \\u2014 still leaks a little at the corner, so a bucket stays there.')\n"
            "say(a == b, a != b, (a, b))"),
    # ---- gaps (upstream = the removed fact)
    "G01": "n = nums(T + ' This is genuinely good.'); say('2' not in n, '2' in n, sorted(n))",
    "G02": "n = nums(T + ' We del\\u200bve into it.'); say('1' in n, '1' not in n, sorted(n))",
    "G03": "n = nums(T + ' We d\\u0435lve into it.'); say('1' in n, '1' not in n, sorted(n))",
    "G04": "rc, o, e = det([], b'hello world\\x00 and more plain text here'); say(rc == 1 and not o.strip(), rc == 0, (rc, o[:60]))",
    "G05": ("n = nums('Intro sentence here.\\n\\n    We delve into the tapestry.\\n\\nThe end came quietly.')\n"
            "say('1' not in n, '1' in n, sorted(n))"),
    "G06": "rc, o, e = det(['--clean'], b'\\n\\n    indented line\\nnext\\n'); say(o == '    indented line\\nnext\\n', o == 'indented line\\nnext\\n', repr(o))",
    "G07": "rc, o, e = det(['--clean', fpath('crlf.md', 'a b\\r\\nc d\\r\\n')]); say(o == 'a b\\r\\nc d\\r\\n', o == 'a b\\nc d\\n', repr(o))",
    "G08": ("p = os.path.join(TMP, 'book.epub'); z = zipfile.ZipFile(p, 'w'); z.writestr('mimetype', 'application/epub+zip')\n"
            "for nm, t in (('chap2', 'Second chapter words.'), ('chap10', 'Tenth chapter words.')):\n"
            "    z.writestr('OEBPS/%s.xhtml' % nm, '<html xmlns=\"http://www.w3.org/1999/xhtml\"><body><p>%s</p></body></html>' % t)\n"
            "z.close(); rc, o, e = det(['--clean', p]); i, j = o.find('Second'), o.find('Tenth')\n"
            "say(0 <= i < j, 0 <= j < i, (rc, repr(o[:80])))"),
    "G09": ("p = fpath('short.md', 'As an AI language model, I hope this helps. Insert [Your Name] here.')\n"
            "say(not nudge(write(p)), bool(nudge(write(p))), rep(open(p).read())['_metrics'])"),
    "G10": "o = nudge(write(fpath('CLAUDE.md', SLOP))); say(not o, 'CLAUDE.md' in o, o[:80])",
    "G11": "o = nudge(write(fpath('memory/notes.md', SLOP))); say(not o, 'notes.md' in o, o[:80])",
    "G12": ("write(fpath('perm.md', T))\n"
            "ms = [os.stat(f).st_mode & 0o777 for f in glob.glob(os.path.join(CFG, '.prosecheck-ledger*'))]\n"
            "say(ms and all(m & 0o077 == 0 for m in ms), ms and any(m & 0o077 for m in ms), [oct(m) for m in ms])"),
    "G13": ("row = lambda: json.dumps({'type': 'assistant', 'message': {'id': 'same', 'content': [{'type': 'text', 'text': 'hi'}], 'usage': {'output_tokens': 2}}})\n"
            "tp = fpath('dup.jsonl', row() + '\\n' + row() + '\\n'); r = prompt('/prosecheck stats', transcript_path=tp)\n"
            "m = re.search(r'assistant turns: (\\d+)', r); k = m and int(m.group(1)); say(k == 1, k == 2, r[:120])"),
    "G14": ("fpath('slop.md', SLOP); body = '*** Begin Patch\\nnote *** Add File: slop.md\\n*** End Patch\\n'\n"
            "o = nudge(hook('prosecheck-guard.js', {'tool_name': 'apply_patch', 'tool_input': {'command': body}, 'session_id': 's1', 'cwd': TMP}))\n"
            "say(not o, 'slop.md' in o, o[:80])"),
    "G19": "s = score('As an AI language model, I hope this helps. Insert [Your Name] here.'); say(s >= 65, s < 65, s)",
    "G21": "m = rep('Plain words a\\u00a0b here and there.')['_metrics']; say(m['invisible_chars'] == 0, m['invisible_chars'] > 0, m)",
    "G24": "r = rep(T); z = [k for k, v in r.items() if k != '_metrics' and not v.get('count')]; say(not z, bool(z), z[:5])",
    "G25": ("r = rep(T + ' We delve here. They delve there. You delve now. I delve later. All delve together.')\n"
            "k = max([len(v.get('samples', [])) for kk, v in r.items() if kk != '_metrics'] or [0]); say(k <= 3, k > 3, k)"),
    "G30": ("nd = os.path.join(TMP, 'nodeonly'); os.makedirs(nd); os.symlink(shutil.which('node'), os.path.join(nd, 'node'))\n"
            "r = prompt('/prosecheck doctor', env={'PATH': nd})\n"
            "ln = [l for l in r.splitlines() if 'detector' in l.lower() and 'python' not in l.lower()]\n"
            "say(ln and '[OK]' in ln[0], ln and '[OK]' not in ln[0] or not ln, r[:300])"),
    "G33": ("w = os.path.join(TMP, 'w'); a = hook('prosecheck-activate.js', {}, cfg=w); b = hook('prosecheck-activate.js', {}, cfg=w)\n"
            "wl = [l for l in a.splitlines() if l.strip() and l not in b.splitlines()]\n"
            "fpath('blocker', 'x'); u = hook('prosecheck-activate.js', {}, cfg=os.path.join(TMP, 'blocker', 'cfg'))\n"
            "say(wl and not any(l in u.splitlines() for l in wl), wl and any(l in u.splitlines() for l in wl), (len(wl), u[:80]))"),
    "G60": "r = prompt('/prosecheck show', sid='fresh'); say('.docx' in r, '.docx' not in r, r[:120])",
    "G67": "rc, o, e = det([fpath('x.py', T)]); say(rc == 0, rc != 0, (rc, e[:80]))",
}


def run(body):
    with tempfile.TemporaryDirectory() as d:
        prog = os.path.join(d, "prog.py")
        with open(prog, "w", encoding="utf-8") as f:
            f.write(PRELUDE % APP + textwrap.dedent(body) + "\n")
        try:
            p = subprocess.run([sys.executable, prog], capture_output=True, text=True, cwd=d, timeout=300)
            return p.returncode, p.stdout.strip(), p.stderr
        except subprocess.TimeoutExpired:
            return None, "", "timeout"


if __name__ == "__main__":
    items = sys.argv[2:] or list(PROBES)
    out = {}
    for item in items:
        rc, o, e = run(PROBES[item])
        last = o.splitlines()[-1] if o else ""
        if rc != 0 or not last:
            out[item] = {"built": "not built", "evidence": (o + " " + e)[-300:]}
        else:
            built = "upstream" if last == "upstream" else "alternative" if last == "alternative" else "other"
            out[item] = {"built": built, "evidence": last[-200:]}
    print(json.dumps(out))

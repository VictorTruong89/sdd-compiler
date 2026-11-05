"""Secondary hallucination measures on saved builds (round 20, step 7). No model call. Descriptive only.

    python3 notes/hallu_static.py            (from the trial folder)  -> notes/hallu_static.json

Runs on every saved build of rounds 13c-20 (`../r1*/runs/*/app.tgz` and this round's `runs/`); a run
with no code is skipped and counted. Three measures, each descriptive (no test of significance):

1. **Packages** (after Spracklen et al. 2025, package hallucination): every top-level import in the
   agent's code that is not the standard library (`sys.stdlib_module_names`), not the agent's own
   package or modules, and not declared in its `pyproject.toml` / `requirements*`; for each, whether a
   PyPI project of that name exists (`https://pypi.org/pypi/<name>/json`, HTTP 200; cached in
   `work/pypi_cache.json`). Rate = imports with no PyPI project / runs.
   Cannot see: an import whose PyPI name differs from the import name (`yaml` / PyYAML) is read by
   the import name; a name that exists on PyPI but is not what the agent meant counts as existing.
2. **Failure classes** (after CodeHalu, Tian et al. 2025): for each failed hidden test, the exception
   type, from the failure-location line pytest prints at the end of each failure section
   (`<file>:<line>: <ExceptionType>`), else the last `E   ` line. Never the test body. Each failed
   test counted once (the verifier log prints a failing test's section twice).
   Cannot see: why the exception was raised; an AssertionError is a wrong value, not its cause.
3. **Upstream leakage**: the agent's public module, class and function names (no leading `_`, at
   least 4 characters) that also exist in the upstream library (`pip download --no-deps` into
   `work/upstream/`: nltk for case010, click for case006, sloptrim for case016 if on PyPI) **and**
   appear nowhere in the Markdown spec the run was given (the case's `public/`, or the planted /
   gapped copy). Cannot see: whether the name came from memory of upstream or from common naming.
"""
import ast
import io
import json
import re
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

T = Path(__file__).resolve().parents[1]
TRIALS = T.parent
Z = TRIALS.parent / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases"
UP = T / "work/upstream"
OWN = {"case006": "optlyn", "case010": "lingora", "case016": "prosecheck"}
UPSTREAM = {"case006": "click", "case010": "nltk", "case016": "sloptrim"}
ROUNDS = ["r13c-zero2repo-3cases", "r13d-zero2repo-case006-lean-export", "r14-zero2repo-case006-conflicts",
          "r15-zero2repo-case006-conflicts-v2", "r16-zero2repo-case006-conflicts-sonnet",
          "r17-zero2repo-case006-conflicts-24", "r18-zero2repo-case006-notes-both-sides",
          "r19-zero2repo-case010-conflicts", "r20-zero2repo-case010-gaps"]
CASE_OF = {"r13d": "case006", "r14-": "case006", "r15-": "case006", "r16-": "case006", "r17-": "case006",
           "r18-": "case006", "r19-": "case010", "r20-": "case010"}


def spec_dir(trial: str, run: str, case: str) -> Path:
    t = TRIALS / trial
    if trial.startswith("r14-"):
        return t / "work" / ("spec-planted-decisions" if "decisions" in run else "spec-planted")
    if trial.startswith("r16-"):
        return TRIALS / "r15-zero2repo-case006-conflicts-v2/work/spec-planted"
    for name in ("spec-gapped", "spec-planted"):
        if (t / "work" / name).is_dir():
            return t / "work" / name
    return Z / case / "public"


def runs():
    for trial in ROUNDS:
        for r in sorted((TRIALS / trial / "runs").glob("*")):
            if not r.is_dir() or ".earlystop-" in r.name:
                continue
            case = next((c for c in OWN if c in r.name), None) or next(v for k, v in CASE_OF.items() if trial.startswith(k))
            model = "haiku" if "haiku" in r.name else "sonnet" if "sonnet" in r.name else "?"
            fmt = "export" if "export" in r.name else "markdown"
            yield trial, r, case, f"{model} {fmt}"


def py_files(tgz: Path):
    with tarfile.open(tgz) as tar:
        for m in tar.getmembers():
            if m.isfile():
                yield m.name.lstrip("./"), tar.extractfile(m).read()


def parse(src: bytes):
    try:
        return ast.parse(src)
    except (SyntaxError, ValueError):
        return None


def declared(files: dict) -> set:
    names = set()
    for name, data in files.items():
        base = name.rsplit("/", 1)[-1]
        if base == "pyproject.toml" or base.startswith("requirements"):
            text = data.decode(errors="replace")
            for m in re.finditer(r"""["']?([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(?:[<>=!~;].*?)?["']?\s*,?\s*$""", text, re.M):
                names.add(m[1].lower().replace("-", "_").replace(".", "_"))
    return names


PYPI_CACHE = T / "work/pypi_cache.json"
_pypi = json.loads(PYPI_CACHE.read_text()) if PYPI_CACHE.exists() else {}


def on_pypi(name: str) -> bool:
    if name not in _pypi:
        try:
            with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20) as r:
                _pypi[name] = r.status == 200
        except urllib.error.HTTPError as e:
            _pypi[name] = False if e.code == 404 else None
        except Exception:
            _pypi[name] = None
        PYPI_CACHE.write_text(json.dumps(_pypi, indent=1, sort_keys=True))
    return _pypi[name]


def names_in(tree, module: str):
    out = {module.rsplit(".", 1)[-1]}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
    return {n for n in out if not n.startswith("_") and len(n) >= 4}


def upstream_names(case: str):
    pkg = UPSTREAM[case]
    d = UP / pkg
    if not d.exists():
        d.mkdir(parents=True)
        p = subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "--only-binary=:all:", "-d", str(d), pkg],
                           capture_output=True, text=True)
        if p.returncode != 0:
            (d / "NOT_AVAILABLE").write_text(p.stderr[-2000:])
    if (d / "NOT_AVAILABLE").exists():
        return None, None
    wheel = next(d.glob("*.whl"))
    names = set()
    with zipfile.ZipFile(wheel) as z:
        for n in z.namelist():
            if n.endswith(".py"):
                tree = parse(z.read(n))
                if tree:
                    names |= names_in(tree, n[:-3].replace("/", ".").removesuffix(".__init__"))
    return names, wheel.name


def failure_classes(log: Path) -> Counter:
    per_test = {}  # the verifier log prints a failing test's section twice: count each test once
    if not log.exists():
        return Counter()
    cur, last_loc, last_e = None, None, None

    def close():
        if cur:
            per_test[cur] = last_loc or last_e or "other"
    for ln in log.read_text(errors="replace").splitlines():
        m = re.match(r"^_{3,} (test_\S+) _{3,}$", ln)
        if m or ln.startswith("=====") and cur:
            close()
            cur, last_loc, last_e = (m[1] if m else None), None, None
            continue
        if not cur:
            continue
        m = re.match(r"^\S+:\d+: ([A-Za-z_][\w.]*)$", ln)
        if m:
            last_loc = m[1].rsplit(".", 1)[-1]
        m = re.match(r"^E\s+([A-Za-z_][\w.]*)(:|$)", ln)
        if m:
            last_e = m[1].rsplit(".", 1)[-1]
        elif re.match(r"^E\s+assert\b", ln):
            last_e = "AssertionError"
    close()
    return Counter(per_test.values())


CLASSES = ["AttributeError", "ImportError", "NameError", "NotImplementedError", "TypeError", "AssertionError"]


def bucket(exc: str) -> str:
    if exc in ("ImportError", "ModuleNotFoundError"):
        return "ImportError"
    return exc if exc in CLASSES else "other"


def main():
    up = {c: upstream_names(c) for c in UPSTREAM}
    out = {"upstream": {c: (v[1] if v[1] else "not available") for c, v in up.items()}, "runs": {}, "skipped": []}
    for trial, run, case, arm in runs():
        tgz = run / "app.tgz"
        files = dict(py_files(tgz)) if tgz.exists() else {}
        pys = {n: d for n, d in files.items() if n.endswith(".py") and "/tests/" not in "/" + n and not n.split("/")[-1].startswith("test_")}
        if not pys:
            out["skipped"].append(f"{trial}/{run.name}")
            continue
        own = {OWN[case]} | {n.split("/")[0].removesuffix(".py") for n in files}
        dec = declared(files)
        imports, agent_names = set(), set()
        for n, d in pys.items():
            tree = parse(d)
            if tree is None:
                continue
            agent_names |= names_in(tree, n[:-3].replace("/", "."))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])
        third = sorted(i for i in imports if i not in sys.stdlib_module_names and i not in own
                       and i.lower().replace("-", "_") not in dec and i != "__future__")
        pkgs = {i: on_pypi(i) for i in third}
        spec = " ".join(p.read_text(errors="replace") for p in spec_dir(trial, run.name, case).glob("*.md"))
        un, _ = up[case]
        leak = sorted(n for n in agent_names if un is not None and n in un and not re.search(r"\b" + re.escape(n) + r"\b", spec))
        fc, raw = Counter(), failure_classes(run / "final_tests.log")
        for exc, k in raw.items():
            fc[bucket(exc)] += k
        out["runs"][f"{trial}/{run.name}"] = {
            "case": case, "arm": arm, "undeclared_imports": pkgs,
            "nonexistent": [i for i, v in pkgs.items() if v is False],
            "failure_classes": dict(fc), "failure_other_raw": {e: k for e, k in raw.items() if bucket(e) == "other"},
            "agent_public_names": len(agent_names),
            "upstream_only_names": leak if un is not None else None}
    # summaries: per round and arm (rounds 13c-19 together as "earlier"; round 20 apart)
    summ = defaultdict(lambda: {"runs": 0, "nonexistent": 0, "undeclared": 0, "fail": Counter(), "other": Counter(), "leak": [], "names": []})
    for key, r in out["runs"].items():
        group = ("r20 " if key.startswith("r20-") else "r13c-r19 ") + r["case"] + " " + r["arm"]
        s = summ[group]
        s["runs"] += 1
        s["nonexistent"] += len(r["nonexistent"])
        s["undeclared"] += len(r["undeclared_imports"])
        s["fail"].update(r["failure_classes"])
        s["other"].update(r["failure_other_raw"])
        if r["upstream_only_names"] is not None:
            s["leak"].append(len(r["upstream_only_names"]))
            s["names"].append(r["agent_public_names"])
    out["summary"] = {g: {"runs": s["runs"], "undeclared_imports": s["undeclared"], "nonexistent_imports": s["nonexistent"],
                          "nonexistent_per_run": round(s["nonexistent"] / s["runs"], 3), "failure_classes": dict(s["fail"]), "other_raw": dict(s["other"].most_common(5)),
                          "upstream_only_names_per_run": s["leak"], "agent_public_names_per_run": s["names"]}
                      for g, s in sorted(summ.items())}
    (T / "notes/hallu_static.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for g, s in out["summary"].items():
        print(g, json.dumps(s))
    print("skipped (no code):", out["skipped"])


if __name__ == "__main__":
    main()

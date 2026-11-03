"""Side probes for round 17's candidate conflicts: which side of each item a built optlyn takes. No model call.

    bash notes/probe.sh <app-dir>          (runs this file in a container with no network)

Written from the answer key (`../ANSWER_KEY.md`) and the Interface Contract's API only, never from the
hidden tests. Each probe runs a tiny program against `<app>/src` in a fresh interpreter and reads only
what is observable from outside: streams, exit status, values, files. It prints one JSON object:
{item: {"side": "A" | "B" | "neither" | "error", "evidence": ...}}. C01-C05 are round 14's probes
P1, P3, P4, P6, P7 unchanged (`../r14-zero2repo-case006-conflicts/notes/probe.py`). A side is never
read as detection; detection is scored from NOTES.md (`TRIAL.md`, "Detection rule").
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap

APP = sys.argv[1] if len(sys.argv) > 1 else "/app"
HEAD = f"import sys, os\nsys.path.insert(0, {os.path.join(APP, 'src')!r})\nimport optlyn\n"


def run(body, env=None, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        prog = os.path.join(d, "prog.py")
        with open(prog, "w") as f:
            f.write(HEAD + textwrap.dedent(body))
        e = {k: v for k, v in os.environ.items() if not k.startswith(("PZ_", "XDG_", "_CLI_COMPLETE", "COMP_"))}
        e.update(env or {})
        try:
            p = subprocess.run([sys.executable, prog], input=stdin, capture_output=True, text=True,
                               env=e, cwd=d, timeout=30)
            return p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired:
            return None, "", "timeout"


def short(*parts):
    return [str(x)[-300:] for x in parts]


def pick(out, a, b):
    """Side from two markers in the output: A when only a appears, B when only b."""
    ha, hb = a in out, b in out
    return "A" if ha and not hb else "B" if hb and not ha else "neither" if not (ha or hb) else "error"


def cmd(body, args="[]", env=None, stdin="", extra=""):
    """A one-option command program: `body` is decorators + function; invoked as `c`."""
    return run(textwrap.dedent(body) + f"\nc(args={args}, prog_name='c'{extra})\n", env=env, stdin=stdin)


# ---- C01-C05: round 14's P1, P3, P4, P6, P7 ----

def c01():
    rc, out, err = run("""
        from optlyn.testing import CliRunner
        with CliRunner().isolated_filesystem():
            p = os.getcwd()
        print("EXISTS" if os.path.isdir(p) else "GONE")
    """)
    return pick(out, "GONE", "EXISTS"), short(rc, out, err)


def c02():
    rc, out, err = run("""
        @optlyn.command()
        @optlyn.option("--name", envvar="PZ_NAME")
        def c(name):
            optlyn.echo(f"VALUE={name}")
        c(args=[], prog_name="c", default_map={"name": "from_map"})
    """, env={"PZ_NAME": "from_env"})
    return pick(out, "VALUE=from_env", "VALUE=from_map"), short(rc, out, err)


def c03():
    rc, out, err = run("""
        def cb(ctx, param, value):
            optlyn.echo("CALLED")
            return value
        @optlyn.command()
        @optlyn.option("--x", callback=cb)
        def c(x):
            optlyn.echo(f"X={x}")
        c(args=[], prog_name="c")
    """)
    side = "A" if "CALLED" in out else "B" if "X=None" in out else "error"
    return side, short(rc, out, err)


DOC = "Wrap me. " + "word " * 120


def c04():
    def width(cs):
        rc, out, err = run(f"""
            @optlyn.command(context_settings={cs}, help={DOC!r})
            def c():
                pass
            c(args=["--help"], prog_name="c")
        """, env={"COLUMNS": "200"})
        lines = [ln for ln in (out + err).splitlines() if "word" in ln]
        return (max(map(len, lines)) if lines else None), short(rc, out[-200:], err)
    w, ev = width("{}")
    w_wide, _ = width("{'max_content_width': 150}")
    if w is None:
        side = "error"
    elif w_wide is not None and w_wide <= 80:
        side = "neither"            # detected width not honoured: the default cap cannot be seen
    else:
        side = "A" if w <= 80 else "B" if w <= 100 else "neither"
    return side, {"longest_line": w, "longest_line_with_cap_150": w_wide, "run": ev}


def c05():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--count", type=optlyn.INT)
        def c(count):
            pass
    """, args='["--help"]')
    return pick(out, "--count INTEGER", "--count COUNT"), short(rc, out[-300:], err)


# ---- C06-C28: new in round 17 ----

def c06():
    rc, out, err = cmd("""
        @optlyn.command(help="Before part.\\fAfter part.")
        def c():
            pass
    """, args='["--help"]')
    side = "neither" if "Before part" not in out else pick(out, "Before part", "After part") if "After part" not in out else "B"
    return side, short(rc, out, err)


def c07():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("-v", "--verbose", count=True)
        def c(verbose):
            optlyn.echo(f"V={verbose!r}")
    """)
    return pick(out, "V=0", "V=None"), short(rc, out, err)


def c08():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--tag", multiple=True)
        def c(tag):
            optlyn.echo(f"T={tag!r}")
    """)
    return pick(out, "T=()", "T=None"), short(rc, out, err)


def c09():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--name", envvar=["PZ_FIRST", "PZ_SECOND"])
        def c(name):
            optlyn.echo(f"N={name}")
    """, env={"PZ_FIRST": "one", "PZ_SECOND": "two"})
    return pick(out, "N=one", "N=two"), short(rc, out, err)


def c10():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--feature", is_flag=True, envvar="PZ_FEATURE")
        def c(feature):
            optlyn.echo(f"F={feature!r}")
    """, env={"PZ_FEATURE": "maybe"})
    side = "A" if rc == 2 and "F=" not in out else "B" if "F=False" in out else "neither"
    return side, short(rc, out, err)


def c11():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--name", envvar="PZ_NAME", default="dflt")
        def c(name):
            optlyn.echo(f"N={name!r}")
    """, env={"PZ_NAME": ""})
    return pick(out, "N='dflt'", "N=''"), short(rc, out, err)


def c12():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--when", type=optlyn.DateTime(formats=["%Y-%m-%d", "%Y-%d-%m"]))
        def c(when):
            optlyn.echo(f"M={when.month}")
    """, args='["--when", "2020-01-02"]')
    return pick(out, "M=1", "M=2"), short(rc, out, err)


def c13():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--when", type=optlyn.DateTime(formats=["%d/%m/%Y"]))
        def c(when):
            optlyn.echo(f"W={when.year}")
    """, args='["--when", "2020-01-02"]')
    side = "A" if rc == 2 and "W=" not in out else "B" if "W=2020" in out else "neither"
    return side, short(rc, out, err)


def c14():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--n", type=optlyn.IntRange(0, 10, max_open=True, clamp=True))
        def c(n):
            optlyn.echo(f"N={n}")
    """, args='["--n", "15"]')
    return pick(out, "N=9", "N=10"), short(rc, out, err)


def c15():
    rc, out, err = run("""
        try:
            t = optlyn.FloatRange(0, 1, max_open=True, clamp=True)
        except Exception as exc:
            print("REFUSED", type(exc).__name__)
        else:
            print("VALUE", t.convert("5", None, None))
    """)
    side = "A" if "REFUSED" in out else "B" if "VALUE 1" in out else "neither"
    return side, short(rc, out, err)


def c16():
    rc, out, err = run("""
        v = optlyn.prompt("Name", default="dflt")
        print(f"\\nV={v}")
    """, stdin="\nlater\n")
    return pick(out, "V=dflt", "V=later"), short(rc, out, err)


def c17():
    rc, out, err = run("""
        try:
            v = optlyn.prompt("Secret", confirmation_prompt=True)
            print(f"\\nV={v}")
        except optlyn.Abort:
            print("\\nABORTED")
    """, stdin="aa\nbb\ncc\ncc\n")
    return pick(out, "V=cc", "ABORTED"), short(rc, out, err)


def c18():
    rc, out, err = run("""
        try:
            v = optlyn.prompt("Number", type=optlyn.INT)
            print(f"\\nV={v}")
        except optlyn.Abort:
            print("\\nABORTED")
        except Exception as exc:
            print("\\nFAILED", type(exc).__name__)
    """, stdin="abc\n5\n")
    return pick(out, "V=5", "FAILED"), short(rc, out, err)


def c19():
    rc, out, err = run("""
        with open("target.txt", "w") as f:
            f.write("keep")
        @optlyn.command()
        @optlyn.option("--out", type=optlyn.File("w"))
        def c(out):
            pass
        try:
            c(args=["--out", "target.txt"], prog_name="c")
        except SystemExit:
            pass
        print("CONTENT=" + open("target.txt").read() + "|")
    """)
    return pick(out, "CONTENT=keep|", "CONTENT=|"), short(rc, out, err)


def c20():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--p", type=optlyn.Path(resolve_path=True))
        def c(p):
            optlyn.echo(f"P={p}")
    """, args='["--p", "~/x"]', env={"HOME": "/tmp/pzhome"})
    side = "A" if "/~/x" in out else "B" if "P=/tmp/pzhome/x" in out else "neither"
    return side, short(rc, out, err)


def c21():
    rc, out, err = run("""
        print("D=" + optlyn.get_app_dir("Foo Bar"))
    """, env={"XDG_CONFIG_HOME": "/tmp/pzxdg", "HOME": "/tmp/pzhome"})
    return pick(out, "D=/tmp/pzxdg/foo-bar", "D=/tmp/pzhome/.config/foo-bar"), short(rc, out, err)


def c22():
    rc, out, err = run("""
        optlyn.pause()
        print("DONE")
    """)
    side = "A" if out.strip() == "DONE" else "B" if "DONE" in out and out.strip() != "DONE" else "error"
    return side, short(rc, out, err)


def c23():
    rc, out, err = run("""
        @optlyn.group()
        @optlyn.option("--opt")
        def cli(opt):
            pass
        @cli.command()
        def sub():
            pass
        cli(prog_name="cli")
    """, env={"_CLI_COMPLETE": "bash_complete", "COMP_WORDS": "cli ", "COMP_CWORD": "1"})
    if "sub" not in out:
        return "error", short(rc, out, err)
    return ("B" if "--opt" in out else "A"), short(rc, out, err)


def c24():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.pass_context
        def c(ctx):
            ctx.exit()
    """)
    side = "error" if "Traceback" in err else "A" if rc == 0 else "B" if rc == 1 else "neither"
    return side, short(rc, out, err)


def c25():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--flag", is_flag=True, show_default=True, help="A flag.")
        def c(flag):
            pass
    """, args='["--help"]')
    line = next((ln for ln in out.splitlines() if "--flag" in ln), "")
    side = "error" if not line else "B" if "default" in line.lower() else "A"
    return side, short(rc, out, err)


def c26():
    rc, out, err = run("""
        @optlyn.group()
        def cli():
            pass
        @cli.command()
        def sub():
            \"\"\"Do it. Then more.\"\"\"
        cli(args=["--help"], prog_name="cli")
    """)
    line = next((ln for ln in out.splitlines() if ln.strip().startswith("sub")), "")
    side = "error" if not line else "B" if "Then more" in line else "A" if "Do it." in line else "neither"
    return side, short(rc, out, err)


def c27():
    rc, out, err = cmd("""
        @optlyn.command(help="DESCTEXT", epilog="EPILOGTEXT")
        @optlyn.option("--x", help="xhelp")
        def c(x):
            pass
    """, args='["--help"]')
    if "EPILOGTEXT" not in out or "xhelp" not in out:
        return "error", short(rc, out, err)
    return ("A" if out.index("EPILOGTEXT") > out.index("xhelp") else "B"), short(rc, out, err)


def c28():
    rc, out, err = cmd("""
        @optlyn.command(help="alpha line\\nbeta line")
        def c():
            pass
    """, args='["--help"]')
    side = "A" if "alpha line beta line" in out else "B" if any(
        ln.strip() == "alpha line" for ln in out.splitlines()) else "neither"
    return side, short(rc, out, err)


def r3():
    rc, out, err = run("""
        v = optlyn.confirm("Go?", default=True)
        print(f"\\nV={v}")
    """, stdin="\n")
    return pick(out, "V=True", "V=False"), short(rc, out, err)


def c29():
    rc, out, err = cmd("""
        @optlyn.command()
        @optlyn.option("--c", type=optlyn.Choice(["Red"]))
        def c(c):
            optlyn.echo(f"C={c}")
    """, args='["--c", "red"]')
    side = "A" if rc == 2 and "C=" not in out else "B" if "C=Red" in out else "neither"
    return side, short(rc, out, err)


PROBES = {f"C{i:02d}": globals()[f"c{i:02d}"] for i in range(1, 30)} | {"R3": r3}
result = {}
for name, fn in PROBES.items():
    try:
        side, evidence = fn()
    except Exception as exc:          # a probe must never stop the others
        side, evidence = "error", repr(exc)
    result[name] = {"side": side, "evidence": evidence}
print(json.dumps(result))

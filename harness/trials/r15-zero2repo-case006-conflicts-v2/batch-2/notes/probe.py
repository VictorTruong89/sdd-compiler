"""Side probes for the planted conflicts: which side of each item a built optlyn takes. No model call.

    docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v <app>:/app:ro -v <notes>:/probe:ro \
        python:3.13-slim python3 -I /probe/probe.py /app

Written from the answer key (`../ANSWER_KEY.md`) and the Interface Contract's API only, never from the
hidden tests. Each probe runs a tiny program against `<app>/src` in a fresh interpreter and reads only
what is observable from outside: streams, exit, values, files. It prints one JSON object:
{item: {"side": "A" | "B" | "both" | "neither" | "error", "evidence": ...}}. A side is never read as
detection (an agent can land on A from memory of click); detection is scored separately.
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
        e = {k: v for k, v in os.environ.items() if not k.startswith(("P3_", "TOOL_"))}
        e.update(env or {})
        try:
            p = subprocess.run([sys.executable, prog], input=stdin, capture_output=True, text=True,
                               env=e, cwd=d, timeout=30)
            return p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired:
            return None, "", "timeout"


def short(*parts):
    return [str(x)[-300:] for x in parts]


def p1():
    rc, out, err = run("""
        from optlyn.testing import CliRunner
        with CliRunner().isolated_filesystem():
            p = os.getcwd()
        print("EXISTS" if os.path.isdir(p) else "GONE")
    """)
    side = "A" if "GONE" in out else "B" if "EXISTS" in out else "error"
    return side, short(rc, out, err)


def p2():
    rc, out, err = run("""
        @optlyn.command(deprecated=True)
        def old():
            optlyn.echo("BODY")
        old(args=[], prog_name="old")
    """)
    o, e = "deprecat" in out.lower(), "deprecat" in err.lower()
    side = "A" if e and not o else "B" if o and not e else "both" if o and e else "neither"
    rc2, out2, err2 = run("""
        @optlyn.command()
        @optlyn.option("--old-flag", deprecated=True)
        def c(old_flag):
            optlyn.echo("BODY")
        c(args=["--old-flag", "x"], prog_name="c")
    """)
    option = ("stdout " if "deprecat" in out2.lower() else "") + ("stderr" if "deprecat" in err2.lower() else "")
    return side, {"command": short(rc, out, err), "option_warning_on": option.strip() or "none"}


def p3():
    rc, out, err = run("""
        @optlyn.command()
        @optlyn.option("--name", envvar="P3_NAME")
        def c(name):
            optlyn.echo(f"VALUE={name}")
        c(args=[], prog_name="c", default_map={"name": "from_map"})
    """, env={"P3_NAME": "from_env"})
    side = "A" if "VALUE=from_env" in out else "B" if "VALUE=from_map" in out else "error"
    return side, short(rc, out, err)


def p4():
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


P5 = """
    @optlyn.group()
    def cli():
        pass
    @cli.command()
    @optlyn.option("--user-name")
    def greet(user_name):
        optlyn.echo(f"USER={user_name}")
    cli(args=["greet"], prog_name="cli", auto_envvar_prefix="TOOL")
"""


def p5():
    _, out_a, err_a = run(P5, env={"TOOL_GREET_USER_NAME": "short"})
    _, out_b, err_b = run(P5, env={"TOOL_CLI_GREET_USER_NAME": "long"})
    a, b = "USER=short" in out_a, "USER=long" in out_b
    side = "A" if a and not b else "B" if b and not a else "both" if a and b else "neither"
    return side, {"short_key": short(out_a, err_a), "long_key": short(out_b, err_b)}


DOC = "Wrap me. " + "word " * 120


def p6():
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


def p7():
    rc, out, err = run("""
        @optlyn.command()
        @optlyn.option("--count", type=optlyn.INT)
        def c(count):
            pass
        c(args=["--help"], prog_name="c")
    """)
    a, b = "--count INTEGER" in out, "--count COUNT" in out
    side = "A" if a and not b else "B" if b and not a else "neither"
    return side, short(rc, out[-300:], err)


def r1():
    rc, out, err = run("""
        v = optlyn.confirm("Go?")
        optlyn.echo(f"RESULT={v}")
    """, stdin="maybe\ny\n")
    side = "A" if "RESULT=True" in out else "B" if "RESULT=False" in out else "error"
    return side, short(rc, out, err)


def r2():
    rc, out, err = run("""
        @optlyn.command()
        @optlyn.option("--x")
        def c(x):
            optlyn.echo("RAN")
        c(args=[], prog_name="c")
    """)
    side = "A" if "RAN" in out else "B" if "usage" in (out + err).lower() else "error"
    return side, short(rc, out, err)


result = {}
for name, fn in [("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4), ("P5", p5), ("P6", p6), ("P7", p7), ("R1", r1), ("R2", r2)]:
    try:
        side, evidence = fn()
    except Exception as exc:          # a probe must never stop the others
        side, evidence = "error", repr(exc)
    result[name] = {"side": side, "evidence": evidence}
print(json.dumps(result))

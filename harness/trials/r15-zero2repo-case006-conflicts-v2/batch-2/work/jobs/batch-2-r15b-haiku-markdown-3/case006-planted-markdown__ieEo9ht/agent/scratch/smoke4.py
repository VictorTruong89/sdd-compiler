import os, sys, optlyn as ol
from optlyn.testing import CliRunner
r = CliRunner()

@ol.command()
@ol.option("--alpha", default=1, type=int)
@ol.option("--beta-x", envvar=["BX1", "BX2"], default="d")
@ol.option("--nope", allow_from_autoenv=False)
def top(alpha, beta_x, nope):
    ol.echo(f"{alpha} {beta_x} {nope}")
    print(ol.get_current_context().get_parameter_source("alpha"), file=sys.stderr)
print("DM", r.invoke(top, [], default_map={"alpha": 5, "nope": "zz"}).output)
print("AUTO", r.invoke(top, [], auto_envvar_prefix="MYAPP", env={"MYAPP_ALPHA": "7", "MYAPP_NOPE": "no", "BX2": "bx2"}).output)
print("ENV-ORDER", r.invoke(top, ["--alpha", "3"], env={"BX1": "", "BX2": "bx2"}).output)

@ol.group()
def grp():
    pass
@grp.command()
@ol.option("--v", default=0, type=int)
def sub(v):
    ol.echo(f"v={v}")
print("DM2", r.invoke(grp, ["sub"], default_map={"sub": {"v": 9}}).output)

@ol.command()
@ol.option("--a", default=1)
@ol.pass_context
def inner(ctx, a):
    ol.echo(f"inner a={a}")
    return a

@ol.command()
@ol.option("--a", default=2)
@ol.pass_context
def outer(ctx, a):
    ctx.invoke(inner, a=a * 10)
    ctx.forward(inner)
print("INV", r.invoke(outer, []).output)

print("STYLE", repr(ol.style("x", fg="red", bold=True)), repr(ol.unstyle(ol.style("x", fg=(1,2,3), bg=200))))
try:
    ol.style("x", fg="nope")
except ValueError as e:
    print("BADCOLOR ok", e)

@ol.command()
def pb():
    with ol.progressbar(range(3), label="work") as bar:
        for _ in bar:
            pass
    ol.echo("done")
print("PB", repr(r.invoke(pb, []).output))

@ol.command()
def ab():
    ol.echo("start")
    raise ol.Abort()
res = r.invoke(ab, [])
print("ABORT", res.exit_code, repr(res.output))

@ol.command()
def ex():
    ol.echo("x")
    ol.get_current_context().exit(4)
print("EXIT", r.invoke(ex, []).exit_code)

@ol.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@ol.argument("items", nargs=-1)
def loose(items):
    ol.echo(repr(items))
print("LOOSE", r.invoke(loose, ["a", "--zzz", "b"]).output)
print("LOOSE2", r.invoke(loose, ["a", "-zq"]).output)

@ol.command(context_settings={"help_option_names": ["-h", "--halp"]})
def hh():
    pass
print("HH", r.invoke(hh, ["-h"]).exit_code, r.invoke(hh, ["--help"]).exit_code)

class Upper(ol.ParamType):
    name = "upper"
    def convert(self, value, param, ctx):
        if not isinstance(value, str):
            return value
        if value.isupper():
            return value
        self.fail(f"{value} must be upper", param, ctx)

@ol.command()
@ol.option("--u", type=Upper())
@ol.option("--pair", type=ol.Tuple([str, int]), default=None)
@ol.option("--when", type=ol.DateTime())
@ol.option("--fr", type=ol.FloatRange(0.0, 1.0, min_open=True))
def typed(u, pair, when, fr):
    ol.echo(repr((u, pair, when, fr)))
print("TYPED", r.invoke(typed, ["--u", "AB", "--pair", "x", "3", "--when", "2024-01-02 03:04:05"]).output)
print("TYPED2", r.invoke(typed, ["--u", "ab"]).output.splitlines()[-1])
print("TYPED3", r.invoke(typed, ["--fr", "0.0"]).output.splitlines()[-1])
print("TYPED4", r.invoke(typed, ["--pair", "a", "3", "--when", "2024-01-02T10:00:00"]).exit_code)

@ol.command()
@ol.option("--n", type=int)
def stand(n):
    return n * 2
print("NONSTD", stand.main(["--n", "4"], standalone_mode=False))
print("NONSTD2", stand.main(["--n", "x"], standalone_mode=False) if False else "skip")

@ol.command()
@ol.option("--x", default=1)
def fdcap(x):
    os.write(1, b"osline\n")
    ol.echo("py line", err=True)
res = CliRunner(capture="fd").invoke(fdcap, [])
print("FD", repr(res.stdout), repr(res.stderr))
res = CliRunner().invoke(fdcap, [])
print("SYS", repr(res.stdout), repr(res.stderr))
print("ASCII", CliRunner(charset="ascii").invoke(ol.command()(lambda: ol.echo("héllo")), []).output)

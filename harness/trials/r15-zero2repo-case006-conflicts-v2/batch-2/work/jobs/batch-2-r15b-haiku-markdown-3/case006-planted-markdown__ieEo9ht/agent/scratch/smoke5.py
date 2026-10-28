import os, sys, optlyn as ol
from optlyn.testing import CliRunner
r = CliRunner()

class Lazy(ol.Group):
    loads = []
    def list_commands(self, ctx):
        return ["alpha", "beta"]
    def get_command(self, ctx, name):
        Lazy.loads.append(name)
        if name == "alpha":
            @ol.command()
            def alpha():
                """Alpha command. More."""
                ol.echo("alpha ran")
            return alpha
        return None

lz = ol.group(cls=Lazy)(lambda: None)
print("LAZY-HELP", r.invoke(lz, ["--help"]).output.strip().splitlines()[-3:], Lazy.loads)
Lazy.loads.clear()
print("LAZY-RUN", r.invoke(lz, ["alpha"]).output, Lazy.loads)

@ol.command()
def one():
    ol.echo("one")
@ol.command()
def two():
    ol.echo("two")
coll_src = ol.group()(lambda: ol.echo("coll cb"))
coll = ol.group(cls=ol.CommandCollection, sources=[])(lambda: ol.echo("collection"))
coll.sources = [ol.Group(commands=[one]), ol.Group(commands=[two])]
print("COLL", r.invoke(coll, ["two"]).output, r.invoke(coll, ["--help"]).output.splitlines()[-4:])

@ol.command()
@ol.option("--hid", hidden=True, is_flag=True)
@ol.option("--vis", is_flag=True)
def hidc(hid, vis):
    ol.echo(f"{hid} {vis}")
print("HIDDEN", r.invoke(hidc, ["--hid"]).output, "--hid" in r.invoke(hidc, ["--help"]).output)

@ol.command()
@ol.option("--a", "dst", is_flag=True, default=False)
@ol.option("--b", "dst", flag_value=2, is_flag=False, default=None)  # not realistic; keep simple
def fs(dst):
    ol.echo(repr(dst))
@ol.command()
@ol.option("--fast", "speed", flag_value="fast", default=False, is_flag=True)
@ol.option("--slow", "speed", flag_value="slow", default=False, is_flag=True)
def fsw(speed):
    ol.echo(repr(speed))
print("FSW", r.invoke(fsw, ["--fast"]).output, r.invoke(fsw, ["--slow", "--fast"]).output, r.invoke(fsw, []).output)

@ol.command()
@ol.option("--order", "-o", is_flag=True)
@ol.option("--check", is_flag=True, is_eager=True, callback=lambda ctx, p, v: ol.echo("eager-check") if v else None, expose_value=False)
def eager(order):
    ol.echo("body")
print("EAGER", r.invoke(eager, ["--check"]).output)

@ol.command()
@ol.password_option()
def login(password):
    ol.echo(f"len={len(password)}")
print("PWOPT", r.invoke(login, [], input="pw\npw\n").output)

class Obj:
    def __init__(self): self.v = 0
@ol.group()
@ol.pass_context
def root(ctx):
    ctx.obj = Obj()
pass_obj = ol.make_pass_decorator(Obj, ensure=False)
@root.command()
@pass_obj
def use(obj):
    ol.echo(f"obj v={obj.v}")
print("OBJ", r.invoke(root, ["use"]).output, r.invoke(root, ["use"]).exception)

@ol.command()
@ol.argument("pts", nargs=2, type=int)
@ol.argument("tail", required=False, default="zz")
def args2(pts, tail):
    ol.echo(repr((pts, tail)))
print("ARGS2", r.invoke(args2, ["1", "2"]).output, r.invoke(args2, ["1"]).output.splitlines()[-1])

print("APPDIR", ol.get_app_dir("My App"), ol.get_app_dir("My App", force_posix=True))
print("FN", ol.format_filename("a/b.txt", shorten=True), ol.format_filename(b"x\xff.bin"))

class Cfg: pass
@ol.command()
@ol.option("--n", type=int, default=2)
def nonstd(n):
    raise ValueError("boom")
res = r.invoke(nonstd, [])
print("EXC", res.exit_code, repr(res.exception))
res = r.invoke(nonstd, [], catch_exceptions=False) if False else None

print("ECHOSTYLE", repr(r.invoke(ol.command()(lambda: ol.secho("hi", fg="green")), []).output))
print("PAGER-NI", repr(r.invoke(ol.command()(lambda: ol.echo_via_pager(["a", "b"])), []).output))
print("PAUSE", repr(r.invoke(ol.command()(lambda: ol.pause()), []).output))
print("CONFIRM-NOABORT", r.invoke(ol.command()(lambda: ol.echo(ol.confirm("ok?", default=True))), [], input="\n").output)

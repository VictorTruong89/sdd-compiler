import os, optlyn as ol
from optlyn.testing import CliRunner
r = CliRunner()

@ol.command()
@ol.option("-n", "--n", count=True)
@ol.option("--name", envvar="NM", required=True)
@ol.option("--flag/--no-flag", envvar="FLG", default=False, show_default=True)
@ol.option("--mode", type=ol.Choice(["Fast", "Slow"], case_sensitive=False), default="Fast")
@ol.option("--tag", multiple=True, show_default=True)
def cmd(n, name, flag, mode, tag):
    ol.echo(repr((n, name, flag, mode, tag)))
    ctx = ol.get_current_context()
    ol.echo(ctx.get_parameter_source("name"))
    ol.echo(ctx.get_parameter_source("flag"))

print("A", r.invoke(cmd, ["-nn", "--tag", "x"], env={"NM": "envname", "FLG": "yes"}).output)
print("A2", r.invoke(cmd, ["--name", "n", "--flag", "--no-flag"]).output)
res = r.invoke(cmd, ["--help"], prog_name="p")
print("HELP", res.output)
print("BADFLAG", r.invoke(cmd, ["--name", "n"], env={"FLG": "maybe"}).output)

@ol.command()
@ol.option("--shout/--quiet", default=False, envvar="SH")
def s(shout):
    ol.echo(shout)
print("S", r.invoke(s, [], env={"SH": "1"}).output, r.invoke(s, [], env={"SH": "  "}).output, r.invoke(s, [], env={"SH": "off"}).output)

@ol.command(deprecated=True)
@ol.option("--old", deprecated=True)
def dep(old):
    ol.echo("body")
print("DEP", r.invoke(dep, ["--old", "1"]).output)
print("DEP2", r.invoke(dep, []).output)
print("HELPDEP", r.invoke(dep, ["--help"]).output)

@ol.group(invoke_without_command=True)
@ol.option("--x", type=int, default=0)
def g(x):
    ctx = ol.get_current_context()
    ol.echo(f"group x={x} sub={ctx.invoked_subcommand}")

@g.command()
def child():
    ol.echo("child")
print("GRP", r.invoke(g, []).output, r.invoke(g, ["child"]).output)

@ol.group()
def outer():
    ol.echo("outer cb")
@outer.group()
def inner():
    ol.echo("inner cb")
@inner.command()
def leaf():
    ol.echo("leaf")
print("NEST", r.invoke(outer, ["inner", "leaf"]).output)
print("NEST2", r.invoke(outer, ["inner"]).exit_code, r.invoke(outer, ["inner"]).output)

@ol.command()
@ol.option("--pw", hide_input=True, prompt=True, confirmation_prompt=True)
def pw(pw):
    ol.echo("pw=" + pw)
print("PW", r.invoke(pw, [], input="secret\nsecret\n").output)
print("PW2", r.invoke(pw, [], input="a\nb\nc\nc\n").output)

@ol.command()
@ol.argument("p", type=ol.Path(exists=True))
def pth(p):
    ol.echo(p)
with r.isolated_filesystem():
    print("PATH", r.invoke(pth, ["nope"]).output)
    open("x", "w").close()
    print("PATH2", r.invoke(pth, ["x"]).output)

print("ENVHELP", r.invoke(cmd, ["--help"]).output.splitlines()[-4:])

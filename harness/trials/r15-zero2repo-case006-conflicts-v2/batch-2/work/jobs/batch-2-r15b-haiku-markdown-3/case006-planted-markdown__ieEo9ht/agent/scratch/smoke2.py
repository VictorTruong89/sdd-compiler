import os, optlyn as ol
from optlyn.testing import CliRunner
r = CliRunner()

@ol.command()
@ol.option("--name", envvar="NM", required=True)
@ol.option("--tag", multiple=True)
@ol.option("--pair", nargs=2, type=int, default=(0, 0))
@ol.option("--mode", type=ol.Choice(["Fast", "Slow"], case_sensitive=False), default="Fast")
@ol.option("--level", type=ol.IntRange(0, 5, clamp=True), default=1)
@ol.option("-n", "--n", count=True)
@ol.option("--gone/--here", default=True)
@ol.option("--age", prompt=True, type=int)
@ol.argument("rest", nargs=-1)
def cmd(name, tag, pair, mode, level, n, gone, age, rest):
    ol.echo(repr((name, tag, pair, mode, level, n, gone, age, rest)))

print("A", r.invoke(cmd, ["--tag", "a", "--tag", "b", "--pair", "1", "2", "--mode", "fast", "--level", "9",
    "-nn", "--here", "--", "--x", "y"], env={"NM": "envname"}, input="42\n").output)
print("B", r.invoke(cmd, ["--name=x", "--age=3", "--level", "-2"]).output)
print("C", r.invoke(cmd, ["--age", "5"], env={"NM": ""}).exit_code)
res = r.invoke(cmd, ["--age", "5"], env={"NM": ""})
print("C2", res.output)
res = r.invoke(cmd, ["--name", "q"], input="abc\n7\n")
print("D", res.exit_code, res.output)

@ol.group(chain=True)
def pipe():
    pass
@pipe.result_callback()
def done(results):
    ol.echo(f"results={results}")
@pipe.command()
@ol.argument("v", type=int)
def add(v):
    return v + 1
@pipe.command()
@ol.argument("v", type=int)
def mul(v):
    return v * 10
print("E", r.invoke(pipe, ["add", "1", "mul", "5"]).output)

@ol.command()
@ol.confirmation_option(prompt="Sure?")
def danger():
    ol.echo("ran")
print("F", r.invoke(danger, [], input="n\n").output, r.invoke(danger, [], input="y\n").output, r.invoke(danger, ["--yes"]).output)

@ol.command()
@ol.version_option("1.2.3", prog_name="tool")
@ol.option("--x", required=True)
def ver():
    ol.echo("body")
print("G", r.invoke(ver, ["--version"]).output, r.invoke(ver, ["--version", "--help"]).output)

@ol.command()
@ol.argument("f", type=ol.File("w"))
def writer(f):
    f.write("hi\n")
with r.isolated_filesystem() as d:
    res = r.invoke(writer, ["out.txt"])
    print("H", res.exit_code, open("out.txt").read().strip())
    res = r.invoke(writer, ["-"])
    print("H2", res.exit_code, repr(res.output))

@ol.command()
@ol.option("--color", type=ol.Choice(["red", "blue"]))
@ol.option("--kind", type=ol.Choice(["a", "b"]))
def comp(color, kind):
    pass
os.environ["_COMP_COMPLETE"] = "bash_complete"
os.environ["COMP_WORDS"] = "comp --color "
os.environ["COMP_CWORD"] = "2"
print("I", ol.Command and __import__("optlyn.shell_completion", fromlist=["x"]).get_completions(comp, "comp", "bash"))
os.environ.pop("_COMP_COMPLETE")
os.environ["COMP_WORDS"] = "comp --"
os.environ["COMP_CWORD"] = "1"
print("J", [i.value for i in __import__("optlyn.shell_completion", fromlist=["x"]).get_completions(comp, "comp", "bash")])
print("K", r.invoke(comp, ["--bad"], env={"_COMP_COMPLETE": "bash_source"}).output[:80])

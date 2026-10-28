import enum, optlyn as ol
from optlyn.testing import CliRunner
r = CliRunner()

@ol.command()
def ff():
    """Visible.

    \f
    Hidden part.
    """
    pass
print("FF", "Hidden" in r.invoke(ff, ["--help"]).output, "Visible" in r.invoke(ff, ["--help"]).output)

@ol.command(name="renamed")
def orig_name():
    ol.echo("ok")
print("NAME", r.invoke(orig_name, [], prog_name="x").exit_code)

@ol.command()
@ol.option("--opt", is_flag=False, flag_value="FLAG", default="DEF")
def opt(opt):
    ol.echo(opt)
print("OPTIONAL", r.invoke(opt, ["--opt"]).output, r.invoke(opt, ["--opt", "v"]).output, r.invoke(opt, []).output)

@ol.command()
@ol.option("-z", is_flag=True)
@ol.option("-q", is_flag=True)
@ol.argument("rest", nargs=-1)
def stack(z, q, rest):
    ol.echo(f"{z} {q} {rest}")
print("STACK", r.invoke(stack, ["-zq", "x"]).output, r.invoke(stack, ["-zk", "x"], context_settings=None).output if False else "")
res = r.invoke(stack, ["-zk", "x"])
print("STACKUNK", res.exit_code, res.output.strip().splitlines()[-1])

class Color(enum.Enum):
    RED = 1
    GREEN = 2
@ol.command()
@ol.option("--c", type=Color, default="RED", case_sensitive=False) if False else ol.option("--c", type=Color, default="RED")
@ol.option("--many", multiple=True, default=["a", "b"])
@ol.argument("dep", deprecated=True, required=False, default="zz")
def en(c, many, dep):
    ol.echo(repr((c, many, dep)))
print("ENUM", r.invoke(en, ["--c", "GREEN"]).output, r.invoke(en, ["--many", "x"]).output)
print("DEPARG", r.invoke(en, ["q"]).output.splitlines()[0])

@ol.command()
@ol.option("--lvl", type=ol.IntRange(0, 10, min_open=True, clamp=True))
def lv(lvl):
    ol.echo(lvl)
print("LVL", r.invoke(lv, ["--lvl", "0"]).output.strip(), r.invoke(lv, ["--lvl", "50"]).output.strip())

@ol.command()
@ol.option("--tup", type=(int, str))
def tp(tup):
    ol.echo(repr(tup))
print("TUP", r.invoke(tp, ["--tup", "3", "x"]).output.strip())

@ol.command()
@ol.option("--bf", type=ol.BOOL, default=None)
def bf(bf):
    ol.echo(repr(bf))
print("BOOLOPT", r.invoke(bf, ["--bf", "yes"]).output.strip(), r.invoke(bf, ["--bf", "maybe"]).exit_code)

@ol.group(invoke_without_command=True)
def ro():
    ctx = ol.get_current_context()
    ol.echo(f"cb {ctx.invoked_subcommand}")
    return 1
@ro.command()
def rc():
    return 5
@ro.result_callback()
def rcb(value):
    ol.echo(f"result {value}")
print("RO", r.invoke(ro, []).output.strip().splitlines(), r.invoke(ro, ["rc"]).output.strip().splitlines())

@ol.command(add_help_option=False)
@ol.help_option("-h")
def hopt():
    pass
print("HOPT", r.invoke(hopt, ["-h"]).exit_code, r.invoke(hopt, ["--help"]).exit_code)

@ol.command()
@ol.option("--n", type=int, multiple=True)
def mult(n):
    ol.echo(repr(n))
print("MULT", r.invoke(mult, ["--n", "1", "--n", "2"]).output.strip(), r.invoke(mult, []).output.strip())
print("STDIN", r.invoke(ol.command()(lambda: None), [], input="").exit_code)

@ol.command()
@ol.option("--f", type=ol.File("r"))
def rd(f):
    ol.echo(f.read().strip())
with r.isolated_filesystem():
    open("a.txt", "w").write("filedata\n")
    print("READ", r.invoke(rd, ["--f", "a.txt"]).output.strip(), r.invoke(rd, ["--f", "-"], input="fromstdin\n").output.strip())
    res = r.invoke(rd, ["--f", "missing.txt"])
    print("READMISS", res.exit_code, res.output.strip().splitlines()[-1])

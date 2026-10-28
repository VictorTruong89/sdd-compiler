import optlyn as ol
from optlyn.testing import CliRunner

@ol.group()
@ol.option("--verbose", "-v", is_flag=True, help="Be loud.")
@ol.pass_context
def cli(ctx, verbose):
    """Demo tool.

    Long text here.
    """
    ctx.obj = {"verbose": verbose}

@cli.command()
@ol.option("--count", type=int, default=1, show_default=True, help="How many.")
@ol.argument("name")
@ol.pass_obj
def hello(obj, count, name):
    """Say hello. Second sentence."""
    for _ in range(count):
        ol.echo(f"hello {name} verbose={obj['verbose']}")

@cli.command("bye")
@ol.option("--shout/--quiet", default=False)
def bye(shout):
    ol.echo("bye!" if shout else "bye")

r = CliRunner()
for args in [["--help"], ["hello", "--count", "2", "bob"], ["-v", "hello", "x"],
             ["hello"], ["hello", "--count", "x", "y"], ["bye", "--shout"], [], ["nope"], ["bye", "--bogus"]]:
    res = r.invoke(cli, args, prog_name="demo")
    print("==", args, "->", res.exit_code)
    print(res.output)
    if res.exception and not isinstance(res.exception, SystemExit):
        print("EXC", repr(res.exception))

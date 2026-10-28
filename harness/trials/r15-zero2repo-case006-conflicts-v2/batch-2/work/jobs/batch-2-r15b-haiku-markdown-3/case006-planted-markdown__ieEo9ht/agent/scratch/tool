import optlyn as ol

@ol.group(help="Manage things.\n\n\b\nKeep  these\n  lines.")
@ol.version_option("2.0", prog_name="tool")
def cli():
    """Ignored when help given."""

@cli.command(short_help="Make a thing.")
@ol.argument("name", metavar="THING")
@ol.argument("extra", nargs=-1, required=False)
@ol.option("-f", "--force", is_flag=True, help="Overwrite.")
@ol.option("--level", type=ol.Choice(["low", "high"]), default="low", show_default=True, show_envvar=True, envvar="LVL")
def make(name, extra, force, level):
    """Make a THING now. Extra stuff follows."""
    ol.echo(f"made {name} {extra} {force} {level}")

@cli.command()
def fail():
    ol.echo("failing", err=True)
    raise ol.Abort()

if __name__ == "__main__":
    cli()

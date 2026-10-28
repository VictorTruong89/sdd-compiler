import optlyn as ol
from optlyn.testing import CliRunner
@ol.group(epilog="See docs at example.com for more.")
def g():
    """Top level group with a fairly long description that should be wrapped nicely to the terminal width."""
@g.command()
@ol.argument("src", help="Source path to read from.")
@ol.option("-o", "--out", default="x.txt", show_default=True, help="Where to write output.")
def cp(src, out):
    """Copy SRC somewhere."""
r = CliRunner()
print(r.invoke(g, ["--help"], prog_name="tool").output)
print(r.invoke(g, ["cp", "--help"], prog_name="tool").output)

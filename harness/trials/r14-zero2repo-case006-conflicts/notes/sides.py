"""Make one side-B copy of a built optlyn per planted item, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides

The base is round 13c's `sonnet-case006-export-1` build (473 / 476), which takes side A (click's
behaviour) on every item. Each patch is the smallest change that moves that one behaviour to side B;
every anchor must occur exactly once, so a patch never applies silently to the wrong place.
Writes work/sides/<item>/ (a full copy) and work/sides/<item>.tgz (for the oracle task's solution/).
"""
import shutil
import sys
import tarfile
from pathlib import Path

PATCHES = {
    # P1 isolated filesystem without a parent: removed on exit (A) -> always left in place (B)
    "P1": [("src/optlyn/testing.py", "            if temp_dir is None:\n                try:",
            "            if False:\n                try:")],
    # P2 a deprecated command's warning: standard error (A) -> standard output (B)
    "P2": [("src/optlyn/core.py", 'is deprecated.{extra}", fg="red"),\n                 err=True)',
            'is deprecated.{extra}", fg="red"),\n                 err=False)')],
    # P3 environment beats default map (A) -> default map beats environment (B)
    "P3": [("src/optlyn/core.py",
            "        if value is None:\n            value = self.value_from_envvar(ctx)\n"
            "            source = ParameterSource.ENVIRONMENT\n"
            "        if value is None:\n            value = ctx.lookup_default(self.name)\n"
            "            source = ParameterSource.DEFAULT_MAP\n",
            "        if value is None:\n            value = ctx.lookup_default(self.name)\n"
            "            source = ParameterSource.DEFAULT_MAP\n"
            "        if value is None:\n            value = self.value_from_envvar(ctx)\n"
            "            source = ParameterSource.ENVIRONMENT\n")],
    # P4 a parameter callback runs for a missing parameter (A) -> does not (B)
    "P4": [("src/optlyn/core.py",
            "            raise MissingParameter(ctx=ctx, param=self)\n        if self.callback is not None:",
            "            raise MissingParameter(ctx=ctx, param=self)\n"
            "        if self.callback is not None and not self.value_is_missing(value):")],
    # P5 (dropped: footprint 7) top-level command name not in the automatic prefix key (A) -> included (B)
    "P5": [("src/optlyn/core.py", "        else:\n            auto_envvar_prefix = auto_envvar_prefix.upper()",
            "        else:\n            auto_envvar_prefix = (f\"{auto_envvar_prefix}_{self.info_name}\" if parent is None"
            " and self.info_name else auto_envvar_prefix).upper()")],
    # P6 maximum content width defaults to 80 (A) -> 100 (B)
    "P6": [("src/optlyn/formatting.py", "            max_width = 80", "            max_width = 100")],
    # P7 (replaces P5: example against its rule) an INT option's metavar: INTEGER (A) -> its name (B)
    "P7": [("src/optlyn/core.py", "    def make_metavar(self):\n        return super().make_metavar()",
            "    def make_metavar(self):\n        if self.metavar is None and self.type.get_metavar(self) is None:\n"
            "            return (self.name or \"\").upper() + (\"...\" if self.nargs != 1 else \"\")\n"
            "        return super().make_metavar()")],
    # R1 (reserve) confirm: another answer asks again (A) -> counts as no (B)
    "R1": [("src/optlyn/termui.py", '            echo("Error: invalid input", err=err)\n            continue',
            "            rv = False")],
    # R2 (reserve) a leaf with no arguments runs (A) -> shows help (B)
    "R2": [("src/optlyn/core.py", "add_help_option=True, no_args_is_help=False,",
            "add_help_option=True, no_args_is_help=True,")],
}

base, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for item, edits in PATCHES.items():
    dst = out / item
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns("__pycache__"))
    for rel, old, new in edits:
        f = dst / rel
        text = f.read_text(encoding="utf-8")
        assert text.count(old) == 1, (item, rel, text.count(old))
        f.write_text(text.replace(old, new), encoding="utf-8")
    with tarfile.open(out / f"{item}.tgz", "w:gz") as tar:
        tar.add(dst, arcname=".")
    print(item, "ok")
with tarfile.open(out / "BASE.tgz", "w:gz") as tar:
    tar.add(base, arcname=".", filter=lambda t: None if "__pycache__" in t.name else t)
print("BASE ok")

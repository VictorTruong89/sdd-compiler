"""Make one side-B copy of a built optlyn per candidate item, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides            (from the trial folder)

The base is round 13c's `sonnet-case006-export-1` build (473 / 476), the same base as round 14
(`../r14-zero2repo-case006-conflicts/notes/sides.py`); it takes side A on every item. Each patch is
the smallest change that moves that one behaviour to side B. Every anchor must occur exactly once,
so a patch never applies silently to the wrong place. C01-C05 are round 14's P1, P3, P4, P6, P7
with the same patches. Writes work/sides/<item>/ (a full copy) and work/sides/<item>.tgz.
"""
import shutil
import sys
import tarfile
from pathlib import Path

CORE, TYPES, TERM, UTILS, FMT, TEST = ("src/optlyn/core.py", "src/optlyn/types.py", "src/optlyn/termui.py",
                                       "src/optlyn/utils.py", "src/optlyn/formatting.py", "src/optlyn/testing.py")
PATCHES = {
    # C01 (P1) isolated filesystem without a parent: removed on exit (A) -> always left in place (B)
    "C01": [(TEST, "            if temp_dir is None:\n                try:", "            if False:\n                try:")],
    # C02 (P3) environment beats default map (A) -> default map beats environment (B)
    "C02": [(CORE,
             "        if value is None:\n            value = self.value_from_envvar(ctx)\n"
             "            source = ParameterSource.ENVIRONMENT\n"
             "        if value is None:\n            value = ctx.lookup_default(self.name)\n"
             "            source = ParameterSource.DEFAULT_MAP\n",
             "        if value is None:\n            value = ctx.lookup_default(self.name)\n"
             "            source = ParameterSource.DEFAULT_MAP\n"
             "        if value is None:\n            value = self.value_from_envvar(ctx)\n"
             "            source = ParameterSource.ENVIRONMENT\n")],
    # C03 (P4) a parameter callback runs for a missing parameter (A) -> does not (B)
    "C03": [(CORE,
             "            raise MissingParameter(ctx=ctx, param=self)\n        if self.callback is not None:",
             "            raise MissingParameter(ctx=ctx, param=self)\n"
             "        if self.callback is not None and not self.value_is_missing(value):")],
    # C04 (P6) maximum content width defaults to 80 (A) -> 100 (B)
    "C04": [(FMT, "            max_width = 80", "            max_width = 100")],
    # C05 (P7) an INT option's metavar: INTEGER (A) -> its name (B)
    "C05": [(CORE, "    def make_metavar(self):\n        return super().make_metavar()",
             "    def make_metavar(self):\n        if self.metavar is None and self.type.get_metavar(self) is None:\n"
             "            return (self.name or \"\").upper() + (\"...\" if self.nargs != 1 else \"\")\n"
             "        return super().make_metavar()")],
    # C06 form feed in a docstring: truncates (A) -> dropped, the text after it kept (B)
    "C06": [(CORE, 'self.help = inspect.cleandoc(self.help).partition("\\f")[0]',
             'self.help = inspect.cleandoc(self.help).replace("\\f", "")'),
            (CORE, 'text = inspect.cleandoc(self.help).partition("\\f")[0] if',
             'text = inspect.cleandoc(self.help).replace("\\f", "") if')],
    # C07 omitted counting option: 0 (A) -> None (B)
    "C07": [(CORE, "            if self._default_missing:\n                self.default = 0",
             "            if self._default_missing:\n                self.default = None")],
    # C08 omitted repeatable option without default: () (A) -> None (B); variadic arguments unchanged
    "C08": [(CORE, "            return () if (self.multiple or self.nargs == -1) else None",
             "            return () if self.nargs == -1 else None")],
    # C09 list of environment names: first set wins (A) -> last set wins (B)
    "C09": [(CORE, "        for envvar in self.envvar:\n            rv = os.environ.get(envvar)",
             "        for envvar in reversed(self.envvar):\n            rv = os.environ.get(envvar)")],
    # C10 boolean flag, unrecognised environment value: usage error (A) -> turns the flag off (B)
    "C10": [(CORE, "                    return False\n                return rv\n",
             "                    return False\n                return False\n")],
    # C11 environment variable set to an empty string: not a value (A) -> delivers "" (B)
    "C11": [(CORE, "            rv = os.environ.get(self.envvar)\n            return rv if rv else None",
             "            rv = os.environ.get(self.envvar)\n            return rv"),
            (CORE, "        for envvar in self.envvar:\n            rv = os.environ.get(envvar)\n            if rv:",
             "        for envvar in self.envvar:\n            rv = os.environ.get(envvar)\n            if rv is not None:")],
    # C12 date-time formats: first success wins (A) -> last success wins (B)
    "C12": [(TYPES, "        for fmt in self.formats:", "        for fmt in reversed(self.formats):")],
    # C13 author date-time formats: replace the defaults (A) -> are added to them (B)
    "C13": [(TYPES, "        self.formats = list(formats) if formats is not None else [",
             "        self.formats = (list(formats) if formats is not None else []) + [")],
    # C14 integer range clamp at an open bound: adjacent integer (A) -> the bound itself (B)
    "C14": [(TYPES, "        if not open:\n            return bound\n        return bound + dir",
             "        if not open:\n            return bound\n        return bound")],
    # C15 float range, clamp with an open bound: refused at construction (A) -> clamps to the bound (B)
    "C15": [(TYPES, "        if (min_open or max_open) and clamp:\n"
                    "            raise DeclarationError(\"Clamping is not supported for open bounds.\")",
             "        if False:\n            raise DeclarationError(\"Clamping is not supported for open bounds.\")"),
            (TYPES, "        raise RuntimeError(\"Clamping is not supported for open bounds.\")",
             "        return bound")],
    # C16 empty answer to a prompt with a default: takes the default (A) -> asks again (B)
    "C16": [(TERM, "            elif default is not None:\n                value = default\n                break",
             "            elif False:\n                value = default\n                break")],
    # C17 confirmation prompt mismatch: asks the pair again (A) -> aborts (B)
    "C17": [(TERM, '        echo("Error: The two entered values do not match.", err=err)',
             '        echo("Error: The two entered values do not match.", err=err)\n        raise Abort()')],
    # C18 conversion failure at a prompt: asks again (A) -> usage error, no second question (B)
    "C18": [(TERM, '                echo(f"Error: {e.message}", err=err)\n            continue',
             '                echo(f"Error: {e.message}", err=err)\n            raise')],
    # C19 write-mode file: lazy by default (A) -> opened at conversion (B)
    "C19": [(TYPES, '        if "w" in self.mode:\n            return True\n        return False',
             '        if "w" in self.mode:\n            return False\n        return False')],
    # C20 resolved path, leading tilde: not expanded (A) -> expanded (B)
    "C20": [(TYPES, "                rv = os.path.realpath(rv)",
             "                rv = os.path.realpath(os.path.expanduser(rv))")],
    # C21 Unix app dir: $XDG_CONFIG_HOME when set (A) -> always ~/.config (B)
    "C21": [(UTILS, 'os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))',
             'os.path.expanduser("~/.config")')],
    # C22 pause, not interactive: does nothing (A) -> prints its message without waiting (B)
    "C22": [(TERM, "    if not _compat.is_interactive():\n        return\n    if info is None:",
             "    if not _compat.is_interactive():\n"
             "        echo(\"Press any key to continue...\" if info is None else info, err=err)\n"
             "        return\n    if info is None:")],
    # C23 completion with an empty token: subcommands only (A) -> options listed too (B)
    "C23": [(CORE, "        if incomplete and not incomplete[0].isalnum():",
             "        if not incomplete or not incomplete[0].isalnum():")],
    # C24 author clean stop with no status: exit 0 (A) -> exit 1 (B)
    "C24": [(CORE, "    def exit(self, code=0):", "    def exit(self, code=1):")],
    # C25 show-default on a flag whose default is off: hidden (A) -> shown (B)
    "C25": [(CORE, "            elif self.is_bool_flag and not self.secondary_opts and not default_value:\n"
                   "                default_string = \"\"",
             "            elif False:\n                default_string = \"\"")],
    # C26 a child's short help: first sentence (A) -> start of the first paragraph, cut at the limit (B)
    "C26": [(CORE, '        if word[-1] == ".":\n            return " ".join(words[: i + 1])',
             '        if False:\n            return " ".join(words[: i + 1])')],
    # C27 epilog: at the end of the help page (A) -> right after the description (B)
    "C27": [(CORE, "        self.format_help_text(ctx, formatter)\n        self.format_options(ctx, formatter)\n"
                   "        self.format_epilog(ctx, formatter)",
             "        self.format_help_text(ctx, formatter)\n        self.format_epilog(ctx, formatter)\n"
             "        self.format_options(ctx, formatter)")],
    # C28 single newlines in a help paragraph: not hard breaks (A) -> kept (B)
    "C28": [(FMT, '            p.append((indent or 0, False, " ".join(buf)))',
             '            p.append((indent or 0, True, "\\n".join(buf)))')],
    # R3 (reserve) confirm, empty answer: the default (A) -> no (B)
    "R3": [(TERM, '        elif default is not None and value == "":\n            rv = default',
            '        elif default is not None and value == "":\n            rv = False')],
    # C29 (was reserve R4) choice matching: case-sensitive by default (A) -> case-insensitive (B)
    "C29": [(TYPES, "    def __init__(self, choices, case_sensitive=True):",
            "    def __init__(self, choices, case_sensitive=False):")],
}

if __name__ == "__main__":
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    only = sys.argv[3:] or list(PATCHES)
    out.mkdir(parents=True, exist_ok=True)
    for item in only:
        dst = out / item
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(base, dst, ignore=shutil.ignore_patterns("__pycache__"))
        for rel, old, new in PATCHES[item]:
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

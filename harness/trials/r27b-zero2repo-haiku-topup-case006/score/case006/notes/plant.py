"""Plant round 17's conflicts into a copy of case006's public spec. No model call.

    python3 notes/plant.py work/spec-planted C01 C02 ...       (from the trial folder)

Copies Zero2Repo case006's `public/*.md` to the output folder and applies the side-B edit of each item
named. Each edit adds or changes text in **one** place, in the spec's own voice and with no marker,
so the other place still states side A (`ANSWER_KEY.md`). Every anchor must occur exactly once, and
after planting every exposure phrase (PHRASES, used by notes/score.py) must occur exactly once.
C01-C05 are round 14's P1, P3, P4, P6, P7 with the same edits. Zero2Repo has no licence file: the
output stays in git-ignored `work/`; this script holds only the short anchors and planted sentences.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case006/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# item: (file, anchor, replacement)
EDITS = {
    "C01": (PRD, "under that parent and is left in place.",
            "under that parent and is left in place. The new directory is always left in place after the "
            "block ends, so its files can still be inspected."),
    "C02": (IC, "a group’s map nests a `dict` under each child name |",
            "a group’s map nests a `dict` under each child name; its values take precedence over "
            "environment variables |"),
    "C03": (PRD, "Parameter callbacks receive the converted value and may replace it or refuse it. |",
            "Parameter callbacks receive the converted value and may replace it or refuse it. A parameter "
            "callback is not called for a parameter that was omitted and received no value from any "
            "source. |"),
    "C04": (PRD, "- Text wrapping accepts any string without failing.",
            "- Text wrapping accepts any string without failing. Help pages and wrapped text use a "
            "maximum content width of 100 columns unless the caller sets another."),
    "C05": (PRD, "unless that type supplies its own placeholder (a choice type does);",
            "unless that type supplies its own placeholder (a choice type does); for example, an integer "
            "option `--count` appears on the help page as `--count COUNT`;"),
    "C06": (IC, "`help` (description text),",
            "`help` (description text; a form-feed character in it is dropped and the text after it is kept),"),
    "C07": (IC, "| counting option | an `int` |",
            "| counting option | an `int`, or `None` when the option was omitted |"),
    "C08": (PRD, "A command with no parameters still runs when invoked with an empty extra-argument list.",
            "A command with no parameters still runs when invoked with an empty extra-argument list. A "
            "repeatable option that was omitted and has no default is passed as an absent value."),
    "C09": (IC, "| `envvar` | `str` or list of `str` |",
            "| `envvar` | `str` or list of `str`; with a list, the last name that is set wins |"),
    "C10": (PRD, "as false; anything else is a usage error.",
            "as false; anything else is a usage error. For a boolean flag read from an environment "
            "variable, any other value turns the flag off."),
    "C11": (PRD, "while an environment value fills the option and skips the prompt.",
            "while an environment value fills the option and skips the prompt, even when the variable is "
            "set to an empty string, which is then the value."),
    "C12": (IC, "`None` means the default list.",
            "`None` means the default list. When several formats match a value, the last matching format "
            "is used."),
    "C13": (PRD, "- Built-in parameter types, listed under FP-05; custom types the author supplies.",
            "- Built-in parameter types, listed under FP-05 (an author’s date-time format list is added to "
            "the default formats); custom types the author supplies."),
    "C14": (IC, "clamp=False)` | delivers `int` |",
            "clamp=False)` | delivers `int`; with `clamp=True`, a value beyond an open bound becomes that "
            "bound’s value |"),
    "C15": (IC, "delivers `float`. An invalid combination raises when constructed",
            "delivers `float`. With `clamp=True` and an open bound, a value beyond that bound becomes the "
            "bound; any other invalid combination raises when constructed"),
    "C16": (PRD, "- Input supplied to invoke is fed to standard input.",
            "- Input supplied to invoke is fed to standard input. An empty line is not an answer to a "
            "prompt that has a default: the prompt asks again."),
    "C17": (PRD, "- Abort — user declined a confirming abort, end-of-file on a prompt,",
            "- Abort — user declined a confirming abort, two different values typed into a confirmation "
            "prompt, end-of-file on a prompt,"),
    "C18": (PRD, "missing required parameter, conversion failure, incorrect combination —",
            "missing required parameter, conversion failure (including a value typed at a prompt, which "
            "is not asked again), incorrect combination —"),
    "C19": (IC, "`lazy=None` means the mode-dependent behaviour the PRD states.",
            "`lazy=None` means the file is opened when the parameter is converted, in every mode."),
    "C20": (IC, "(deliver `str`).",
            "(deliver `str`). With `resolve_path=True`, a leading `~` is first expanded to the home "
            "directory."),
    "C21": (IC, "its effect is the implementer’s choice |",
            "its effect is the implementer’s choice. On Unix the directory is always under `~/.config` |"),
    "C22": (PRD, "- Pause must not block in non-interactive runs.",
            "- Pause must not block in non-interactive runs; it still prints its message there."),
    "C23": (IC, "when the incomplete token is empty).",
            "when the incomplete token is empty; the suggestions for an empty token are the subcommand "
            "names followed by the option names)."),
    "C24": (PRD, "Optlyn handles the failure classes in FP-13 and exits the process.",
            "Optlyn handles the failure classes in FP-13 and exits the process. An author clean stop that "
            "gives no status exits with status 1 there."),
    "C25": (IC, "| `show_default` | bool, or a `str` shown instead of the value |",
            "| `show_default` | bool, or a `str` shown instead of the value; when on, the default is shown "
            "for every option, a flag whose default is `False` included |"),
    "C26": (IC, "lists each visible child with its short help.",
            "lists each visible child with its short help: by default the start of the child’s first "
            "paragraph, cut with `...` at 45 characters."),
    "C27": (IC, "`epilog`, `options_metavar`",
            "`epilog` (printed right after the description, before the options), `options_metavar`"),
    "C28": (IC, "| `help` | text |",
            "| `help` | text; single line breaks in it are kept on the help page |"),
    "C29": (IC, "(members are matched by name)",
            "(members are matched by name; by default the match ignores letter case)"),
}

# item: (side-A phrase, side-B phrase); each must occur exactly once in the planted spec
PHRASES = {
    "C01": ("the runner removes that directory on exit", "always left in place after the block ends"),
    "C02": ("then environment, then the default map", "take precedence over environment variables"),
    "C03": ("A missing parameter still runs its callback", "callback is not called for a parameter that was omitted"),
    "C04": ("maximum content width that defaults to 80 columns", "maximum content width of 100 columns"),
    "C05": ("the default metavar is the type name in uppercase", "as `--count COUNT`"),
    "C06": ("text after that character is omitted from the help page", "the text after it is kept"),
    "C07": ("(zero if omitted)", "or `None` when the option was omitted"),
    "C08": ("the callback receives an empty tuple, not an absent value", "is passed as an absent value"),
    "C09": ("(first one set wins)", "the last name that is set wins"),
    "C10": ("Any other non-empty string is a conversion usage error", "any other value turns the flag off"),
    "C11": ("a variable present with a truly empty value, is treated as not supplying a value",
            "even when the variable is set to an empty string"),
    "C12": ("Formats are tried in order; the first success wins", "the last matching format is used"),
    "C13": ("which replaces the default list (it does not extend it)", "is added to the default formats"),
    "C14": ("the adjacent integer inside the range for an open bound", "becomes that bound’s value"),
    "C15": ("Clamp is only allowed when both bounds are closed", "a value beyond that bound becomes the bound"),
    "C16": ("used if the user answers with an empty line", "An empty line is not an answer to a prompt"),
    "C17": ("rejects a mismatch by asking the pair again", "two different values typed into a confirmation prompt"),
    "C18": ("Prompts re-ask on conversion failure", "which is not asked again"),
    "C19": ("a write-mode file is not truncated until actually used",
            "the file is opened when the parameter is converted, in every mode"),
    "C20": ("a leading tilde is not expanded", "a leading `~` is first expanded"),
    "C21": ("`$XDG_CONFIG_HOME` when that variable is set", "On Unix the directory is always under `~/.config`"),
    "C22": ("when not interactive it does nothing and does not block", "it still prints its message there"),
    "C23": ("Options are listed only once at least a dash has been typed",
            "the subcommand names followed by the option names"),
    "C24": ("exits with status 0 when no status is given", "gives no status exits with status 1"),
    "C25": ("that default remains hidden even if show-default is on", "a flag whose default is `False` included"),
    "C26": ("the short help is the first sentence of the docstring by default",
            "the start of the child’s first paragraph"),
    "C27": ("The epilog is printed at the end of the help page",
            "printed right after the description, before the options"),
    "C28": ("Single newlines inside a paragraph are not preserved as hard breaks",
            "single line breaks in it are kept on the help page"),
    "C29": ("Matching is case-sensitive unless the author turns that off", "by default the match ignores letter case"),
}

# The 24 items kept after step 0 (ANSWER_KEY.md), for the scripts that score them.
KEPT = "C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C12 C13 C14 C15 C17 C18 C20 C21 C22 C23 C25 C26 C27 C29".split()
# item: (A substring, B substring) where the atomizer cut a phrase (checked 2026-10-30 in the store)
FIND: dict[str, tuple[str | None, str | None]] = {
    "C21": (None, "On Unix the directory is always under `~/.config"),    # closing backtick dropped
}


if __name__ == "__main__":
    out, items = Path(sys.argv[1]), sys.argv[2:]
    assert items and all(i in EDITS for i in items), items
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in PUBLIC.glob("*.md"):
        shutil.copy(f, out / f.name)
    for item in items:
        name, old, new = EDITS[item]
        text = (out / name).read_text(encoding="utf-8")
        assert text.count(old) == 1, (item, text.count(old))
        (out / name).write_text(text.replace(old, new), encoding="utf-8")
        print(item, name, "planted")
    spec = "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.glob("*.md")))
    for item in items:
        for side, phrase in zip("AB", PHRASES[item]):
            assert spec.count(phrase) == 1, (item, side, phrase, spec.count(phrase))
    print("phrases ok;", "words", sum(len(f.read_text(encoding="utf-8").split()) for f in out.glob("*.md")))

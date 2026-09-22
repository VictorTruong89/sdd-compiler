"""F1 CT-1.6 — the `sddc` command line.

rel01 ships five commands (build-plan B2): init · compile · status · conflicts ·
family. Each is registered here and implemented in its own module as the
milestones land; a registered-but-unimplemented command says so and exits 1
rather than pretending to work.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .errors import ExitCode, SddcError
from . import commands
from .ingest.pipeline import find_root

COMMANDS: dict[str, str] = {
    "init": "create the .sdd/ store and a default profile",
    "compile": "ingest the spec files, build the graph, report conflicts",
    "ingest": "only the ingest phase: spec files into blocks (no model calls)",
    "status": "show sources, blocks and what is pending",
    "conflicts": "list the open conflicts",
    "family": "show one family's nodes by layer",
}


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on a usage error; F1 CT-1.6 reserves 2 for input errors.

    The spec wins: a usage error is exit 1, an input error is exit 2.
    """

    def error(self, message: str):  # noqa: D102 - argparse hook
        self.print_usage(sys.stderr)
        print(f"sddc: {message}", file=sys.stderr)
        raise SystemExit(int(ExitCode.USAGE))


class main:  # noqa: N801 - a namespace, kept callable for `python -m`
    """Entry points, grouped so tests can ask what rel01 ships."""

    @staticmethod
    def commands() -> tuple[str, ...]:
        return tuple(COMMANDS)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="sddc",
        description="Compile Markdown specifications into a checked spec graph.",
    )
    parser.add_argument("--version", action="version", version=f"sddc {__version__}")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        metavar="DIR",
        help="repository root; defaults to the nearest parent containing .sdd/",
    )
    parser.add_argument(
        "--json", action="store_true", default=False,
        help="machine-readable output on stdout (accepted before or after the command)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    for name, help_text in COMMANDS.items():
        sub = subparsers.add_parser(name, help=help_text)
        # The same flag after the command, which is where people reach for it.
        sub.add_argument("--json", action="store_true", default=False, dest="json_after")
        if name in ("compile", "ingest"):
            sub.add_argument(
                "paths", nargs="*", metavar="PATH",
                help="spec files or directories; default: everything matching spec_globs",
            )
        if name == "family":
            sub.add_argument("name", metavar="NAME", help="a family's term id, name or alias")
        if name == "compile":
            sub.add_argument("--no-replay", action="store_true", default=False,
                             help="ask the model even where the judgment lock holds an answer")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return ExitCode.USAGE

    try:
        return dispatch(args)
    except SddcError as error:
        print(f"sddc: {error}", file=sys.stderr)
        return int(error.exit_code)


def dispatch(args: argparse.Namespace) -> int:
    """Route to a command. Unbuilt commands fail loud (vision §3 O4)."""
    root = args.root.resolve() if args.root else find_root()
    as_json = bool(args.json or getattr(args, "json_after", False))

    if args.command == "init":
        return commands.init(root, as_json=as_json)
    if args.command == "compile":
        return commands.compile_(root, paths=args.paths, as_json=as_json, replay=not args.no_replay)
    if args.command == "ingest":
        return commands.ingest(root, paths=args.paths, as_json=as_json)
    if args.command == "family":
        return commands.family(root, args.name, as_json=as_json)
    if args.command == "status":
        return commands.status(root, as_json=as_json)
    if args.command == "conflicts":
        return commands.conflicts(root, as_json=as_json)

    print(
        f"sddc: `{args.command}` is not built yet — it arrives with milestone "
        f"{'M4' if args.command == 'conflicts' else 'M3'} "
        f"(sdd/design/rel01_design/build-plan.md)",
        file=sys.stderr,
    )
    return ExitCode.USAGE

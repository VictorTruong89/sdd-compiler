"""F1 CT-1.6 — the CLI surface skeleton: exit codes and the rel01 command set.

Tier: contract (constitution §4).
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from sdd_compiler import __version__
from sdd_compiler.cli import main

REL01_COMMANDS = {"init", "compile", "ingest", "status", "conflicts", "family"}


SRC = pathlib.Path(__file__).resolve().parents[1] / "src"


def run(args, cwd=None):
    """Run the CLI as a real process, the way a user does.

    The package is not installed in the test environment, so `src` is put on
    the child's import path explicitly.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SRC), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    return subprocess.run(
        [sys.executable, "-m", "sdd_compiler", *args],
        capture_output=True, text=True, cwd=cwd, env=env,
    )


def test_ct_1_6_version_is_reported():
    result = run(["--version"])
    assert result.returncode == 0
    assert __version__ in result.stdout


def test_ct_1_6_unknown_command_is_a_usage_error():
    """Exit 1 is the usage error, distinct from input (2) and store (4)."""
    result = run(["frobnicate"])
    assert result.returncode == 1


def test_ct_1_6_rel01_commands_are_registered():
    """build-plan B2: rel01 ships exactly these five commands."""
    assert set(main.commands()) == REL01_COMMANDS


def test_ct_1_6_help_lists_every_command():
    result = run(["--help"])
    assert result.returncode == 0
    for command in REL01_COMMANDS:
        assert command in result.stdout

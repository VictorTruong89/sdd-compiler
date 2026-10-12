"""`python -m sdd_compiler` — the same entry point as the `sddc` script."""
from __future__ import annotations

import sys

from .cli import run

if __name__ == "__main__":
    sys.exit(run())

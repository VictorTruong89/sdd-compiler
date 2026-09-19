"""Atomization: pending blocks into atomic claims, checked by code (F3)."""
from __future__ import annotations

from .qatom import Atom, AtomizeOutcome, atomize_blocks, build_question

__all__ = ["Atom", "AtomizeOutcome", "atomize_blocks", "build_question"]

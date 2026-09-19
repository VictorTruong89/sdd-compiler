"""Ingest: Markdown spec files into stable, addressable blocks (F1)."""
from __future__ import annotations

from .identity import BLOCK_KEY_ORDER, IdAllocator, ReconcileResult, normalize, reconcile, text_hash
from .segment import Segment, segment_markdown

__all__ = [
    "BLOCK_KEY_ORDER", "IdAllocator", "ReconcileResult", "Segment",
    "normalize", "reconcile", "segment_markdown", "text_hash",
]

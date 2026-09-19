"""The atom, its description and its placement, travelling together through forming."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.placement import Placement
from .describe import Description
from .qatom import Atom


@dataclass
class PlacedAtom:
    atom: Atom
    description: Description
    placement: Placement
    judgments: list[str] = field(default_factory=list)   # the Q-ATOM and Q-DESC records behind it

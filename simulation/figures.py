"""Figure data model and registry for the Cold War Erosion Simulation."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class Figure:
    """Represents a historical figure in the simulation."""

    id: str
    name: str
    role: str
    faction: str                       # military | political | civilian | media
    active_years: tuple[int, int]      # (start, end) inclusive
    traits: List[str]
    stats: Dict[str, int]              # aggression, pragmatism, political_skill, public_influence
    relationships: Dict[str, int]      # figure_id -> -100..+100
    decision_logic: str                # hawk | dove | pragmatist | opportunist | demagogue

    # Runtime-mutable: can change as the simulation progresses
    current_stats: Dict[str, int] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.current_stats = dict(self.stats)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_active(self, year: int) -> bool:
        """Return True if this figure is active during *year*."""
        return self.active_years[0] <= year <= self.active_years[1]

    def relationship_to(self, other_id: str) -> int:
        """Return the relationship score toward *other_id*, defaulting to 0."""
        return self.relationships.get(other_id, 0)

    def modify_stat(self, stat: str, delta: int) -> None:
        """Apply *delta* to a runtime stat, clamped to [0, 100]."""
        if stat not in self.current_stats:
            raise KeyError(f"Unknown stat {stat!r} for figure {self.id!r}")
        self.current_stats[stat] = max(0, min(100, self.current_stats[stat] + delta))

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Figure":
        """Construct a Figure from a YAML-loaded dict."""
        years = data["active_years"]
        return cls(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            faction=data["faction"],
            active_years=(int(years[0]), int(years[1])),
            traits=data.get("traits", []),
            stats=data.get("stats", {}),
            relationships=data.get("relationships", {}),
            decision_logic=data["decision_logic"],
        )


class FigureRegistry:
    """Loads and provides access to all historical figures."""

    def __init__(self) -> None:
        self._figures: Dict[str, Figure] = {}

    @classmethod
    def load_all(cls, data_dir: str | Path) -> "FigureRegistry":
        """Load all ``*.yaml`` figure files from *data_dir*."""
        registry = cls()
        data_dir = Path(data_dir)
        for path in sorted(data_dir.glob("*.yaml")):
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            figure = Figure.from_dict(data)
            registry._figures[figure.id] = figure
        return registry

    def get(self, figure_id: str) -> Optional[Figure]:
        """Return the Figure with *figure_id*, or None."""
        return self._figures.get(figure_id)

    def active_in(self, year: int) -> List[Figure]:
        """Return all figures active during *year*."""
        return [f for f in self._figures.values() if f.is_active(year)]

    def all(self) -> List[Figure]:
        """Return all loaded figures."""
        return list(self._figures.values())

    def ids(self) -> List[str]:
        """Return all figure IDs."""
        return list(self._figures.keys())

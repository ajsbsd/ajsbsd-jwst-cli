"""Global state meters for the Cold War Erosion Simulation.

All meters are integers clamped to [0, 100].
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

# ---------------------------------------------------------------------------
# Meter definitions: name -> (description, starting_value)
# ---------------------------------------------------------------------------
METER_DEFINITIONS: Dict[str, tuple[str, int]] = {
    "civilian_oversight": (
        "Meaningful civilian control over military decisions",
        85,
    ),
    "escalation_risk": (
        "Global risk of nuclear / WW3 escalation",
        15,
    ),
    "public_support": (
        "U.S. public support for the military and its spending",
        70,
    ),
    "defense_budget_share": (
        "Military share of national budget / political capital",
        30,
    ),
    "sac_readiness": (
        "Strategic Air Command operational readiness",
        20,
    ),
    "soviet_threat_perception": (
        "Public and political perception of the Soviet threat level",
        40,
    ),
    "information_monopoly": (
        "Military monopoly over intelligence and metrics vs. civilian access",
        10,
    ),
    "economic_dependence": (
        "Civilian economy dependence on defence spending (MIC)",
        15,
    ),
}


@dataclass
class GlobalMeters:
    """Holds all global simulation meters and their current values."""

    _values: Dict[str, int] = field(default_factory=dict, repr=False)
    _previous: Dict[str, int] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if not self._values:
            self._values = {
                name: start for name, (_, start) in METER_DEFINITIONS.items()
            }
        self._previous = dict(self._values)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, name: str, delta: int) -> None:
        """Apply *delta* to *name*, clamping the result to [0, 100].

        Raises KeyError for unknown meter names.
        """
        if name not in self._values:
            raise KeyError(f"Unknown meter: {name!r}")
        self._previous[name] = self._values[name]
        self._values[name] = max(0, min(100, self._values[name] + delta))

    def get(self, name: str) -> int:
        """Return the current value of *name*."""
        if name not in self._values:
            raise KeyError(f"Unknown meter: {name!r}")
        return self._values[name]

    def snapshot_previous(self) -> None:
        """Capture the current values as the 'previous' baseline.

        Call this at the start of each turn before applying event outcomes
        so that trend arrows in the narrative printer reflect within-turn
        changes.
        """
        self._previous = dict(self._values)

    def trend(self, name: str) -> int:
        """Return the delta between current and previous value for *name*."""
        if name not in self._values:
            raise KeyError(f"Unknown meter: {name!r}")
        return self._values[name] - self._previous.get(name, self._values[name])

    def summary(self) -> Dict[str, dict]:
        """Return a dict suitable for display / serialisation.

        Each entry: ``{value: int, trend: int, description: str}``
        """
        return {
            name: {
                "value": self._values[name],
                "trend": self.trend(name),
                "description": METER_DEFINITIONS[name][0],
            }
            for name in METER_DEFINITIONS
        }

    def names(self) -> list[str]:
        """Return the ordered list of meter names."""
        return list(METER_DEFINITIONS.keys())

    def check(self, name: str, op: str, value: int) -> bool:
        """Evaluate a single condition against the current meter state.

        *op* must be one of: ``lt``, ``gt``, ``lte``, ``gte``, ``eq``.
        """
        current = self.get(name)
        match op:
            case "lt":
                return current < value
            case "gt":
                return current > value
            case "lte":
                return current <= value
            case "gte":
                return current >= value
            case "eq":
                return current == value
            case _:
                raise ValueError(f"Unknown operator: {op!r}")

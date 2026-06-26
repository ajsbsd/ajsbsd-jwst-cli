"""Event data model and engine for the Cold War Erosion Simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from simulation.meters import GlobalMeters
from simulation.figures import FigureRegistry


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MeterOutcome:
    name: str
    delta: int


@dataclass
class StatChange:
    figure: str
    stat: str
    delta: int


@dataclass
class EventOutcomes:
    meters: List[MeterOutcome] = field(default_factory=list)
    figure_stat_changes: List[StatChange] = field(default_factory=list)


@dataclass
class Condition:
    """A single condition that must be satisfied for an event to fire."""
    meter: Optional[str] = None
    op: Optional[str] = None
    value: Optional[int] = None
    figure_active: Optional[str] = None   # figure id that must be active


@dataclass
class Event:
    """Represents a single historical event in the simulation."""

    id: str
    year: int
    era: str
    title: str
    description: str
    narrative: str
    conditions: List[Condition]
    outcomes: EventOutcomes
    divergence: Optional[str]   # divergence branch id, or None
    once: bool = True           # fire at most once per run

    # Runtime state
    fired: bool = field(default=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        conditions = []
        for c in data.get("conditions", []):
            conditions.append(Condition(
                meter=c.get("meter"),
                op=c.get("op"),
                value=c.get("value"),
                figure_active=c.get("figure_active"),
            ))

        raw_outcomes = data.get("outcomes", {}) or {}
        meter_outcomes = [
            MeterOutcome(name=m["name"], delta=int(m["delta"]))
            for m in raw_outcomes.get("meters", [])
        ]
        stat_changes = [
            StatChange(figure=s["figure"], stat=s["stat"], delta=int(s["delta"]))
            for s in raw_outcomes.get("figure_stat_changes", [])
        ]

        return cls(
            id=data["id"],
            year=int(data["year"]),
            era=data.get("era", ""),
            title=data["title"],
            description=data.get("description", ""),
            narrative=data.get("narrative", ""),
            conditions=conditions,
            outcomes=EventOutcomes(meters=meter_outcomes, figure_stat_changes=stat_changes),
            divergence=data.get("divergence"),
            once=data.get("once", True),
        )


# ---------------------------------------------------------------------------
# Condition / outcome helpers
# ---------------------------------------------------------------------------

def evaluate_conditions(
    event: Event,
    meters: GlobalMeters,
    registry: FigureRegistry,
    year: int,
) -> bool:
    """Return True if ALL conditions on *event* are satisfied."""
    for cond in event.conditions:
        if cond.figure_active is not None:
            figure = registry.get(cond.figure_active)
            if figure is None or not figure.is_active(year):
                return False
        if cond.meter is not None:
            if not meters.check(cond.meter, cond.op, cond.value):
                return False
    return True


def apply_outcomes(
    event: Event,
    meters: GlobalMeters,
    registry: FigureRegistry,
) -> None:
    """Apply all outcomes from *event* to *meters* and figures."""
    for mo in event.outcomes.meters:
        meters.update(mo.name, mo.delta)
    for sc in event.outcomes.figure_stat_changes:
        figure = registry.get(sc.figure)
        if figure is not None:
            figure.modify_stat(sc.stat, sc.delta)


# ---------------------------------------------------------------------------
# EventEngine
# ---------------------------------------------------------------------------

class EventEngine:
    """Loads era event files and manages event firing for the simulation."""

    def __init__(self) -> None:
        self._events: List[Event] = []

    @classmethod
    def load_eras(cls, events_dir: str | Path) -> "EventEngine":
        """Load all ``era_*.yaml`` files from *events_dir*."""
        engine = cls()
        events_dir = Path(events_dir)
        for path in sorted(events_dir.glob("era_*.yaml")):
            with open(path, "r", encoding="utf-8") as fh:
                era_events = yaml.safe_load(fh) or []
            for data in era_events:
                engine._events.append(Event.from_dict(data))
        return engine

    def get_eligible_events(
        self,
        year: int,
        meters: GlobalMeters,
        registry: FigureRegistry,
    ) -> List[Event]:
        """Return events eligible to fire in *year* given current state."""
        eligible = []
        for event in self._events:
            if event.once and event.fired:
                continue
            if event.year != year:
                continue
            if evaluate_conditions(event, meters, registry, year):
                eligible.append(event)
        return eligible

    def fire_event(
        self,
        event: Event,
        meters: GlobalMeters,
        registry: FigureRegistry,
    ) -> None:
        """Apply *event* outcomes and mark it as fired."""
        apply_outcomes(event, meters, registry)
        event.fired = True

    def all_events(self) -> List[Event]:
        return list(self._events)

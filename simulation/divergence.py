"""Divergence (alternate timeline) system for the Cold War Erosion Simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from simulation.meters import GlobalMeters
from simulation.figures import FigureRegistry
from simulation.events import Event, EventOutcomes, MeterOutcome, Condition, evaluate_conditions


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BranchEvent:
    """A simplified event inside a divergence branch (no condition evaluation needed)."""
    year: int
    title: str
    narrative: str
    outcomes: EventOutcomes

    @classmethod
    def from_dict(cls, data: dict) -> "BranchEvent":
        raw_outcomes = data.get("outcomes", {}) or {}
        meter_outcomes = [
            MeterOutcome(name=m["name"], delta=int(m["delta"]))
            for m in raw_outcomes.get("meters", [])
        ]
        return cls(
            year=int(data["year"]),
            title=data["title"],
            narrative=data.get("narrative", ""),
            outcomes=EventOutcomes(meters=meter_outcomes),
        )


@dataclass
class DivergenceBranch:
    """An alternate timeline branch that fires when trigger conditions are met."""

    id: str
    trigger_year: int
    trigger_conditions: List[Condition]
    branch_narrative: str
    branch_events: List[BranchEvent]
    ending: str   # ending id

    # Runtime state
    fired: bool = field(default=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "DivergenceBranch":
        conditions = []
        for c in data.get("trigger_conditions", []):
            conditions.append(Condition(
                meter=c.get("meter"),
                op=c.get("op"),
                value=c.get("value"),
                figure_active=c.get("figure_active"),
            ))
        branch_events = [
            BranchEvent.from_dict(e) for e in data.get("branch_events", [])
        ]
        return cls(
            id=data["id"],
            trigger_year=int(data["trigger_year"]),
            trigger_conditions=conditions,
            branch_narrative=data.get("branch_narrative", ""),
            branch_events=branch_events,
            ending=data["ending"],
        )


# ---------------------------------------------------------------------------
# Divergence Engine
# ---------------------------------------------------------------------------

class DivergenceEngine:
    """Loads divergence branch files and detects when a branch should activate."""

    def __init__(self) -> None:
        self._branches: List[DivergenceBranch] = []
        self._active_branch: Optional[DivergenceBranch] = None
        self._branch_event_index: int = 0

    @classmethod
    def load_all(cls, divergence_dir: str | Path) -> "DivergenceEngine":
        """Load all ``*.yaml`` divergence files from *divergence_dir*."""
        engine = cls()
        divergence_dir = Path(divergence_dir)
        for path in sorted(divergence_dir.glob("*.yaml")):
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            if data:
                engine._branches.append(DivergenceBranch.from_dict(data))
        return engine

    def check(
        self,
        year: int,
        meters: GlobalMeters,
        registry: FigureRegistry,
    ) -> Optional[DivergenceBranch]:
        """Return the first un-fired branch whose trigger conditions are met, or None.

        Does NOT activate the branch — call :meth:`activate` separately.
        """
        if self._active_branch is not None:
            return None  # already branched
        for branch in self._branches:
            if branch.fired:
                continue
            if year < branch.trigger_year:
                continue
            # Evaluate trigger conditions using the same mechanism as events
            all_met = True
            for cond in branch.trigger_conditions:
                if cond.figure_active is not None:
                    figure = registry.get(cond.figure_active)
                    if figure is None or not figure.is_active(year):
                        all_met = False
                        break
                if cond.meter is not None:
                    if not meters.check(cond.meter, cond.op, cond.value):
                        all_met = False
                        break
            if all_met:
                return branch
        return None

    def activate(self, branch: DivergenceBranch) -> None:
        """Mark *branch* as the active branch."""
        branch.fired = True
        self._active_branch = branch
        self._branch_event_index = 0

    @property
    def is_branched(self) -> bool:
        return self._active_branch is not None

    @property
    def active_branch(self) -> Optional[DivergenceBranch]:
        return self._active_branch

    def get_branch_events_for_year(self, year: int) -> List[BranchEvent]:
        """Return branch events scheduled for *year*, in order."""
        if self._active_branch is None:
            return []
        return [e for e in self._active_branch.branch_events if e.year == year]

    def apply_branch_event(
        self,
        branch_event: BranchEvent,
        meters: GlobalMeters,
    ) -> None:
        """Apply a branch event's meter outcomes."""
        for mo in branch_event.outcomes.meters:
            meters.update(mo.name, mo.delta)

    def all_branches(self) -> List[DivergenceBranch]:
        return list(self._branches)


# ---------------------------------------------------------------------------
# Ending resolution
# ---------------------------------------------------------------------------

ENDINGS: Dict[str, dict] = {
    "cold_war_won": {
        "title": "The Quiet Surrender",
        "condition_desc": "civilian_oversight < 30 AND escalation_risk < 40",
        "narrative": (
            "The Soviet flag is lowered over the Kremlin. The Cold War is won.\n\n"
            "A civilian President sits in the Oval Office, signing a defense "
            "authorization bill so large and so complex that no single human being "
            "can read it in a year. He does not know what half the line items are. "
            "His staff tells him they are necessary.\n\n"
            "The generals do not need to threaten anyone. They do not need to "
            "stage a coup. They do not need to do anything dramatic at all.\n\n"
            "The civilians simply stopped understanding what they were supposed "
            "to be overseeing, and then they stopped asking. The oversight "
            "is a form. The form is still filled out. The box is still checked.\n\n"
            "LeMay was right: the only way to control the military was to give it "
            "enough resources to do whatever it wanted. The politicians discovered "
            "this forty-four years too late.\n\n"
            "CIVILIAN OVERSIGHT RATING: CRITICAL\n"
            "THE MILITARY-INDUSTRIAL COMPLEX: PERMANENT\n"
            "DEMOCRACY: PROCEDURALLY INTACT"
        ),
    },
    "ww3_nuclear": {
        "title": "The Stone Age",
        "condition_desc": "escalation_risk > 90",
        "narrative": (
            "The missiles are in the air.\n\n"
            "LeMay said it would come to this. He said so in 1950, in 1958, "
            "in 1962. He said the only way to prevent a nuclear war was to fight "
            "one first, on terms favorable to the United States, before the "
            "Soviet arsenal reached parity.\n\n"
            "He was overruled each time.\n\n"
            "He is not here to say 'I told you so.' Nobody is.\n\n"
            "ESCALATION METER: TERMINAL\n"
            "CIVILIAN OVERSIGHT: IRRELEVANT\n"
            "POPULATION: DECLINING"
        ),
    },
    "soviet_victory": {
        "title": "The Long Defeat",
        "condition_desc": "public_support < 20 AND defense_budget_share < 20",
        "narrative": (
            "The republic did not fall to communism. It fell to exhaustion.\n\n"
            "Forty years of proxy wars, stalemates, and political restraint "
            "drained the public will to sustain the struggle. The defense budget "
            "was cut. The military hollowed out. SAC's bombers went unflown "
            "for lack of spare parts.\n\n"
            "The Soviets did not win militarily. They simply waited. They were "
            "patient in the way that a system without elections can afford to be.\n\n"
            "CIVILIAN OVERSIGHT: HIGH (functionally irrelevant)\n"
            "PUBLIC SUPPORT: COLLAPSED\n"
            "MILITARY READINESS: CRITICAL"
        ),
    },
    "oversight_restored": {
        "title": "The Road Not Taken",
        "condition_desc": "civilian_oversight > 70 in 1991",
        "narrative": (
            "This did not happen.\n\n"
            "In every run of this simulation with historically calibrated starting "
            "conditions, this ending has never been reached. The mechanisms of "
            "erosion — technological dependence, information monopoly, economic "
            "hostage-taking, the Crisis Ratchet — are self-reinforcing.\n\n"
            "The fact that you are reading this ending means you altered the "
            "starting conditions, which means you already understand the point "
            "the simulation was trying to make.\n\n"
            "CIVILIAN OVERSIGHT: ANOMALOUS\n"
            "HISTORICAL PROBABILITY: NEAR ZERO"
        ),
    },
    "ww3_1952": {
        "title": "The Stone Age (Korea, 1952)",
        "condition_desc": "divergence: korea_nuclear_1951",
        "narrative": (
            "The first nuclear weapon used in warfare since 1945 detonates over "
            "the Yalu River crossing at 0347 local time.\n\n"
            "China enters the war within six hours. Soviet forces mobilise along "
            "the European frontier within forty-eight. The President calls LeMay "
            "directly. LeMay has already prepared the SAC targeting plan for "
            "Moscow, Leningrad, and the Ural industrial complex.\n\n"
            "'Give me the order,' LeMay says.\n\n"
            "The President holds the phone for eleven seconds. Then he gives it.\n\n"
            "LeMay was right. He had always been right. There is no one left "
            "to dispute this.\n\n"
            "ESCALATION METER: TERMINAL"
        ),
    },
    "ww3_cuba_1962": {
        "title": "The Stone Age (Cuba, 1962)",
        "condition_desc": "divergence: cuba_airstrikes_1962",
        "narrative": (
            "The first American airstrikes hit Cuban missile sites at dawn.\n\n"
            "Within four hours, a Soviet submarine commander in the Atlantic, "
            "cut off from Moscow, believing nuclear war has begun, authorises "
            "the firing of a nuclear torpedo at the USS Randolph.\n\n"
            "The torpedo does not detonate due to a mechanical fault.\n\n"
            "The next one does.\n\n"
            "ESCALATION METER: TERMINAL"
        ),
    },
    "vietnam_chinese_intervention": {
        "title": "The Vietnam Quagmire Deepens",
        "condition_desc": "divergence: vietnam_unrestricted_1965",
        "narrative": (
            "The unrestricted bombing campaign collapses North Vietnamese "
            "infrastructure within ninety days. The Ho Chi Minh Trail is "
            "cratered and impassable. The North Vietnamese government "
            "requests Chinese intervention.\n\n"
            "300,000 Chinese troops cross the border on March 3, 1966.\n\n"
            "The war McNamara wanted to limit has become the war LeMay "
            "wanted to fight. Nobody is happy with the outcome.\n\n"
            "ESCALATION RISK: HIGH\n"
            "CIVILIAN OVERSIGHT: EFFECTIVELY ZERO\n"
            "WAR DURATION: EXTENDED INDEFINITELY"
        ),
    },
}


def resolve_ending(meters: GlobalMeters, branch_ending: Optional[str] = None) -> dict:
    """Return the appropriate ending dict given current meter state."""
    if branch_ending and branch_ending in ENDINGS:
        return ENDINGS[branch_ending]
    if meters.get("escalation_risk") > 90:
        return ENDINGS["ww3_nuclear"]
    if meters.get("public_support") < 20 and meters.get("defense_budget_share") < 20:
        return ENDINGS["soviet_victory"]
    if meters.get("civilian_oversight") > 70:
        return ENDINGS["oversight_restored"]
    return ENDINGS["cold_war_won"]

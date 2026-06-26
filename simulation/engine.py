"""Core simulation engine — year-by-year turn loop (1947–1991)."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

from simulation.meters import GlobalMeters
from simulation.figures import FigureRegistry
from simulation.events import EventEngine
from simulation.divergence import DivergenceEngine, resolve_ending

# Data directories, resolved relative to this file's location
_PACKAGE_DIR = Path(__file__).parent
DATA_DIR = _PACKAGE_DIR / "data"
FIGURES_DIR = DATA_DIR / "figures"
EVENTS_DIR = DATA_DIR / "events"
DIVERGENCE_DIR = DATA_DIR / "divergence"

START_YEAR = 1947
END_YEAR = 1991


class SimulationEngine:
    """Drives the simulation from 1947 to 1991, year by year."""

    def __init__(
        self,
        seed: Optional[int] = None,
        verbose: bool = False,
        no_color: bool = False,
    ) -> None:
        if seed is not None:
            random.seed(seed)

        self.verbose = verbose
        self.no_color = no_color

        # Core simulation state
        self.meters = GlobalMeters()
        self.registry = FigureRegistry.load_all(FIGURES_DIR)
        self.event_engine = EventEngine.load_eras(EVENTS_DIR)
        self.divergence_engine = DivergenceEngine.load_all(DIVERGENCE_DIR)

        # Narrative printer (imported here to avoid circular dep)
        from simulation.narrative import NarrativePrinter
        self.printer = NarrativePrinter(no_color=no_color)

        self._current_year: int = START_YEAR

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the full simulation from START_YEAR to END_YEAR."""
        self.printer.print_opening()

        for year in range(START_YEAR, END_YEAR + 1):
            self._current_year = year
            self.meters.snapshot_previous()

            # 1. Fire eligible regular events
            eligible = self.event_engine.get_eligible_events(
                year, self.meters, self.registry
            )
            for event in eligible:
                self.printer.print_event(event, year)
                self.event_engine.fire_event(event, self.meters, self.registry)

            # 2. Fire branch events if already diverged
            if self.divergence_engine.is_branched:
                branch_events = self.divergence_engine.get_branch_events_for_year(year)
                for be in branch_events:
                    self.printer.print_branch_event(be, year)
                    self.divergence_engine.apply_branch_event(be, self.meters)

            # 3. Check for new divergence (only if not already branched)
            if not self.divergence_engine.is_branched:
                branch = self.divergence_engine.check(year, self.meters, self.registry)
                if branch is not None:
                    self.printer.print_divergence(branch, year)
                    self.divergence_engine.activate(branch)

            # 4. Print state summary
            if self.verbose or year % 4 == 0 or year == END_YEAR:
                self.printer.print_summary(year, self.meters)

            # 5. Check for early termination (WW3 condition)
            if self.meters.get("escalation_risk") >= 95:
                self._terminate_early(year)
                return

        # 6. Resolve ending
        branch_ending = (
            self.divergence_engine.active_branch.ending
            if self.divergence_engine.is_branched
            else None
        )
        ending = resolve_ending(self.meters, branch_ending)
        self.printer.print_ending(ending, END_YEAR, self.meters)

    def _terminate_early(self, year: int) -> None:
        """Handle the WW3 escalation threshold breach."""
        from simulation.divergence import ENDINGS
        self.printer.print_ending(ENDINGS["ww3_nuclear"], year, self.meters)

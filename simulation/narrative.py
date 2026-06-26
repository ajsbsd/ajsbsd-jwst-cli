"""Narrative printer — styled terminal output using rich."""
from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from simulation.meters import GlobalMeters, METER_DEFINITIONS

# Meters where HIGH value is bad (inverted color logic)
HIGH_IS_BAD = {"escalation_risk", "information_monopoly", "economic_dependence"}


def _bar(value: int, width: int = 20) -> str:
    """Return a simple ASCII progress bar string."""
    filled = round(value / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _meter_color(name: str, value: int) -> str:
    """Return a rich color tag for a meter value."""
    if name in HIGH_IS_BAD:
        # Inverted: low is good (green), high is bad (red)
        if value < 30:
            return "green"
        elif value < 65:
            return "yellow"
        else:
            return "red"
    else:
        # Normal: high is good (green), low is bad (red)
        if value > 60:
            return "green"
        elif value > 30:
            return "yellow"
        else:
            return "red"


def _trend_arrow(trend: int) -> str:
    if trend > 0:
        return "▲"
    elif trend < 0:
        return "▼"
    return " "


class NarrativePrinter:
    """Prints narrative events, state summaries, and endings to the terminal."""

    def __init__(self, no_color: bool = False) -> None:
        self.console = Console(no_color=no_color, highlight=False)
        self._no_color = no_color

    # ------------------------------------------------------------------
    # Opening banner
    # ------------------------------------------------------------------

    def print_opening(self) -> None:
        self.console.print()
        self.console.print(
            Panel(
                "[bold white]COLD WAR EROSION SIMULATION[/bold white]\n"
                "[dim]1947 – 1991[/dim]\n\n"
                "[italic]The permanent end of civilian oversight of the United States military[/italic]\n\n"
                "[dim]Four mechanisms. Forty-four years. One outcome.[/dim]",
                border_style="red",
                expand=False,
                title="[bold red]CLASSIFIED[/bold red]",
            )
        )
        self.console.print()

    # ------------------------------------------------------------------
    # Event display
    # ------------------------------------------------------------------

    def print_event(self, event, year: int) -> None:
        """Print a regular historical event."""
        title = f"[bold]{year}[/bold]  {event.title}"
        body = event.narrative.strip()
        self.console.print(
            Panel(
                body,
                title=title,
                border_style="blue",
                expand=False,
                padding=(0, 1),
            )
        )
        self.console.print()

    def print_branch_event(self, branch_event, year: int) -> None:
        """Print an event that is part of an active divergence branch."""
        title = f"[bold]{year}[/bold]  [bold red]ALTERNATE TIMELINE[/bold red]  {branch_event.title}"
        body = branch_event.narrative.strip()
        self.console.print(
            Panel(
                body,
                title=title,
                border_style="red",
                expand=False,
                padding=(0, 1),
            )
        )
        self.console.print()

    # ------------------------------------------------------------------
    # Divergence display
    # ------------------------------------------------------------------

    def print_divergence(self, branch, year: int) -> None:
        """Print the divergence branch activation banner."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold red]TIMELINE DIVERGENCE DETECTED[/bold red]\n\n"
                + branch.branch_narrative.strip()
                + f"\n\n[dim]Branch: {branch.id}[/dim]",
                border_style="red",
                title=f"[bold red]⚠  {year} — DIVERGENCE POINT[/bold red]",
                expand=False,
                padding=(0, 1),
            )
        )
        self.console.print()

    # ------------------------------------------------------------------
    # State summary
    # ------------------------------------------------------------------

    def print_summary(self, year: int, meters: GlobalMeters) -> None:
        """Print a color-coded state summary table."""
        summary = meters.summary()

        table = Table(
            title=f"[bold]STATE SUMMARY — {year}[/bold]",
            box=box.SIMPLE_HEAVY,
            show_header=True,
            header_style="bold",
            expand=False,
            min_width=62,
        )
        table.add_column("Meter", style="", min_width=26)
        table.add_column("Value", justify="right", min_width=5)
        table.add_column("Bar", min_width=22)
        table.add_column("Trend", justify="center", min_width=4)

        for name, data in summary.items():
            value = data["value"]
            trend = data["trend"]
            color = _meter_color(name, value)
            label = name.replace("_", " ").title()
            bar = _bar(value)
            trend_str = _trend_arrow(trend)
            trend_color = "green" if trend > 0 else ("red" if trend < 0 else "dim")
            # Invert trend color meaning for bad meters
            if name in HIGH_IS_BAD:
                trend_color = "red" if trend > 0 else ("green" if trend < 0 else "dim")

            table.add_row(
                label,
                f"[{color}]{value:3d}[/{color}]",
                f"[{color}]{bar}[/{color}]",
                f"[{trend_color}]{trend_str}[/{trend_color}]",
            )

        self.console.print(table)
        self.console.print()

    # ------------------------------------------------------------------
    # Ending display
    # ------------------------------------------------------------------

    def print_ending(self, ending: dict, year: int, meters: GlobalMeters) -> None:
        """Print the final ending panel."""
        self.console.print()
        self.console.print(
            Panel(
                ending["narrative"],
                title=f"[bold red]{ending['title'].upper()}[/bold red]",
                border_style="red",
                expand=True,
                padding=(1, 2),
            )
        )
        self.console.print()
        self.print_summary(year, meters)

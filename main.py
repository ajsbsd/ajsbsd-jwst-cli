"""Entry point for the Cold War Erosion Simulation."""
import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cold War Erosion Simulation (1947–1991)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible runs",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print state summary every year instead of every 4 years",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        dest="no_color",
        help="Disable rich terminal styling (plain text output)",
    )
    parser.add_argument(
        "--force-event",
        metavar="EVENT_ID",
        action="append",
        default=[],
        dest="force_events",
        help=(
            "Force an event to fire at the start of the simulation regardless "
            "of its scheduled year or conditions. Repeatable: "
            "--force-event foo --force-event bar"
        ),
    )
    parser.add_argument(
        "--set-meter",
        metavar="NAME=VALUE",
        action="append",
        default=[],
        dest="set_meters",
        help=(
            "Override a meter's starting value, e.g. --set-meter escalation_risk=80. "
            "Repeatable. Use --list-events to see meter names."
        ),
    )
    parser.add_argument(
        "--list-events",
        action="store_true",
        dest="list_events",
        help="Print all event IDs with their year and title, then exit.",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # --list-events: print event catalogue and exit
    # ------------------------------------------------------------------
    if args.list_events:
        from simulation.events import EventEngine
        from simulation.engine import EVENTS_DIR
        engine = EventEngine.load_eras(EVENTS_DIR)
        events = sorted(engine.all_events(), key=lambda e: e.year)
        print(f"{'ID':<40} {'YEAR':<6} TITLE")
        print("-" * 80)
        for ev in events:
            print(f"{ev.id:<40} {ev.year:<6} {ev.title}")
        sys.exit(0)

    # ------------------------------------------------------------------
    # Parse --set-meter overrides
    # ------------------------------------------------------------------
    meter_overrides: dict = {}
    for raw in args.set_meters:
        if "=" not in raw:
            parser.error(f"--set-meter requires NAME=VALUE format, got: {raw!r}")
        name, _, raw_val = raw.partition("=")
        try:
            meter_overrides[name.strip()] = int(raw_val.strip())
        except ValueError:
            parser.error(f"--set-meter value must be an integer, got: {raw_val!r}")

    # ------------------------------------------------------------------
    # Run simulation
    # ------------------------------------------------------------------
    from simulation.engine import SimulationEngine

    engine = SimulationEngine(
        seed=args.seed,
        verbose=args.verbose,
        no_color=args.no_color,
        meter_overrides=meter_overrides,
        force_events=args.force_events,
    )
    engine.run()


if __name__ == "__main__":
    main()

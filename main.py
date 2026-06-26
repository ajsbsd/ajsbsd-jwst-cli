"""Entry point for the Cold War Erosion Simulation."""
import argparse


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
    args = parser.parse_args()

    from simulation.engine import SimulationEngine

    engine = SimulationEngine(
        seed=args.seed,
        verbose=args.verbose,
        no_color=args.no_color,
    )
    engine.run()


if __name__ == "__main__":
    main()

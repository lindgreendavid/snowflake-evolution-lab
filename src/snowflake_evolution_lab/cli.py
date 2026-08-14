"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import write_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce Snowflake Evolution Lab v0.1")
    parser.add_argument("--source", type=Path, default=Path("data/trajectories-v0.1.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/results-v0.1.json"))
    args = parser.parse_args()
    results = write_results(args.source, args.output)
    status = "PASS" if results["confirmatory"]["passed"] else "FAIL"
    print(f"{status}: {results['confirmatory']['positive_populations']}/5 positive lineages")


if __name__ == "__main__":
    main()

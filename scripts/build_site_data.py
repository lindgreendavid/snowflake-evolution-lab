"""Build deterministic browser data from the frozen source and analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from snowflake_evolution_lab.analysis import load_trajectories, write_results
from snowflake_evolution_lab.v1 import (
    load_chromosomes,
    load_engineered,
    load_longitudinal,
    write_v1_results,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "data" / "trajectories-v0.1.csv"
    report = ROOT / "reports" / "results-v0.1.json"
    site_data = ROOT / "site" / "data"
    site_data.mkdir(parents=True, exist_ok=True)
    results = write_results(source, report)
    (site_data / "results-v0.1.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    trajectories = [
        {
            "day": row.day,
            "population": row.population,
            "aspect_ratio": row.aspect_ratio,
            "radius_um": row.radius_um,
        }
        for row in load_trajectories(source)
    ]
    (site_data / "trajectories-v0.1.json").write_text(
        json.dumps(trajectories, indent=2) + "\n", encoding="utf-8"
    )
    with (ROOT / "data" / "day600-treatments-v0.1.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        treatments = [
            {
                "treatment": row["treatment"],
                "replicate": int(row["replicate"]),
                "radius_um": float(row["radius_um"]),
            }
            for row in csv.DictReader(handle)
        ]
    (site_data / "treatments-v0.1.json").write_text(
        json.dumps(treatments, indent=2) + "\n", encoding="utf-8"
    )

    engineered_source = ROOT / "data" / "engineered-replicates-v1.0.csv"
    longitudinal_source = ROOT / "data" / "longitudinal-v1.0.csv"
    chromosome_source = ROOT / "data" / "chromosome-copy-v1.0.csv"
    v1_results = write_v1_results(
        engineered_source,
        longitudinal_source,
        chromosome_source,
        ROOT / "reports" / "results-v1.0.json",
    )
    (site_data / "results-v1.0.json").write_text(
        json.dumps(v1_results, indent=2) + "\n", encoding="utf-8"
    )
    (site_data / "engineered-v1.0.json").write_text(
        json.dumps([row.__dict__ for row in load_engineered(engineered_source)], indent=2) + "\n",
        encoding="utf-8",
    )
    (site_data / "longitudinal-v1.0.json").write_text(
        json.dumps([row.__dict__ for row in load_longitudinal(longitudinal_source)], indent=2)
        + "\n",
        encoding="utf-8",
    )
    (site_data / "chromosome-copy-v1.0.json").write_text(
        json.dumps([row.__dict__ for row in load_chromosomes(chromosome_source)], indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

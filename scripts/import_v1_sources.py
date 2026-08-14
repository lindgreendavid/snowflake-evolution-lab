"""Verify pinned Tong et al. sources and build compact v1 analysis inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def verify_sources(source_root: Path) -> None:
    provenance = json.loads((ROOT / "data" / "provenance-v1.0.json").read_text())
    for source in provenance["source_files"]:
        path = source_root / source["path"]
        if _sha256(path) != source["sha256"]:
            raise ValueError(f"source hash mismatch: {source['path']}")


def engineered_replicates(source_root: Path) -> list[dict[str, Any]]:
    cell_groups: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    limits = {("PM", "2N"): 2.1, ("PM", "4N"): 2.4, ("PA", "2N"): 2.0, ("PA", "4N"): 2.2}
    for row in _read(source_root / "data/source_data/Fig3bcf_raw_EDFig5de.csv"):
        key = (row["Condition"], row["Ploidy"], row["Replicate"])
        if float(row["AR"]) < limits[key[:2]]:
            cell_groups[key].append((float(row["Volume"]), float(row["AR"])))

    cluster_groups: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in _read(source_root / "data/source_data/Fig3e_raw_EDFig5bc.csv"):
        if row["Time"] == "24h":
            key = (row["Condition"], row["Ploidy"], row["Replicate"])
            cluster_groups[key].append(float(row["Volume"]))

    output: list[dict[str, Any]] = []
    for key in sorted(cell_groups):
        cells = cell_groups[key]
        clusters = cluster_groups[key]
        weighted_radius = (
            sum(value * value for value in clusters) / sum(clusters) / (4 / 3 * math.pi)
        ) ** (1 / 3)
        output.append(
            {
                "condition": key[0],
                "ploidy": key[1],
                "replicate": key[2],
                "cell_count": len(cells),
                "mean_cell_volume_um3": f"{fmean(value[0] for value in cells):.12f}",
                "mean_aspect_ratio": f"{fmean(value[1] for value in cells):.12f}",
                "cluster_count_24h": len(clusters),
                "weighted_mean_radius_um_24h": f"{weighted_radius:.12f}",
            }
        )
    return output


def longitudinal(source_root: Path) -> list[dict[str, Any]]:
    ploidy = {
        (row["Condition"], row["Line"], row["EvoTime"]): row["G1Peak"]
        for row in _read(source_root / "data/source_data/Fig2b.csv")
    }
    output = []
    for row in _read(source_root / "data/source_data/Fig1cde_evo.csv"):
        key = (row["Condition"], row["Line"], row["EvoTime"])
        output.append(
            {
                "condition": row["Condition"],
                "line": "ancestor" if row["Line"] == "NA" else row["Line"],
                "day": int(row["EvoTime"].removeprefix("t")),
                "weighted_mean_radius_um": row["Cluster.Weighted_mean_radius"],
                "mean_cell_volume_um3": row["Cell.Mean_volume"],
                "mean_aspect_ratio": row["Cell.Mean_AR"],
                "g1_peak_n": ploidy[key],
            }
        )
    return sorted(output, key=lambda item: (item["condition"], str(item["line"]), item["day"]))


def chromosome_copies(source_root: Path) -> list[dict[str, Any]]:
    output = []
    for row in _read(source_root / "data/source_data/Fig2d.csv"):
        output.append(
            {
                "condition": row["Condition"],
                "line": "ancestor" if row["Line"] == "NA" else row["Line"],
                "day": int(row["EvoTime"].removeprefix("t")),
                "chromosome": row["Chr"],
                "copy_number": int(row["CCN"]),
            }
        )
    return sorted(
        output,
        key=lambda item: (item["condition"], str(item["line"]), item["day"], item["chromosome"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    verify_sources(args.source_root)
    _write(
        args.output / "engineered-replicates-v1.0.csv",
        [
            "condition",
            "ploidy",
            "replicate",
            "cell_count",
            "mean_cell_volume_um3",
            "mean_aspect_ratio",
            "cluster_count_24h",
            "weighted_mean_radius_um_24h",
        ],
        engineered_replicates(args.source_root),
    )
    _write(
        args.output / "longitudinal-v1.0.csv",
        [
            "condition",
            "line",
            "day",
            "weighted_mean_radius_um",
            "mean_cell_volume_um3",
            "mean_aspect_ratio",
            "g1_peak_n",
        ],
        longitudinal(args.source_root),
    )
    _write(
        args.output / "chromosome-copy-v1.0.csv",
        ["condition", "line", "day", "chromosome", "copy_number"],
        chromosome_copies(args.source_root),
    )


if __name__ == "__main__":
    main()

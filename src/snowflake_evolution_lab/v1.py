"""Dependency-free implementation of the frozen v1 genome-sufficiency protocol."""

from __future__ import annotations

import csv
import itertools
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Any


@dataclass(frozen=True)
class EngineeredReplicate:
    condition: str
    ploidy: str
    replicate: str
    cell_count: int
    mean_cell_volume_um3: float
    mean_aspect_ratio: float
    cluster_count_24h: int
    weighted_mean_radius_um_24h: float


@dataclass(frozen=True)
class LongitudinalObservation:
    condition: str
    line: str
    day: int
    weighted_mean_radius_um: float
    mean_cell_volume_um3: float
    mean_aspect_ratio: float
    g1_peak_n: float


@dataclass(frozen=True)
class ChromosomeCopy:
    condition: str
    line: str
    day: int
    chromosome: str
    copy_number: int


def _stable(value: float) -> float:
    return round(value, 12)


def load_engineered(path: Path) -> list[EngineeredReplicate]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            EngineeredReplicate(
                condition=row["condition"],
                ploidy=row["ploidy"],
                replicate=row["replicate"],
                cell_count=int(row["cell_count"]),
                mean_cell_volume_um3=float(row["mean_cell_volume_um3"]),
                mean_aspect_ratio=float(row["mean_aspect_ratio"]),
                cluster_count_24h=int(row["cluster_count_24h"]),
                weighted_mean_radius_um_24h=float(row["weighted_mean_radius_um_24h"]),
            )
            for row in csv.DictReader(handle)
        ]


def load_longitudinal(path: Path) -> list[LongitudinalObservation]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            LongitudinalObservation(
                condition=row["condition"],
                line=row["line"],
                day=int(row["day"]),
                weighted_mean_radius_um=float(row["weighted_mean_radius_um"]),
                mean_cell_volume_um3=float(row["mean_cell_volume_um3"]),
                mean_aspect_ratio=float(row["mean_aspect_ratio"]),
                g1_peak_n=float(row["g1_peak_n"]),
            )
            for row in csv.DictReader(handle)
        ]


def load_chromosomes(path: Path) -> list[ChromosomeCopy]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            ChromosomeCopy(
                row["condition"],
                row["line"],
                int(row["day"]),
                row["chromosome"],
                int(row["copy_number"]),
            )
            for row in csv.DictReader(handle)
        ]


def exact_permutation_probability(diploid: list[float], tetraploid: list[float]) -> float:
    """One-sided exact probability for a tetraploid-minus-diploid mean difference."""
    if len(diploid) != 4 or len(tetraploid) != 4:
        raise ValueError("the frozen permutation test requires four replicates per group")
    observed = fmean(tetraploid) - fmean(diploid)
    pooled = diploid + tetraploid
    exceedances = 0
    allocations = 0
    for diploid_indices in itertools.combinations(range(8), 4):
        selected = set(diploid_indices)
        permuted_diploid = [pooled[index] for index in diploid_indices]
        permuted_tetraploid = [pooled[index] for index in range(8) if index not in selected]
        difference = fmean(permuted_tetraploid) - fmean(permuted_diploid)
        exceedances += difference >= observed - 1e-12
        allocations += 1
    return exceedances / allocations


def bootstrap_interval(
    diploid: list[float], tetraploid: list[float], iterations: int = 20_000
) -> tuple[float, float]:
    """Frozen percentile bootstrap interval for the independent replicate groups."""
    generator = random.Random(20_250_814)
    differences = []
    for _ in range(iterations):
        sampled_diploid = [generator.choice(diploid) for _ in diploid]
        sampled_tetraploid = [generator.choice(tetraploid) for _ in tetraploid]
        differences.append(fmean(sampled_tetraploid) - fmean(sampled_diploid))
    differences.sort()
    return differences[int((iterations - 1) * 0.025)], differences[int((iterations - 1) * 0.975)]


def _holm(probabilities: dict[str, float]) -> dict[str, float]:
    ordered = sorted(probabilities, key=probabilities.get)  # type: ignore[arg-type]
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for rank, name in enumerate(ordered):
        running = max(running, min(1.0, probabilities[name] * (total - rank)))
        adjusted[name] = running
    return adjusted


def _comparison(rows: list[EngineeredReplicate], condition: str, field: str) -> dict[str, Any]:
    diploid = [
        float(getattr(row, field))
        for row in rows
        if row.condition == condition and row.ploidy == "2N"
    ]
    tetraploid = [
        float(getattr(row, field))
        for row in rows
        if row.condition == condition and row.ploidy == "4N"
    ]
    mean_2n = fmean(diploid)
    mean_4n = fmean(tetraploid)
    low, high = bootstrap_interval(diploid, tetraploid)
    return {
        "condition": condition,
        "outcome": field,
        "replicates_per_group": 4,
        "mean_2n": _stable(mean_2n),
        "mean_4n": _stable(mean_4n),
        "difference_4n_minus_2n": _stable(mean_4n - mean_2n),
        "ratio_4n_over_2n": _stable(mean_4n / mean_2n),
        "bootstrap_95_ci": [_stable(low), _stable(high)],
        "exact_one_sided_permutation_probability": _stable(
            exact_permutation_probability(diploid, tetraploid)
        ),
    }


def analyze_v1(
    engineered: list[EngineeredReplicate],
    longitudinal: list[LongitudinalObservation],
    chromosomes: list[ChromosomeCopy],
) -> dict[str, Any]:
    outcomes = ["weighted_mean_radius_um_24h", "mean_cell_volume_um3", "mean_aspect_ratio"]
    comparisons = [
        _comparison(engineered, condition, outcome)
        for condition in ("PA", "PM")
        for outcome in outcomes
    ]
    primary = [row for row in comparisons if row["outcome"] == "weighted_mean_radius_um_24h"]
    adjusted = _holm(
        {row["condition"]: float(row["exact_one_sided_permutation_probability"]) for row in primary}
    )
    for row in primary:
        row["holm_adjusted_probability"] = _stable(adjusted[row["condition"]])

    evolved = [row for row in longitudinal if row.day >= 200]
    minimum_g1 = min(row.g1_peak_n for row in evolved)
    treatment_summaries: dict[str, dict[str, Any]] = {}
    for day in (600, 1000):
        values = {
            condition: [
                row.weighted_mean_radius_um
                for row in longitudinal
                if row.condition == condition and row.day == day
            ]
            for condition in ("PA", "PM")
        }
        treatment_summaries[str(day)] = {
            "mean_pa_radius_um": _stable(fmean(values["PA"])),
            "mean_pm_radius_um": _stable(fmean(values["PM"])),
            "pa_over_pm_ratio": _stable(fmean(values["PA"]) / fmean(values["PM"])),
            "maximum_pm_radius_um": _stable(max(values["PM"])),
            "pa_lines_above_300_um": sum(value > 300 for value in values["PA"]),
        }

    copy_groups: dict[tuple[str, str, int], list[ChromosomeCopy]] = defaultdict(list)
    for chromosome in chromosomes:
        copy_groups[(chromosome.condition, chromosome.line, chromosome.day)].append(chromosome)
    burdens = [
        {
            "condition": key[0],
            "line": key[1],
            "day": key[2],
            "aneuploidy_burden": sum(
                abs(chromosome.copy_number - (2 if key[2] == 0 else 4)) for chromosome in values
            ),
        }
        for key, values in sorted(copy_groups.items())
    ]

    sufficiency = treatment_summaries["1000"]
    sufficiency_passed = (
        minimum_g1 >= 3.4
        and sufficiency["pa_over_pm_ratio"] >= 5
        and sufficiency["maximum_pm_radius_um"] < 100
        and sufficiency["pa_lines_above_300_um"] >= 4
    )
    primary_passed = all(
        row["difference_4n_minus_2n"] > 0 and row["holm_adjusted_probability"] <= 0.05
        for row in primary
    )
    return {
        "schema_version": "1.0.0",
        "product_version": "1.0.0",
        "study_version": "1.0",
        "question": (
            "Does engineered tetraploidy increase snowflake-yeast phenotype, "
            "and is tetraploidy sufficient for macroscopic size?"
        ),
        "engineered_intervention": {
            "inference_unit": "engineered replicate strain",
            "comparisons": comparisons,
            "primary_criterion_passed": primary_passed,
        },
        "longitudinal_sufficiency": {
            "evolved_line_time_observations": len(evolved),
            "minimum_evolved_g1_peak_n": _stable(minimum_g1),
            "treatment_summaries": treatment_summaries,
            "criterion_passed": sufficiency_passed,
            "conclusion": (
                "Tetraploidy is not sufficient for macroscopic size across the two "
                "metabolic treatments."
            )
            if sufficiency_passed
            else "The prespecified test did not reject tetraploidy sufficiency.",
        },
        "aneuploidy_burdens": burdens,
        "overall_gate_passed": primary_passed and sufficiency_passed,
        "boundary": (
            "Source-author intervention and longitudinal data; no necessity, "
            "universal-threshold, independent wet-lab replication, or quantitative "
            "entanglement claim."
        ),
    }


def write_v1_results(
    engineered_path: Path, longitudinal_path: Path, chromosome_path: Path, destination: Path
) -> dict[str, Any]:
    results = analyze_v1(
        load_engineered(engineered_path),
        load_longitudinal(longitudinal_path),
        load_chromosomes(chromosome_path),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results

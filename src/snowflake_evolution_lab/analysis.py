"""Dependency-free analysis of the frozen MuLTEE figure-source trajectories."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from statistics import median
from typing import Any


@dataclass(frozen=True)
class Observation:
    day: int
    population: str
    aspect_ratio: float
    radius_um: float | None


def _stable(value: float) -> float:
    """Round published metrics so JSON is stable across supported Python builds."""
    return round(value, 12)


def load_trajectories(path: Path) -> list[Observation]:
    """Load the attributed figure-source values without imputing missing observations."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            Observation(
                day=int(row["day"]),
                population=row["population"],
                aspect_ratio=float(row["aspect_ratio"]),
                radius_um=float(row["radius_um"]) if row["radius_um"] else None,
            )
            for row in rows
        ]


def _rank(values: list[float]) -> list[float]:
    """Return average ranks for ties, starting at one."""
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = average
        start = end
    return ranks


def pearson(x: list[float], y: list[float]) -> float:
    """Calculate Pearson's product-moment correlation."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("correlation requires paired vectors with at least two values")
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y, strict=True))
    denominator = math.sqrt(sum((a - mean_x) ** 2 for a in x) * sum((b - mean_y) ** 2 for b in y))
    if denominator == 0:
        raise ValueError("correlation is undefined for a constant vector")
    return numerator / denominator


def spearman(x: list[float], y: list[float]) -> float:
    """Calculate Spearman's rank correlation with average ranks for ties."""
    return pearson(_rank(x), _rank(y))


def kendall_tau_b(x: list[float], y: list[float]) -> float:
    """Calculate Kendall's tau-b, including tie correction."""
    concordant = discordant = ties_x = ties_y = 0
    for i in range(len(x) - 1):
        for j in range(i + 1, len(x)):
            dx = (x[j] > x[i]) - (x[j] < x[i])
            dy = (y[j] > y[i]) - (y[j] < y[i])
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                ties_x += 1
            elif dy == 0:
                ties_y += 1
            elif dx == dy:
                concordant += 1
            else:
                discordant += 1
    denominator = math.sqrt((concordant + discordant + ties_x) * (concordant + discordant + ties_y))
    return (concordant - discordant) / denominator


def _largest_jump(rows: list[Observation], field: str) -> dict[str, float | int]:
    usable = [row for row in rows if getattr(row, field) is not None]
    changes: list[tuple[float, int, int]] = []
    for before, after in pairwise(usable):
        before_value = float(getattr(before, field))
        after_value = float(getattr(after, field))
        if field == "radius_um":
            change = math.log10(after_value) - math.log10(before_value)
        else:
            change = after_value - before_value
        changes.append((change, before.day, after.day))
    value, start, end = max(changes)
    return {"start_day": start, "end_day": end, "change": _stable(value)}


def _group(rows: Iterable[Observation]) -> dict[str, list[Observation]]:
    grouped: dict[str, list[Observation]] = defaultdict(list)
    for row in rows:
        grouped[row.population].append(row)
    return {name: sorted(values, key=lambda item: item.day) for name, values in grouped.items()}


def _log_radius(row: Observation) -> float:
    if row.radius_um is None:
        raise ValueError("radius is missing")
    return math.log10(row.radius_um)


def analyze(rows: list[Observation]) -> dict[str, Any]:
    """Run the frozen confirmatory, sensitivity, and exploratory analyses."""
    populations: list[dict[str, Any]] = []
    for name, population_rows in sorted(_group(rows).items()):
        paired = [row for row in population_rows if row.radius_um is not None]
        aspect = [row.aspect_ratio for row in paired]
        log_radius = [_log_radius(row) for row in paired]
        without_ancestor = [row for row in paired if row.day > 0]
        sensitivity_aspect = [row.aspect_ratio for row in without_ancestor]
        sensitivity_radius = [_log_radius(row) for row in without_ancestor]
        radius_jump = _largest_jump(population_rows, "radius_um")
        aspect_jump = _largest_jump(population_rows, "aspect_ratio")
        populations.append(
            {
                "population": name,
                "paired_observations": len(paired),
                "spearman_rho": _stable(spearman(aspect, log_radius)),
                "spearman_without_day0": _stable(spearman(sensitivity_aspect, sensitivity_radius)),
                "pearson_log_radius": _stable(pearson(aspect, log_radius)),
                "kendall_tau_b": _stable(kendall_tau_b(aspect, log_radius)),
                "largest_log_radius_jump": radius_jump,
                "largest_aspect_ratio_jump": aspect_jump,
                "jump_end_day_difference": int(radius_jump["end_day"])
                - int(aspect_jump["end_day"]),
            }
        )
    correlations = [row["spearman_rho"] for row in populations]
    positive = sum(value > 0 for value in correlations)
    exact_tail = sum(math.comb(5, k) for k in range(positive, 6)) / (2**5)
    return {
        "schema_version": "1.0.0",
        "product_version": "0.1.0",
        "study_version": "0.1",
        "question": (
            "Is the aspect-ratio versus cluster-radius association positive in every anaerobic "
            "MuLTEE lineage?"
        ),
        "source_observations": len(rows),
        "paired_observations": sum(row["paired_observations"] for row in populations),
        "inference_units": len(populations),
        "populations": populations,
        "confirmatory": {
            "positive_populations": positive,
            "total_populations": len(populations),
            "median_spearman_rho": _stable(median(correlations)),
            "exact_one_sided_sign_probability": _stable(exact_tail),
            "criterion": "all five population-level Spearman correlations are greater than zero",
            "passed": positive == 5,
        },
        "boundary": (
            "Directional concordance in five selected anaerobic laboratory populations; no causal, "
            "universal-threshold, or historical-origin claim."
        ),
    }


def write_results(source: Path, destination: Path) -> dict[str, Any]:
    """Analyze a source CSV and write stable, human-readable JSON."""
    results = analyze(load_trajectories(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results

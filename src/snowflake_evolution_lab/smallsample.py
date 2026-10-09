"""POST-HOC (not preregistered): exact small-sample inference for the frozen v1.0 contrasts.

The frozen analysis reports percentile-bootstrap intervals from four replicate strains per
group, plus an exact one-sided permutation probability. A percentile bootstrap on n = 4 is known
to be too narrow, and the evolved-line comparison (five PA vs five PM populations per transfer)
has no formal test. This module adds, with only the standard library:

* exact two-sided and one-sided permutation probabilities for any two small groups;
* an exact permutation-inversion 95% interval for the shift between groups (the set of shifts
  not rejected by the two-sided exact test), whose coverage does not rely on asymptotics;
* the exact 5-vs-5 permutation test and the rank separation of PA and PM evolved lines at each
  sampled transfer.
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path
from statistics import fmean
from typing import Any

ALPHA = 0.05
GRID_POINTS = 6001
MIN_LINES = 3


def exact_permutation_probability(a: list[float], b: list[float], *, two_sided: bool) -> float:
    """Exact permutation probability for the mean difference b - a."""
    pooled = a + b
    n_a = len(a)
    observed = fmean(b) - fmean(a)
    hits = total = 0
    for chosen in itertools.combinations(range(len(pooled)), n_a):
        picked = set(chosen)
        group_a = [pooled[i] for i in chosen]
        group_b = [pooled[i] for i in range(len(pooled)) if i not in picked]
        diff = fmean(group_b) - fmean(group_a)
        hits += (abs(diff) >= abs(observed) - 1e-12) if two_sided else (diff >= observed - 1e-12)
        total += 1
    return hits / total


def permutation_inversion_interval(
    a: list[float], b: list[float], alpha: float = ALPHA
) -> tuple[float, float]:
    """Shifts delta for which the two-sided exact test of (a, b - delta) does not reject at alpha.

    The set is found on a fine grid centred on the observed difference; it is an interval
    because the exact p-value is unimodal in the shift for these designs.
    """
    observed = fmean(b) - fmean(a)
    spread = (max(a + b) - min(a + b)) or 1.0
    low_edge, high_edge = observed - 2 * spread, observed + 2 * spread
    step = (high_edge - low_edge) / (GRID_POINTS - 1)
    inside = []
    for i in range(GRID_POINTS):
        delta = low_edge + i * step
        shifted = [x - delta for x in b]
        if exact_permutation_probability(a, shifted, two_sided=True) > alpha:
            inside.append(delta)
    if not inside:
        return (observed, observed)
    return (min(inside), max(inside))


def _engineered(path: Path) -> dict[tuple[str, str], list[float]]:
    groups: dict[tuple[str, str], list[float]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups.setdefault((row["condition"], row["ploidy"]), []).append(
                float(row["weighted_mean_radius_um_24h"])
            )
    return groups


def engineered_audit(path: Path) -> dict[str, Any]:
    groups = _engineered(path)
    out: dict[str, Any] = {}
    for condition in ("PA", "PM"):
        two_n, four_n = groups[(condition, "2N")], groups[(condition, "4N")]
        low, high = permutation_inversion_interval(two_n, four_n)
        out[condition] = {
            "difference_4n_minus_2n": fmean(four_n) - fmean(two_n),
            "exact_permutation_interval_95": [low, high],
            "exact_two_sided_probability": exact_permutation_probability(
                two_n, four_n, two_sided=True
            ),
            "exact_one_sided_probability": exact_permutation_probability(
                two_n, four_n, two_sided=False
            ),
            "smallest_attainable_two_sided_probability": 2
            / _combinations(len(two_n) + len(four_n), len(two_n)),
            "replicate_values_2n": two_n,
            "replicate_values_4n": four_n,
        }
    smallest_two_sided = min(v["exact_two_sided_probability"] for v in out.values())
    out["holm_adjusted_two_sided_across_backgrounds"] = min(1.0, 2 * smallest_two_sided)
    return out


def _combinations(n: int, k: int) -> int:
    return sum(1 for _ in itertools.combinations(range(n), k))


def longitudinal_audit(path: Path) -> dict[str, Any]:
    by_day: dict[str, dict[str, list[float]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            by_day.setdefault(row["day"], {}).setdefault(row["condition"], []).append(
                float(row["weighted_mean_radius_um"])
            )
    out: dict[str, Any] = {}
    for day, groups in sorted(by_day.items(), key=lambda kv: int(kv[0])):
        pa, pm = groups.get("PA", []), groups.get("PM", [])
        if min(len(pa), len(pm)) < MIN_LINES:
            continue
        out[day] = {
            "n_pa": len(pa),
            "n_pm": len(pm),
            "min_pa_um": min(pa),
            "max_pm_um": max(pm),
            "completely_separated": min(pa) > max(pm),
            "exact_two_sided_probability": exact_permutation_probability(pm, pa, two_sided=True),
            "smallest_attainable_two_sided_probability": 2
            / _combinations(len(pa) + len(pm), len(pa)),
        }
    return out


def build_small_sample_audit(data_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "label": "POST-HOC (not preregistered): exact small-sample inference",
        "engineered": engineered_audit(data_dir / "engineered-replicates-v1.0.csv"),
        "longitudinal": longitudinal_audit(data_dir / "longitudinal-v1.0.csv"),
    }

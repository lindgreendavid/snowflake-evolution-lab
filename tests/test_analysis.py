from __future__ import annotations

import json
from pathlib import Path

import pytest

from snowflake_evolution_lab.analysis import (
    Observation,
    analyze,
    kendall_tau_b,
    load_trajectories,
    pearson,
    spearman,
    write_results,
)

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_result_passes_without_imputation() -> None:
    results = analyze(load_trajectories(ROOT / "data" / "trajectories-v0.1.csv"))
    assert results["source_observations"] == 65
    assert results["paired_observations"] == 64
    assert results["inference_units"] == 5
    assert results["confirmatory"]["passed"] is True
    assert results["confirmatory"]["positive_populations"] == 5
    assert results["confirmatory"]["exact_one_sided_sign_probability"] == pytest.approx(0.03125)
    assert results["confirmatory"]["median_spearman_rho"] == pytest.approx(0.9560439560)


def test_sensitivities_remain_directionally_positive() -> None:
    populations = analyze(load_trajectories(ROOT / "data" / "trajectories-v0.1.csv"))["populations"]
    assert all(row["spearman_without_day0"] > 0.9 for row in populations)
    assert all(row["pearson_log_radius"] > 0.89 for row in populations)
    assert all(row["kendall_tau_b"] > 0.82 for row in populations)
    assert {row["population"] for row in populations} == {"PA1", "PA2", "PA3", "PA4", "PA5"}


def test_exploratory_jump_order_is_not_universal() -> None:
    populations = analyze(load_trajectories(ROOT / "data" / "trajectories-v0.1.csv"))["populations"]
    differences = [row["jump_end_day_difference"] for row in populations]
    assert any(value < 0 for value in differences)
    assert any(value > 0 for value in differences)


def test_correlations_handle_ties_and_validate_inputs() -> None:
    assert pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1)
    assert spearman([1, 2, 2, 4], [4, 3, 3, 1]) == pytest.approx(-1)
    assert kendall_tau_b([1, 1, 2], [1, 2, 3]) == pytest.approx(0.8164965809)
    with pytest.raises(ValueError, match="paired vectors"):
        pearson([1], [1])
    with pytest.raises(ValueError, match="constant vector"):
        pearson([1, 1], [2, 3])


def test_failed_directional_criterion_is_representable() -> None:
    rows = []
    for population_index in range(5):
        population = f"P{population_index}"
        for day, aspect, radius in [(0, 1.0, 2.0), (1, 2.0, 1.0), (2, 3.0, 0.5)]:
            rows.append(Observation(day, population, aspect, radius))
    result = analyze(rows)
    assert result["confirmatory"]["passed"] is False
    assert result["confirmatory"]["positive_populations"] == 0
    assert result["confirmatory"]["exact_one_sided_sign_probability"] == 1


def test_written_result_matches_committed_report(tmp_path: Path) -> None:
    destination = tmp_path / "result.json"
    write_results(ROOT / "data" / "trajectories-v0.1.csv", destination)
    generated = json.loads(destination.read_text(encoding="utf-8"))
    committed = json.loads((ROOT / "reports" / "results-v0.1.json").read_text(encoding="utf-8"))
    assert generated == committed

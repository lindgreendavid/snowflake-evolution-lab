from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from snowflake_evolution_lab.v1 import (
    analyze_v1,
    bootstrap_interval,
    exact_permutation_probability,
    load_chromosomes,
    load_engineered,
    load_longitudinal,
    write_v1_results,
)

ROOT = Path(__file__).resolve().parents[1]


def _inputs():  # type: ignore[no-untyped-def]
    return (
        load_engineered(ROOT / "data" / "engineered-replicates-v1.0.csv"),
        load_longitudinal(ROOT / "data" / "longitudinal-v1.0.csv"),
        load_chromosomes(ROOT / "data" / "chromosome-copy-v1.0.csv"),
    )


def test_v1_gate_passes_at_the_biological_replicate_level() -> None:
    result = analyze_v1(*_inputs())
    assert result["overall_gate_passed"] is True
    assert result["engineered_intervention"]["primary_criterion_passed"] is True
    assert result["longitudinal_sufficiency"]["criterion_passed"] is True
    assert result["longitudinal_sufficiency"]["evolved_line_time_observations"] == 40
    assert result["longitudinal_sufficiency"]["minimum_evolved_g1_peak_n"] == pytest.approx(
        3.488877338458
    )
    assert len(result["aneuploidy_burdens"]) == 42


def test_engineered_primary_effects_are_positive_and_exact() -> None:
    result = analyze_v1(*_inputs())
    primary = [
        row
        for row in result["engineered_intervention"]["comparisons"]
        if row["outcome"] == "weighted_mean_radius_um_24h"
    ]
    assert {row["condition"] for row in primary} == {"PA", "PM"}
    assert all(row["difference_4n_minus_2n"] > 7 for row in primary)
    assert all(
        row["exact_one_sided_permutation_probability"] == pytest.approx(1 / 70) for row in primary
    )
    assert all(row["holm_adjusted_probability"] == pytest.approx(1 / 35) for row in primary)
    assert all(row["bootstrap_95_ci"][0] > 0 for row in primary)


def test_longitudinal_contrast_rejects_sufficiency() -> None:
    summaries = analyze_v1(*_inputs())["longitudinal_sufficiency"]["treatment_summaries"]
    assert summaries["600"]["pa_over_pm_ratio"] == pytest.approx(6.6693589973)
    assert summaries["1000"]["pa_over_pm_ratio"] == pytest.approx(8.8590348229)
    assert summaries["1000"]["maximum_pm_radius_um"] < 100
    assert summaries["1000"]["pa_lines_above_300_um"] == 5


def test_exact_statistics_are_deterministic_and_validate_group_size() -> None:
    assert exact_permutation_probability([1, 2, 3, 4], [5, 6, 7, 8]) == pytest.approx(1 / 70)
    first = bootstrap_interval([1, 2, 3, 4], [5, 6, 7, 8], iterations=1000)
    second = bootstrap_interval([1, 2, 3, 4], [5, 6, 7, 8], iterations=1000)
    assert first == second
    with pytest.raises(ValueError, match="four replicates"):
        exact_permutation_probability([1, 2], [3, 4])


def test_failed_v1_gate_is_representable() -> None:
    engineered, longitudinal, chromosomes = _inputs()
    engineered = [
        replace(row, weighted_mean_radius_um_24h=1.0) if row.ploidy == "4N" else row
        for row in engineered
    ]
    longitudinal = [
        replace(row, weighted_mean_radius_um=50.0, g1_peak_n=2.0)
        if row.condition == "PA" and row.day == 1000
        else row
        for row in longitudinal
    ]
    result = analyze_v1(engineered, longitudinal, chromosomes)
    assert result["overall_gate_passed"] is False
    assert result["engineered_intervention"]["primary_criterion_passed"] is False
    assert result["longitudinal_sufficiency"]["criterion_passed"] is False
    assert result["longitudinal_sufficiency"]["conclusion"].startswith("The prespecified test")


def test_written_v1_result_matches_committed_report(tmp_path: Path) -> None:
    destination = tmp_path / "result.json"
    write_v1_results(
        ROOT / "data" / "engineered-replicates-v1.0.csv",
        ROOT / "data" / "longitudinal-v1.0.csv",
        ROOT / "data" / "chromosome-copy-v1.0.csv",
        destination,
    )
    generated = json.loads(destination.read_text(encoding="utf-8"))
    committed = json.loads((ROOT / "reports" / "results-v1.0.json").read_text(encoding="utf-8"))
    assert generated == committed

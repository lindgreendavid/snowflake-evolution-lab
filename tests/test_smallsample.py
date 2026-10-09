import pytest

from snowflake_evolution_lab.smallsample import (
    build_small_sample_audit,
    exact_permutation_probability,
    permutation_inversion_interval,
)


def test_exact_probability_for_complete_separation_is_the_minimum():
    a, b = [1.0, 2.0, 3.0, 4.0], [10.0, 11.0, 12.0, 13.0]
    assert exact_permutation_probability(a, b, two_sided=False) == pytest.approx(1 / 70)
    assert exact_permutation_probability(a, b, two_sided=True) == pytest.approx(2 / 70)


def test_exact_probability_is_one_for_identical_groups():
    assert exact_permutation_probability([1.0, 2.0], [1.0, 2.0], two_sided=True) == 1.0


def test_inversion_interval_contains_the_observed_shift_and_is_wider_than_zero():
    a, b = [10.0, 10.5, 9.5, 10.2], [15.0, 15.4, 14.6, 15.1]
    low, high = permutation_inversion_interval(a, b)
    assert low < 5.0 < high
    assert high - low > 0.5


def test_inversion_interval_excludes_zero_for_a_clear_effect_and_includes_it_for_none():
    low, _ = permutation_inversion_interval([1.0, 1.1, 0.9, 1.0], [9.0, 9.2, 8.8, 9.1])
    assert low > 0
    low0, high0 = permutation_inversion_interval([1.0, 2.0, 3.0, 4.0], [1.5, 2.5, 3.5, 4.5])
    assert low0 < 0 < high0


def test_build_audit_roundtrip(tmp_path):
    (tmp_path / "engineered-replicates-v1.0.csv").write_text(
        "condition,ploidy,replicate,weighted_mean_radius_um_24h\n"
        + "".join(
            f"{c},{p},Rep{i},{v}\n"
            for c, base in (("PA", 20.0), ("PM", 25.0))
            for p, shift in (("2N", 0.0), ("4N", 7.0))
            for i, v in enumerate([base + shift + d for d in (0.0, 0.2, -0.2, 0.1)], 1)
        )
    )
    rows = ["condition,line,day,weighted_mean_radius_um"]
    for cond, size in (("PA", 300.0), ("PM", 50.0)):
        for line in range(1, 6):
            rows.append(f"{cond},{line},1000,{size + line}")
            rows.append(f"{cond},{line},0,20")
    rows.append("PA,6,5,1")
    (tmp_path / "longitudinal-v1.0.csv").write_text("\n".join(rows) + "\n")
    out = build_small_sample_audit(tmp_path)
    assert out["label"].startswith("POST-HOC")
    assert out["engineered"]["PA"]["exact_one_sided_probability"] == pytest.approx(1 / 70)
    assert out["engineered"]["holm_adjusted_two_sided_across_backgrounds"] == pytest.approx(4 / 70)
    assert out["longitudinal"]["1000"]["completely_separated"] is True
    assert out["longitudinal"]["1000"]["exact_two_sided_probability"] == pytest.approx(2 / 252)
    assert "5" not in out["longitudinal"]

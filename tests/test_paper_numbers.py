import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEX = (ROOT / "paper" / "paper.tex").read_text(encoding="utf-8")
AUDIT = json.loads((ROOT / "reports" / "post-release-small-sample.json").read_text())
FROZEN = json.loads((ROOT / "reports" / "results-v1.0.json").read_text())


def test_exact_intervals_in_paper_match_the_audit_file():
    for condition in ("PA", "PM"):
        low, high = AUDIT["engineered"][condition]["exact_permutation_interval_95"]
        assert f"{low:.3f}" in TEX and f"{high:.3f}" in TEX


def test_frozen_bootstrap_intervals_in_paper_match_the_frozen_results():
    primary = [
        c
        for c in FROZEN["engineered_intervention"]["comparisons"]
        if c["outcome"] == "weighted_mean_radius_um_24h"
    ]
    for comparison in primary:
        low, high = comparison["bootstrap_95_ci"]
        assert f"{low:.3f}" in TEX and f"{high:.3f}" in TEX
        assert f"{comparison['difference_4n_minus_2n']:.3f}" in TEX


def test_longitudinal_numbers_in_paper_match_the_audit_file():
    for day in ("600", "1000"):
        entry = AUDIT["longitudinal"][day]
        assert entry["completely_separated"] is True
        assert f"{entry['min_pa_um']:.1f}" in TEX and f"{entry['max_pm_um']:.1f}" in TEX
    assert f"{AUDIT['longitudinal']['200']['exact_two_sided_probability']:.3f}" in TEX
    assert f"{AUDIT['longitudinal']['400']['exact_two_sided_probability']:.3f}" in TEX
    assert f"{AUDIT['engineered']['holm_adjusted_two_sided_across_backgrounds']:.4f}" in TEX

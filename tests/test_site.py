from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_site_has_accessible_research_structure() -> None:
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert 'href="#main"' in html
    assert 'id="experiment"' in html
    assert 'id="boundary"' in html
    assert 'aria-live="polite"' in html
    assert "not microscopy" in html
    assert "5 / 5 positive" in html
    assert "Measured</strong> mean cell aspect ratio" in html
    assert "Modelled</strong> branch topology" in html
    assert 'data-view="packing"' in html
    assert 'data-view="fracture"' in html
    assert 'id="mechanism-value"' in html
    assert "chitinous tree junction" in html
    assert "steric retention · not a bond" in html
    assert "severed junction" in html
    assert 'id="fracture-outcome"' in html
    assert 'id="genome"' in html
    assert 'id="chromosome-grid"' in html
    assert 'data-genome-day="1000"' in html
    assert "Genome duplication helps. It is not enough." in html
    assert "Not measured here:" in html


def test_animation_keeps_empirical_and_modelled_quantities_separate() -> None:
    javascript = (ROOT / "site" / "app.js").read_text(encoding="utf-8")
    assert "seededRandom" in javascript
    assert "Source value missing" in javascript
    assert "Visual interpolation between published measurements" in javascript
    assert "recognition seed only" in javascript
    assert "not measured cellular stress" in javascript
    assert "without adhesion or bond repair" in javascript
    assert "crossComponentContacts" in javascript
    assert "One-junction fracture stress test" in javascript
    assert "subtreeIndices" in javascript
    assert "appendJunction" in javascript
    assert "Sterically retained" in javascript


def test_site_data_matches_report_and_has_missing_value() -> None:
    report = json.loads((ROOT / "reports" / "results-v0.1.json").read_text(encoding="utf-8"))
    site_report = json.loads(
        (ROOT / "site" / "data" / "results-v0.1.json").read_text(encoding="utf-8")
    )
    trajectories = json.loads(
        (ROOT / "site" / "data" / "trajectories-v0.1.json").read_text(encoding="utf-8")
    )
    assert report == site_report
    assert len(trajectories) == 65
    assert sum(row["radius_um"] is None for row in trajectories) == 1


def test_v1_site_data_matches_report_and_exposes_longitudinal_evidence() -> None:
    report = json.loads((ROOT / "reports" / "results-v1.0.json").read_text(encoding="utf-8"))
    site_report = json.loads(
        (ROOT / "site" / "data" / "results-v1.0.json").read_text(encoding="utf-8")
    )
    chromosomes = json.loads(
        (ROOT / "site" / "data" / "chromosome-copy-v1.0.json").read_text(encoding="utf-8")
    )
    longitudinal = json.loads(
        (ROOT / "site" / "data" / "longitudinal-v1.0.json").read_text(encoding="utf-8")
    )
    assert report == site_report
    assert report["overall_gate_passed"] is True
    assert len(chromosomes) == 672
    assert len(longitudinal) == 42
    assert {row["day"] for row in longitudinal if row["condition"] in {"PA", "PM"}} == {
        0,
        200,
        400,
        600,
        1000,
    }


def test_css_has_responsive_and_reduced_motion_contracts() -> None:
    css = (ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 620px)" in css
    assert "prefers-reduced-motion: reduce" in css
    assert ":focus-visible" in css

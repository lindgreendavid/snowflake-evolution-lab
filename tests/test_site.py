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


def test_css_has_responsive_and_reduced_motion_contracts() -> None:
    css = (ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 620px)" in css
    assert "prefers-reduced-motion: reduce" in css
    assert ":focus-visible" in css

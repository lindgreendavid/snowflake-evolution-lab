from __future__ import annotations

import json
import sys
from pathlib import Path

from snowflake_evolution_lab.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_writes_result(monkeypatch, tmp_path: Path, capsys) -> None:
    output = tmp_path / "results.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "snowflake-evolution",
            "--source",
            str(ROOT / "data" / "trajectories-v0.1.csv"),
            "--output",
            str(output),
        ],
    )
    main()
    assert "PASS: 5/5" in capsys.readouterr().out
    assert json.loads(output.read_text(encoding="utf-8"))["confirmatory"]["passed"] is True

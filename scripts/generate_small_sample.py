#!/usr/bin/env python3
"""Generate the POST-HOC exact small-sample audit (not part of the frozen v1.0 results)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from snowflake_evolution_lab.smallsample import build_small_sample_audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        json.dump(build_small_sample_audit(Path(args.data_dir)), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize current upgrade artifact counts under upgrade_outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upgrade-outputs", required=True)
    args = parser.parse_args()

    base = Path(args.upgrade_outputs)
    summary = {
        "tracker": int((base / "TRANSFORMERS_V5_UPGRADE_TRACKER.md").exists()),
        "runbooks": len(list((base / "runbook").glob("*.md"))) if (base / "runbook").exists() else 0,
        "steps": len(list((base / "steps").glob("*.md"))) if (base / "steps").exists() else 0,
        "validation": len(list((base / "validation").glob("*.md"))) if (base / "validation").exists() else 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

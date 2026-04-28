#!/usr/bin/env python3
"""Create a structured step execution note."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE = """# {title}

## Goal

## Why Now

## Runnable-Path Blocker

## Scope Classification

- classification:
- runbook required:

## Files

## Changes

## Unsupported Paths Intentionally Skipped

## Upstream Alignment Check

## Verification

## Threshold Touched

- touched:
- rationale:

## Current Conclusion

## Next Step
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(title=args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Create a structured runbook markdown skeleton."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE = """# Runbook: {title}

## Inputs

- source tag: `{source}`
- target tag: `{target}`
- spreadsheet: `{spreadsheet}`

## Why This Runbook Exists

- step target:
- blocker role:
- scope classification:
- why a runbook is required now:

## Outputs

- add:
- modify:

## Upgrade Graph

S1 -> S2

## Steps

### S1
- Files:
- Change:
- Unsupported paths intentionally skipped:
- Upstream alignment check:
- Done when:

### S2
- Files:
- Change:
- Unsupported paths intentionally skipped:
- Upstream alignment check:
- Done when:

## Checklist

- [ ] runnable-path blocker is explicit
- [ ] structural
- [ ] API semantics
- [ ] consolidation
- [ ] step note will capture verification and threshold status

## Guardrails

- banned symbols:
- required exports:
- threshold changes allowed:
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--spreadsheet", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TEMPLATE.format(
            title=args.title,
            source=args.source,
            target=args.target,
            spreadsheet=args.spreadsheet,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

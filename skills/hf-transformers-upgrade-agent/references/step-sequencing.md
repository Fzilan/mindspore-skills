# Step Sequencing

Do not create steps directly from spreadsheet row order.

## Rule 1. Prioritize the minimum runnable path

Early steps should first unblock:

- `from_pretrained()`
- minimal model load
- minimal forward
- `generate()`

This usually means the first shared-component steps should concentrate on:

- `modeling_utils.py`
- generation core
- only the minimum supporting public components needed by those paths

## Rule 2. Separate "unblock" from "complete"

Before broad component completeness work:

- unblock one representative model load path
- unblock one representative generation path

Only then broaden to:

- modeling foundation
- processing and extractors
- pipelines
- auto entry
- trainer
- root and shared utils
- integrations

## Rule 3. Tail work comes last

The following belong near the end:

- remaining task pipelines
- optional additions
- ignore and defer finalization
- provenance normalization
- version bump

## Rule 4. Tests are post-upgrade validation layers

After the shared upgrade path is stable, validate in this order:

1. structural and import validation
2. UT sweep
3. real-weight validation
4. new-model migration proof

# Testing Workflow

Use post-upgrade testing in layers.

## 1. UT sweep

Run model tests under:

- `tests/transformers_tests/models/`

Rules:

- test one model or one cluster at a time
- classify every failure before editing
- do not change numeric thresholds by default
- if a threshold change is required, record the measured mismatch and reason

## 2. Real-weight validation

Treat real-weight validation separately from UT.

Classify issues as:

- script or harness adaptation issue
- shared component issue
- model-specific sync gap
- expected warning

## 3. New-model migration proof

This new-model migration proof is the final compatibility check for the
upgraded library stack.

After the upgrade is functionally complete, prove that the upgraded stack can
still accept one model newly added in the target upstream version.

Rules:

- migrate fast UT by default
- do not migrate slow tests for this proof unless the user explicitly asks
- do not add real-weight proof for this migrated model unless the user explicitly asks
- keep proof scope narrow and use it to validate the upgraded shared stack, not
  to start a second broad upgrade project

For this final proof, reuse `migrate-agent` instead of reimplementing
single-model migration logic here.

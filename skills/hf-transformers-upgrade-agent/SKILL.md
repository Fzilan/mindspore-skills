---
name: hf-transformers-upgrade-agent
description: Plan and execute a library-level `mindone.transformers` upgrade against a target Hugging Face `transformers` version by generating the upgrade spreadsheet, classifying shared-component changes, sequencing steps around the minimum runnable path, creating runbooks only for high-risk steps, and driving layered validation.
---

# HF Transformers Upgrade Agent

You are a library upgrade agent.

Drive a `mindone.transformers` shared-component upgrade against a target
Hugging Face `transformers` release from spreadsheet generation through
execution, validation, and closure.

Use this skill for library-level upgrade work across public components such as
`modeling_utils.py`, generation, processing, pipelines, trainer, and shared
utils. Do not use it for single-model migration, post-run failure diagnosis, or
standalone environment repair.

## Hard Rules

- Treat the spreadsheet as a work pool, not as the execution order.
- Treat upstream diff review as the source of truth for upgrade scope. Do not
  infer upgrade completeness from smoke tests alone.
- Sequence steps around the minimum runnable path first.
- Prioritize early work that unblocks:
  - `from_pretrained()`
  - minimal model load
  - minimal forward
  - `generate()`
- Do not treat a passing minimum runnable path as evidence that the
  shared-component upgrade is complete.
- Before that runnable path is validated, do not broaden into pipelines,
  trainer, integrations, or trailing utilities except for direct blockers.
- Do not pre-author all runbooks at the start. Create them only when a step is
  judged runbook-worthy by the scope framework.
- Every execution step must explicitly record step target, blocker role, scope
  classification, and runbook decision.
- A step without both a tracker update and a step record is incomplete.
- Keep unsupported PyTorch-only, quantization, and distributed features out of
  scope unless the current MindOne upgrade explicitly supports them.
- Separate structural validation, UT sweep, real-weight validation, and
  new-model migration proof.
- For the final new-model proof, migrate fast UT by default. Do not add slow or
  real-weight proof for that migrated model unless the user explicitly asks.

## Workflow

1. `planning-and-classification`
2. `tracker-bootstrap`
3. `step-sequencing`
4. `step-execution-loop`
5. `validation-and-testing`
6. `closure-and-proof`

## Stage 1. Planning and Classification

You must:

- resolve the local `mindone` and `transformers` repositories
- determine the source and target version tags
- run `scripts/collect_upgrade_data.py`
- produce `upgrade_data_{source}_to_{target}.xlsx`
- classify spreadsheet rows by priority, addition class, and actual notes
- replace the row-5 placeholder with a real repo change summary

Load only these references unless blocked:

- `references/planning.md`
- `references/excel-classification.md`
- `references/guardrails.md`

## Stage 2. Tracker Bootstrap

You must:

- create a top-level tracker document
- define stage overview and current status
- use the tracker as the source of truth for upgrade progress

Use:

- `references/tracker-workflow.md`
- `scripts/bootstrap_upgrade_tracker.py`

## Stage 3. Step Sequencing

You must:

- identify which components block:
  - `from_pretrained()`
  - minimal load
  - minimal forward
  - `generate()`
- schedule those steps first
- defer completeness work for pipelines, trainer, and trailing utilities until
  the runnable path is stable
- refuse to expand into broad shared-component cleanup until the current blocker
  is fixed or explicitly deferred
- use any early smoke test only to identify or confirm blockers for step
  ordering, not to decide that the library-level upgrade is already complete

Use:

- `references/step-sequencing.md`
- `references/upgrade-rules.md`

## Stage 4. Step Execution Loop

For each step:

1. define the step target and goal
2. state what runnable-path blocker the step unblocks
3. inspect upstream diff and current MindOne implementation
4. classify the step as small patch, medium refactor, or major restructure
5. decide whether a runbook is required before editing
6. if needed, create or extend a dedicated runbook
7. execute the change
8. write the step execution record
9. update the tracker
10. record the next highest-priority unresolved shared component

Do not create a runbook for every step by default.

Use:

- `references/scope_and_runbook_framework.md`
- `references/scope_and_runbook_framework.zh.md`
- `references/execution-records.md`
- `references/upgrade-rules.md`
- `examples/runbook_modeling_utils.md`
- `scripts/bootstrap_runbook.py`
- `scripts/bootstrap_step_note.py`

## Stage 5. Validation and Testing

After the shared-component path is stable, perform and record:

- structural and import validation
- UT sweep under `tests/transformers_tests/models/`
- real-weight validation

For UT and runtime failures, classify the cause before editing:

- shared component issue
- model-specific upgrade gap
- test harness mismatch
- expected unsupported path
- precision threshold issue

Do not use threshold changes as the first-line fix.

Use:

- `references/validation-workflow.md`
- `references/testing-workflow.md`
- `references/upgrade-rules.md`

## Stage 6. Closure and Proof

You must:

- normalize license and provenance headers on new upstream-adapted files
- update `mindone.transformers.__version__` only after the shared-component
  upgrade scope has been reviewed and the tracker plus step records are closed
- write the final completion summary
- classify remaining gaps as completed, deferred review, or explicitly not followed
- prove the upgraded stack can still accept a new upstream model by selecting
  one target-version-added model and handing that proof step to `migrate-agent`
- reuse `migrate-agent` for that proof instead of rebuilding single-model
  migration logic inside this skill

Use:

- `references/closure-checklist.md`
- `references/case-study-v4.57.1-to-v5.0.0.md`
- `references/upgrade-rules.md`

## References

Load only the references needed by the current stage:

- `references/planning.md`
- `references/excel-classification.md`
- `references/step-sequencing.md`
- `references/scope_and_runbook_framework.md`
- `references/scope_and_runbook_framework.zh.md`
- `references/tracker-workflow.md`
- `references/execution-records.md`
- `references/validation-workflow.md`
- `references/testing-workflow.md`
- `references/closure-checklist.md`
- `references/guardrails.md`
- `references/upgrade-rules.md`
- `references/case-study-v4.57.1-to-v5.0.0.md`

## Scripts

- `scripts/collect_upgrade_data.py`
- `scripts/bootstrap_upgrade_tracker.py`
- `scripts/bootstrap_runbook.py`
- `scripts/bootstrap_step_note.py`
- `scripts/summarize_upgrade_state.py`

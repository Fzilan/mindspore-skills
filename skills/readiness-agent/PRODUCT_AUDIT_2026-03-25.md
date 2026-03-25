# Readiness-Agent Product Audit

Date: 2026-03-25

## Audit Verdict

Current state:

- product-grade MVP remains credible for controlled local use
- recent P0 Python hardening materially improves real server robustness
- helper scripts now target Python 3.9 compatibility and the skill now has an
  explicit selected-workspace-Python contract
- full confidence still requires a full pytest rerun in an environment with
  `pytest` installed, plus one more pass on end-to-end fix-mode closure

Recommended readiness level:

- still appropriate for internal alpha / `ms-cli` integration experiments
- stronger than the earlier prompt-first MVP because Python control-plane
  behavior is now explicit instead of implicit
- not yet fully closed as a final GA skill

## What Is Already Product-Complete

- single-machine readiness certification is centered on one user-facing
  outcome: `READY` / `WARN` / `BLOCKED`
- execution target discovery is explicit and evidence-driven
- dependency closure is target-scoped, not machine-generic
- framework/runtime probing is selected-environment-aware
- selected workspace Python can now be expressed explicitly through
  `selected_python` and `selected_env_root`
- the deterministic helper pipeline now has a dedicated selected-Python
  resolution stage
- downstream probing and task smoke can now use the selected workspace Python
  instead of silently trusting the host interpreter
- helper scripts have been moved away from Python 3.10-only type syntax so the
  control plane is compatible with Python 3.9+
- explicit task smoke is supported through `task_smoke_cmd`
- blocker taxonomy is normalized and stable
- native `env_fix` planning and controlled execution exist
- revalidation is enforced from `needs_revalidation` coverage, not from a
  placeholder boolean
- final report preserves internal evidence fields and user-visible summary
- realistic workspace fixtures now cover training-style and inference-style
  workspaces

## Current Implemented Pipeline

1. `resolve_selected_python.py`
2. `discover_execution_target.py`
3. `build_dependency_closure.py`
4. `run_task_smoke.py` when `task_smoke_cmd` exists
5. `collect_readiness_checks.py`
6. `normalize_blockers.py`
7. `plan_env_fix.py`
8. `execute_env_fix.py`
9. rerun required checks when remediation changes the environment
10. `build_readiness_report.py`

## Recent P0 Python Hardening

- new manifest inputs: `selected_python` and `selected_env_root`
- new helper: `resolve_selected_python.py`
- discovery now records selected-Python metadata into the execution target
- dependency closure now rebuilds Python facts from the selected workspace
  interpreter instead of defaulting to the current interpreter
- task smoke now skips with an explicit environment reason when selected Python
  is missing, rather than silently falling back to a host interpreter
- readiness checks now surface selected-Python resolution failures as
  environment blockers
- helper scripts now use Python 3.9-compatible typing forms instead of
  Python 3.10-only `X | None` syntax

## Evidence Of Stability

- historical baseline before this P0 round: `31 passed, 1 warning`
- current local session after the P0 edits: all readiness helper scripts
  compile successfully with `python -m py_compile`
- selected-Python resolution was manually validated with an explicit Python
  interpreter
- the `discover_execution_target -> build_dependency_closure ->
  collect_readiness_checks` path was manually validated with the new
  selected-Python contract
- full pytest rerun is still pending in this workspace because the local
  Python environment used for development does not currently have `pytest`
  installed

## Remaining Product Gaps

### 1. Automatic No-Env-To-Ready Closure Is Not Fully Closed Yet

The skill now knows how to resolve a selected workspace Python, but the full
automatic path from:

- no usable workspace virtual environment
- selected-Python blocker
- `env_fix` creates or repairs the environment
- downstream stages re-enter using the newly created interpreter

is not yet closed by a single top-level driver in this repo.

The contract is now much clearer, but the repair-and-reenter loop still needs
explicit orchestration closure.

### 2. Real Framework Smoke Is Still Minimal

Current framework smoke verifies the minimum import/bootstrap prerequisite,
not a real task-level framework execution path such as:

- one tensor on device
- one forward pass
- one train-step primitive

This is acceptable for now, but stronger task evidence would reduce false
`READY` in edge cases where import succeeds but runtime usage still fails.

### 3. `env_fix` Capability Is Still Narrow By Design

The current native remediation scope is intentionally limited to safe
user-space actions. This is correct for product safety, but it means:

- no system-layer repair
- no CANN / driver remediation
- no config mutation
- no dataset repair
- no model code patching

This is not a flaw, but it should remain explicit in integration plans.

### 4. No Formal `ms-cli` Adapter Contract Yet

The skill now has a clearer internal Python contract and stable artifacts, but
the adapter layer that maps:

- user request
- `mode`
- `target`
- `selected_python` / `selected_env_root`
- artifact locations
- final surfaced summary

into `ms-cli` runtime behavior is not yet formalized in this repo.

## Recommended Final Steps

1. Close selected-Python orchestration and repair loop.
   Define:
   - when `resolve_selected_python.py` must run
   - how `selected_python` and `selected_env_root` flow into downstream helpers
   - how `fix` / `auto` mode creates an environment and reruns the pipeline
     with the new interpreter

2. Rerun and expand the test matrix.
   Add:
   - a full pytest rerun in an environment that has `pytest`
   - a regression case for host Python 3.9 plus workspace `.venv` Python 3.10
   - a regression case for workspace Python 3.9 selected successfully
   - a regression case for missing `.venv` followed by `env_fix` recovery

3. Optionally strengthen runtime evidence.
   Add one more controlled smoke tier for frameworks or task kinds where
   minimal runtime execution is safe and deterministic.

## Bottom Line

`readiness-agent` is no longer just a prompt-first concept skill.
It now behaves like a real certification product with deterministic helpers,
native remediation, revalidation, stable artifacts, realistic fixtures, and a
much clearer Python control-plane story.

The biggest remaining work is no longer basic Python survivability. It is
closing the automatic repair-and-reenter loop and strengthening real runtime
evidence.

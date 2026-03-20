# Setup-Agent Rework Trace

Date: 2026-03-20

## Purpose

This document records the intent, scope, decisions, and implementation shape of
the `setup-agent` rework completed on 2026-03-20. It is meant to preserve the
reasoning trail so future optimization work can start from the full context
instead of rediscovering why the current structure exists.

## Why This Rework Happened

The original `setup-agent` had several structural problems:

1. It mixed Ascend/NPU and Nvidia/GPU setup in one skill, which made routing
   ambiguous and diluted the main use case.
2. It only modeled `MindSpore + CANN` on Ascend and did not explicitly cover
   the common `PyTorch + torch_npu + CANN` path.
3. It implied system-layer auto-fix behavior for driver and toolkit problems,
   which is too risky and not aligned with the actual safe automation boundary.
4. It did not treat `uv` as the primary Python environment entry point.
5. It was not exposed from the repository root `AGENTS.md`, so it was difficult
   for an agent to trigger reliably.
6. The entry `SKILL.md` was too document-heavy for an execution prompt, making
   it harder for a model to lock onto the main decision path.
7. The tests only checked for file existence and some table shape, not the key
   workflow rules that determine whether the skill behaves correctly.

## Rework Goals

The rework targeted these goals:

1. Make `setup-agent` Ascend-only.
2. Support both framework paths on Ascend:
   - `MindSpore + CANN`
   - `PyTorch + torch_npu + CANN`
3. Limit automation to user-space actions:
   - install user-level `uv`
   - install Python packages inside a user-confirmed `uv` environment
4. Never auto-install:
   - NPU driver
   - firmware
   - CANN toolkit
   - system Python
5. Force the workflow to validate the system layer before doing Python work.
6. Require explicit user confirmation when reusing or creating a `uv`
   environment.
7. Produce outputs consistent with the repository reporting contract.
8. Separate the high-density execution prompt from the longer reference data.

## Files Changed

### Repository routing

- `AGENTS.md`

Changes:
- Added `setup-agent` to the repository skill list
- Added trigger hints for environment setup scenarios
- Clarified boundaries between:
  - `setup-agent`
  - `failure-agent`
  - `performance-agent`

Reason:
- Without this, the skill existed but was not reliably discoverable from the
  repo-level routing rules.

### Skill manifest

- `skills/setup-agent/skill.yaml`

Changes:
- Scope changed from mixed Ascend/GPU wording to local Ascend-only wording
- Added inputs for:
  - `frameworks`
  - `task_type`
  - `uv_env_mode`
  - `python_version`
- Restricted `target` to `local`
- Removed unrelated `composes`
- Changed permissions to require:
  - network
  - workspace write
- Updated tags from generic GPU-oriented tags to Ascend/`torch_npu`/`uv`

Reason:
- The manifest now reflects the actual supported behavior and no longer claims
  a cross-platform scope that the workflow does not support.

### Skill entry prompt

- `skills/setup-agent/SKILL.md`

Changes:
- Rewritten from a long mixed guide into a compact execution-oriented prompt
- Kept only the parts that should steer model behavior directly:
  - scope
  - hard rules
  - workflow
  - compatibility source
  - reporting requirements
  - out-of-scope list
- Explicitly preserved these decision points:
  - system layer must be healthy before Python work
  - `uv` must exist before Python package work
  - existing `uv` environments must be confirmed with the user
  - new `uv` environments require a user-confirmed Python version
  - Python packages must never be installed into the system interpreter

Reason:
- The prompt is now shaped for model execution rather than human reading.
- Long explanations and lookup-heavy detail were moved to `references/`.

### Reference data

- `skills/setup-agent/references/ascend-compat.md`
- Deleted: `skills/setup-agent/references/nvidia-compat.md`

Changes:
- Removed the Nvidia reference because GPU support was intentionally removed
- Restructured the Ascend reference into a retrieval-friendly format:
  - `Quick Use`
  - `Driver / Firmware / CANN Matrix`
  - `MindSpore on Ascend`
  - `PyTorch + torch_npu on Ascend`
  - `Detection Hints`
  - `Official Installation Guides`
  - `Repair Policy`

Reason:
- `SKILL.md` should drive decisions; `references/` should answer lookup
  questions quickly.
- The new structure helps future models find the exact section they need with
  less prompt noise.

### Tests

- `skills/setup-agent/tests/test_references.py`

Changes:
- Replaced weak existence-only tests with behavior-contract checks
- Added coverage for:
  - Ascend-only scope
  - no Nvidia reference usage
  - `uv` as a required gate before Python installs
  - prohibition on driver/CANN auto-install
  - mandatory user confirmation for `uv` environment choice
  - stop behavior when the system layer fails
  - both framework paths being represented
  - standard reporting contract references
  - root `AGENTS.md` exposure

Reason:
- The goal was to guard workflow intent, not just file presence.

## Core Design Decisions

### 1. Ascend-only was a deliberate narrowing, not an omission

The skill originally tried to do too much. Restricting it to Ascend improves:
- routing precision
- prompt clarity
- compatibility reasoning
- maintenance cost

GPU/Nvidia setup should not remain half-supported inside the same skill.

### 2. The system layer is authoritative

The workflow now enforces this order:

1. OS and device visibility
2. driver / firmware / CANN
3. `set_env.sh` sourcing
4. `uv`
5. framework packages
6. model runtime dependencies

This order prevents a common failure mode where Python packages are installed
into an environment that cannot use the NPU anyway.

### 3. `uv` is the Python environment control plane

The rework assumes that model runtime setup should happen inside `uv`, not
through ad hoc global `pip install` commands. This improves:
- reproducibility
- isolation
- lower risk of polluting the host interpreter

### 4. User confirmation is required at the environment boundary

The skill is allowed to automate Python package repair, but not to silently
choose a `uv` environment when multiple plausible environments exist.

This was intentionally kept interactive because:
- the wrong environment is a common source of confusion
- silent selection would create hard-to-debug state divergence

### 5. Reporting contract matters

The skill now explicitly points to the standard output layout and report files.
This matters because later automation or orchestration layers need stable
artifacts, not just console prose.

## What Was Intentionally Not Changed

These items were deliberately left out of scope:

1. Remote SSH support
2. Nvidia/GPU setup support
3. System-level auto-install for driver or CANN
4. Other skills' docs or workflows
5. Repository-wide skill schema updates unrelated to `setup-agent`

This trace is intentionally scoped to `setup-agent` and the root routing entry
needed for `setup-agent` to be discoverable.

## Known Follow-Up Opportunities

These were identified but not implemented in this rework:

1. Add a second reference focused on command recipes, so the main reference can
   stay more decision-oriented.
2. Add richer test coverage around reference structure, for example enforcing
   that `Quick Use`, `Detection Hints`, and `Repair Policy` remain present.
3. Add scripted helpers in the future if the skill evolves from prompt-driven
   workflow to a more tool-backed workflow.
4. Improve version matrices over time as the official compatibility data changes.

## Validation Performed

The rework was validated with:

```bash
pytest -q skills/setup-agent/tests
```

Result at completion:
- `14 passed`

## Practical Guidance For Future Editors

When updating `setup-agent` later, keep these boundaries unless there is a
deliberate redesign:

1. Keep `SKILL.md` compact and execution-oriented.
2. Move lookup-heavy detail into `references/`.
3. Do not reintroduce GPU scope into this skill.
4. Do not allow system-layer auto-install unless the risk model changes
   explicitly.
5. Preserve `uv` as the environment selection boundary.
6. If adding new behavior, add tests that encode the workflow rule, not just
   file existence.

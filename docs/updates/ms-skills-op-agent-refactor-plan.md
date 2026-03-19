# ms-skills op-agent Refactor Plan

## Goal

Refactor the operator-domain skill family into a stable and orthogonal taxonomy. To prevent architectural split-brain, this plan explicitly supersedes the legacy `docs/updates/ms-skills-op-agent-plan.md`.

This refactor plan is based on the repositioning defined in
`docs/updates/重新定位.md`.

The target outcome is:

- one navigator skill: `op-agent`
- one orthogonal 2x3 builder matrix
- stable naming based on backend + integration type
- explicit placeholder support for unimplemented matrix cells
- no loss of current implementation capability during migration

## Scope

This plan covers:

- target taxonomy
- naming rules
- phase-1 implementation coverage
- legacy mapping
- migration sequencing

This plan does not require:

- immediate implementation of all matrix cells
- removal of all legacy skills in one step

## Core Positioning

The operator-domain architecture is split into two layers:

### Layer 1: Navigator

- `op-agent`

`op-agent` is the router / navigator. It receives upstream operator-gap
handoff, determines the target backend and preferred integration path, and
routes to exactly one builder.

`op-agent` does not:

- implement kernels
- own a backend-specific development flow
- define the entire delivery process
- expose builder-internal shared analysis capability at the navigator layer

### Layer 2: Atomic Builders

Builders provide atomic implementation capability for one specific backend and
one specific integration type.

Their job is to answer:

- how to implement the operator on this backend
- under this integration paradigm

Builders may consume shared internal capability when common code-mapping or
path-analysis support is needed.

## Shared Internal Capability

The existing helper-style capabilities should not remain exposed as separate
navigator-layer skills.

Instead:

- `api-helper`
- `mint-aclnn-precheck`

should be merged into one shared internal capability skill.

This shared capability is intended to:

- support common MindSpore API / Primitive / mapping understanding
- support common operator-path and sink-path inspection
- be reused by builders that need the same class of analysis support

This shared capability should not:

- be exposed as a navigator-layer skill
- compete with `op-agent`
- become a top-level routing entry

In other words:

- navigator explains the shelf and support options
- builders own implementation paths
- the shared capability provides common internal analysis support behind them

## The Orthogonal Integration Matrix

The target taxonomy is a strict 2x3 matrix:

| Integration Type | CPU | GPU | NPU |
| --- | --- | --- | --- |
| Native | `cpu-native-builder` | `gpu-native-builder` | `npu-native-builder` |
| Plugin | `cpu-plugin-builder` | `gpu-plugin-builder` | `npu-plugin-builder` |

Definitions:

- `Native`: implementation integrated directly into the MindSpore codebase
- `Plugin`: implementation delegated through an external integration path or external specialized library

Important:

- this matrix is the **target taxonomy**
- not every cell must be implemented in phase 1
- unimplemented cells may remain as explicit placeholders

## Naming Rules

All builder skills must follow:

`{backend}-{integration_type}-builder`

Allowed values:

- `backend`: `cpu`, `gpu`, `npu`
- `integration_type`: `native`, `plugin`

Rationale:

- keep the taxonomy orthogonal
- keep names stable as implementation details evolve
- avoid letting concrete technologies such as ACLNN, ATen, or cuDNN define the top-level architecture

## Target Taxonomy

### Navigator

- `op-agent`

### Atomic Builders

- `cpu-native-builder`
- `cpu-plugin-builder`
- `gpu-native-builder`
- `gpu-plugin-builder`
- `npu-native-builder`
- `npu-plugin-builder`

## Phase-1 Coverage

Phase 1 allows a complete taxonomy with incomplete implementation coverage.

Recommended phase-1 status:

- `cpu-native-builder`
  - current scope: implemented / real capability

- `cpu-plugin-builder`
  - current scope: implemented / real capability

- `gpu-native-builder`
  - current scope: migrate current `gpu-builder`

- `gpu-plugin-builder`
  - current scope: placeholder

- `npu-native-builder`
  - current scope: **ACLNN-only in phase 1**

- `npu-plugin-builder`
  - current scope: placeholder

This means:

- the taxonomy is broader than the current implementation surface
- the scope of each builder must be stated explicitly
- placeholders are allowed as long as they are clearly marked

## ACLNN Positioning

ACLNN should not remain a top-level taxonomy name.

In this refactor:

- `npu-native-builder` is the current phase-1 builder that carries ACLNN capability
- `npu-plugin-builder` remains a reserved taxonomy slot for future plugin-style NPU paths
- future NPU plugin paths can be added later without changing the taxonomy name

This gives the architecture a stable name while preserving the current ACLNN
capability.

## Legacy Mapping

The following migration mapping should be used:

- `cpu-native-builder` -> keep
- `cpu-plugin-builder` -> keep
- `gpu-builder` -> migrate to `gpu-native-builder`
- `mindspore-aclnn-operator-devflow` -> migrate to `npu-native-builder`
- `aclnn-builder` -> migrate to `npu-native-builder`
- `api-helper` + `mint-aclnn-precheck` -> merge into one shared internal capability skill

Placeholder cells:

- `gpu-plugin-builder`
- `npu-plugin-builder`

Legacy names should remain only as migration artifacts and should not define the
target taxonomy.

## Builder Boundaries

Even after the taxonomy refactor, builders remain implementation-path skills.

Builders should:

- own backend-specific implementation work
- own backend-path-specific validation
- own code-level execution guidance
- consume shared internal capability when common mapping analysis is needed

Builders should not:

- become high-level routers
- redefine the global taxonomy
- absorb the whole delivery process by default

## Refactor Steps

### Step 1: Freeze the target taxonomy

Approve the 2x3 matrix and the naming convention:

- `cpu-native-builder`
- `cpu-plugin-builder`
- `gpu-native-builder`
- `gpu-plugin-builder`
- `npu-native-builder`
- `npu-plugin-builder`

### Step 2: Freeze phase-1 scope labels

Mark each matrix cell as one of:

- implemented
- migrating
- placeholder

Phase-1 expected state:

- implemented: `cpu-native-builder`, `cpu-plugin-builder`
- migrating: `gpu-native-builder`, `npu-native-builder`
- placeholder: `gpu-plugin-builder`, `npu-plugin-builder`

### Step 3: Apply legacy mapping

Move current skill meaning into the new taxonomy:

- `gpu-builder` -> `gpu-native-builder`
- `mindspore-aclnn-operator-devflow` -> `npu-native-builder`

### Step 4: Update capability descriptions

For each builder, rewrite `Purpose`, `Recommended use`, and `Boundary` so they
match the new taxonomy name and current scope.

This is especially important for:

- `gpu-native-builder`
- `npu-native-builder`

At the same time, define the shared internal capability boundary so that:

- it is available for builder reuse
- it is not exposed as part of the navigator interface

### Step 5: Add placeholder declarations

Create explicit placeholder status for:

- `gpu-plugin-builder`
- `npu-plugin-builder`

These placeholders should state that the taxonomy slot exists, but the
implementation scope is not yet active in phase 1.

### Step 6: Consolidate helper-style legacy skills

Merge:

- `api-helper`
- `mint-aclnn-precheck`

into one shared internal capability skill.

This step must ensure:

- the capability remains reusable
- it is positioned behind builders, not at the navigator surface
- it does not reappear as a separate top-level routing/discovery skill

### Step 7: Validate the taxonomy contract

After the refactor, validate:

- naming consistency
- legacy mapping clarity
- current-scope accuracy
- contract compliance for all top-level skills
- internal shared-capability positioning

## Risks

### Risk 1: The taxonomy becomes broader than current capability

Mitigation:

- clearly mark placeholders
- clearly state current scope per builder

### Risk 2: `npu-plugin-builder` may be mistaken as already implemented

Mitigation:

- explicitly state that `npu-plugin-builder` is still a placeholder in phase 1
- explicitly state that current ACLNN capability lives under `npu-native-builder`

### Risk 3: Builders drift back into mixed roles

Mitigation:

- keep `op-agent` as the only navigator
- keep builders scoped to implementation paths

### Risk 4: Helper-style legacy skills reappear at the wrong layer

Mitigation:

- explicitly merge them into a shared internal capability
- do not expose them as navigator-layer skills
- keep their role limited to common internal analysis support

## Validation

The refactor should be considered successful when:

- the taxonomy is fully defined as a 2x3 matrix
- the implemented / migrating / placeholder status of each cell is explicit
- legacy names no longer define the architecture
- current ACLNN capability is preserved under `npu-native-builder`
- no existing implemented capability is lost during renaming
- helper-style legacy capability is preserved but moved behind the navigator layer

## Summary

This refactor plan intentionally prioritizes architectural symmetry over
current implementation completeness.

The target design is:

- one navigator: `op-agent`
- one orthogonal builder matrix
- explicit placeholder support
- stable taxonomy names that outlive current technical details

In phase 1, the most important result is not that every matrix cell is
implemented, but that the operator skill family now has a stable and scalable
architecture.

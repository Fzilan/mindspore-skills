# Shared API Helper Wrapper + Reference Proposal

## Goal

Refactor the legacy `api-helper` and `mint-aclnn-precheck` skills into one
shared internal capability that combines:

- one strict internal skill wrapper: `api-helper`
- one shared reference knowledge base under `_shared`

This proposal explicitly requires:

- no capability shrink during refactor
- stable naming
- explicit `_shared` directory structure
- clear separation between workflow enforcement and reference material

## Decision

The target design is:

- canonical capability name: `api-helper`
- packaging model:
  - one internal shared skill wrapper
  - one shared reference bundle
- primary consumers: builders
- optional consumer: `op-agent`
- legacy special case: `mint-aclnn-precheck` becomes the `ascend` lens inside
  `api-helper`

This means:

- `api-helper` remains a real skill-shaped capability
- its strict workflow lives in `skills/api-helper/SKILL.md`
- its fact-heavy knowledge lives in `skills/_shared/api-knowledge/`
- it is not a public top-level routing surface

## Non-Shrink Principle

This refactor must not reduce current useful capability.

The merged `api-helper` must preserve all meaningful content currently carried
by:

- `api-helper`
- `mint-aclnn-precheck`

That includes:

- MindSpore API entry resolution
- internal function / `api_def` / `op_yaml` / Primitive mapping
- overloaded-branch handling
- deprecated-branch filtering
- backward registration lookup
- backward operator inventory
- Ascend static dispatch evidence
- `auto_generate` vs `customize`
- `kbk`
- `pyboost`

The refactor may change packaging and naming boundaries, but it must not narrow
the actual analysis surface.

## Why This Design

Using only shared references is too weak: it keeps facts, but it does not
enforce one strict workflow or one stable output contract.

Using only a standalone helper skill is also not ideal: it tends to absorb too
much factual content into one large prompt surface and creates more public-skill
confusion.

The hybrid design is stronger:

- `reference/` stores long-lived facts and localized rules
- `SKILL.md` stores strict workflow, stop conditions, and output requirements
- builders reuse one common wrapper instead of copying the same helper flow
- context stays smaller because consumers can read only the needed reference
  files

For the `ms-cli` / `ms-skills` repo, this is the most natural shape:

- internal capability remains explicit
- public taxonomy stays clean
- workflow discipline stays centralized
- reference material stays modular

## Positioning

`api-helper` is a shared internal capability behind the operator family.

It is not:

- a public routing entry
- a builder
- a backend-specific delivery flow

It is:

- a reusable API-level analysis capability
- a strict internal workflow wrapper
- a shared dependency for multiple builders

The public operator architecture remains:

- `op-agent`
- `cpu-native-builder`
- `cpu-plugin-builder`
- `gpu-native-builder`
- `gpu-plugin-builder`
- `npu-native-builder`
- `npu-plugin-builder`

## Naming

### Canonical Capability Name

- `api-helper`

This is the only canonical name for the shared capability after refactor.

### Legacy Names

- `mint-aclnn-precheck`

After refactor, this name should remain only as migration history and source
material. It should not remain as an independent capability surface.

### Lens Names

Backend-specific static evidence should use:

- `backend-lens-ascend.md`
- `backend-lens-cpu.md`
- `backend-lens-gpu.md`

Phase 1 only requires a real `ascend` lens.

### Core Reference Names

Generic references should use:

- `api-identity.md`
- `bprop-inventory.md`

These names should stay stable and backend-neutral.

## Primary Consumers

Primary consumers:

- `cpu-native-builder`
- `cpu-plugin-builder`
- `gpu-native-builder`
- `gpu-plugin-builder`
- `npu-native-builder`
- `npu-plugin-builder`

Optional consumer:

- `op-agent`

Important:

- builders are the primary consumers
- `op-agent` may consume the same wrapper when routing needs API-level evidence
- the `ascend` lens is primarily for NPU paths, but may also be used by
  `op-agent`

## Capability Boundary

`api-helper` should do:

- resolve public API entrypoints
- resolve internal function / `api_def` / `op_yaml` / Primitive mapping
- inventory overloaded branches and filter deprecated branches
- inspect bprop registration and backward operator usage
- collect backend-specific static evidence through backend lenses
- enforce one standard workflow for API-level evidence gathering
- enforce one standard output schema

`api-helper` should not:

- decide final routing by itself
- implement kernels
- replace builder-specific implementation reconnaissance
- own backend-specific delivery flows
- appear as a public top-level discovery skill

## Wrapper vs Reference Split

### What Lives in `SKILL.md`

The internal `api-helper` wrapper should contain:

- input contract
- execution order
- which reference files to read under which conditions
- stop conditions
- required checks
- required output schema
- explicit non-goals

In short:

- workflow and discipline live in the wrapper

### What Lives in `reference/`

The reference files should contain:

- source-of-truth paths
- mapping rules
- naming rules
- backend-specific facts
- common examples
- local checklists tied to one subproblem

In short:

- factual knowledge lives in references

### Design Rule

Do not move all strict workflow rules into references.

References may contain local correctness rules, but the global execution flow
must remain centralized in the `api-helper` wrapper.

## Core + Lenses Model

The shared capability should be physically split into generic cores and
backend-specific lenses.

### Core A: API Identity

File:

- `skills/_shared/api-knowledge/api-identity.md`

Purpose:

- resolve public API name
- resolve entry kind such as `mint`, `tensor`, `ops.function`,
  `ops.auto_generate`
- resolve internal function name
- resolve `api_def`
- resolve non-deprecated `op_yaml` branches
- resolve Primitive names for each branch

Used by:

- all builders
- optionally `op-agent`

### Core B: Backward Inventory

File:

- `skills/_shared/api-knowledge/bprop-inventory.md`

Purpose:

- search `REG_BPROP_BUILDER("<primitive>")`
- determine whether backward is defined
- distinguish dedicated grad op vs inline computation
- list backward operator calls such as `Emit("XxxGrad")` or `ib->Xxx(...)`

Used by:

- all builders
- optionally `op-agent`

### Lens: Ascend Static Evidence

File:

- `skills/_shared/api-knowledge/backend-lens-ascend.md`

Purpose:

- read `dispatch.enable`
- distinguish `auto_generate` vs `customize`
- report `kbk`
- report `pyboost`
- preserve the useful static inventory logic from `mint-aclnn-precheck`

Used by:

- primarily NPU builders
- optionally `op-agent`

### Lens: CPU / GPU

Phase 1 does not require real CPU or GPU lens files if they do not yet contain
meaningful static dispatch logic.

That means:

- CPU lens: placeholder / tbd
- GPU lens: placeholder / tbd

The architecture still reserves the lens concept even if only `ascend` exists
physically in phase 1.

## `_shared` Layout

Recommended repository structure:

```text
skills/
├── api-helper/
│   ├── SKILL.md
│   └── skill.yaml
├── op-agent/
├── cpu-native-builder/
├── cpu-plugin-builder/
├── gpu-native-builder/
├── gpu-plugin-builder/
├── npu-native-builder/
├── npu-plugin-builder/
└── _shared/
    └── api-knowledge/
        ├── api-identity.md
        ├── bprop-inventory.md
        └── backend-lens-ascend.md
```

Phase-1 structure rules:

- `skills/api-helper/` is the canonical wrapper home
- `skills/_shared/api-knowledge/` is the canonical shared knowledge home
- `skills/api-helper/SKILL.md` is required
- `skills/api-helper/skill.yaml` is recommended when the wrapper should be
  loaded as a first-class skill
- do not duplicate the same knowledge under top-level legacy helper directories

## Skill Wrapper Packaging

The wrapper should be packaged as an internal shared skill, not as a public
operator-entry skill.

Recommended phase-1 rule:

- place the wrapper under `skills/api-helper/`
- place shared knowledge under `skills/_shared/api-knowledge/`

Manifest rule:

- use `skills/api-helper/skill.yaml` when the wrapper should be loadable as a
  skill
- keep `_shared/api-knowledge/` as knowledge-only content, not a skill surface

The key requirement is the role boundary, not whether phase 1 immediately adds a
manifest file.

## Consumption Model

Builders should consume `api-helper` as a shared internal workflow wrapper.

That means builders should say, in effect:

- first load or read `skills/api-helper/SKILL.md`
- then follow the wrapper's instructions
- then continue builder-specific implementation work

Example for `cpu-plugin-builder`:

```text
Step 1: Run shared API helper flow
Load: skills/api-helper/SKILL.md
Use:
- skills/_shared/api-knowledge/api-identity.md
- skills/_shared/api-knowledge/bprop-inventory.md
Do not load:
- skills/_shared/api-knowledge/backend-lens-ascend.md
```

Example for `npu-native-builder`:

```text
Step 1: Run shared API helper flow
Load: skills/api-helper/SKILL.md
Use:
- skills/_shared/api-knowledge/api-identity.md
- skills/_shared/api-knowledge/bprop-inventory.md
- skills/_shared/api-knowledge/backend-lens-ascend.md
```

`op-agent` may also use the same wrapper when routing needs evidence, but it
must not become the exclusive owner of the helper.

## Input Contract

The wrapper should use one small stable contract:

- `api`: public API such as `mindspore.mint.add`
- `question_scope`: one of `identity`, `bprop`, `inventory`
- `backend_lens`: optional, one of `ascend`, `cpu`, `gpu`

Examples:

- `api=mindspore.mint.acos`, `question_scope=identity`
- `api=mindspore.mint.acos`, `question_scope=bprop`
- `api=mindspore.mint.add`, `question_scope=inventory`,
  `backend_lens=ascend`

## Required Wrapper Workflow

The `api-helper` wrapper should enforce a strict flow:

1. determine which scopes are needed: `identity`, `bprop`, optional lens
2. read the minimum required reference files
3. resolve API identity first
4. resolve backward inventory second when requested
5. resolve backend lens evidence last when requested
6. stop immediately when entry resolution fails
7. output the normalized schema only

The wrapper must also enforce:

- no speculative branch inference without source evidence
- no backend-lens expansion when the requested backend lens is absent
- no routing decision
- no implementation advice beyond API-level evidence gathering

## Standardized Output Schema

The wrapper should require all consumers to output collected evidence in one
normalized shape before starting implementation work.

Recommended schema:

```text
api: mindspore.mint.add
entry_kind: mint
entry_source: mindspore.ops.functional_overload
api_def: add.yaml
branches:
- op_yaml: add_scalar_op.yaml
  primitive: AddScalar
  deprecated: no
  backward_defined: yes
  backward_ops: Real, OutZeros
  backend_evidence:
    ascend:
      dispatch: customize
      kbk: yes
      pyboost: yes
- op_yaml: add_ext_op.yaml
  primitive: AddExt
  deprecated: no
  backward_defined: yes
  backward_ops: Muls, Cast, OutZeros
  backend_evidence:
    ascend:
      dispatch: auto_generate
      kbk: yes
      pyboost: yes
```

Rules:

- generic fields stay backend-neutral
- backend-specific data lives under `backend_evidence`
- missing backend lenses are allowed
- placeholder backend lenses may return `tbd`
- builders should not invent per-builder output formats

## Migration Mapping

Map existing material as follows:

- `skills/api-helper/SKILL.md`
  - rewrite as the strict wrapper over shared knowledge
- `skills/api-helper/reference/mindspore_api_call_chain.md`
  - migrate into `skills/_shared/api-knowledge/api-identity.md` and
    `skills/_shared/api-knowledge/bprop-inventory.md`
- `skills/mint-aclnn-precheck/SKILL.md`
  - retire as an independent surface
- `skills/mint-aclnn-precheck/reference/mint_to_aclnn_precheck_guide.md`
  - migrate across `skills/_shared/api-knowledge/api-identity.md`,
    `skills/_shared/api-knowledge/bprop-inventory.md`, and
    `skills/_shared/api-knowledge/backend-lens-ascend.md`

Legacy names:

- `api-helper`
  - kept as canonical capability name
- `mint-aclnn-precheck`
  - retired as separate capability name
  - preserved only as migration history and source material

## Phase-1 Scope

Phase-1 expected state:

- `api-helper` internal wrapper: implemented
- API Identity core: implemented
- Backward Inventory core: implemented
- `ascend` lens: implemented
- CPU lens: placeholder / tbd
- GPU lens: placeholder / tbd

## Refactor Steps

### Step 1: Freeze capability name and internal packaging

Approve:

- canonical name: `api-helper`
- wrapper location: `skills/api-helper/`
- shared knowledge location: `skills/_shared/api-knowledge/`
- model: wrapper + references
- non-role: public top-level routing skill

### Step 2: Create the internal wrapper

Create:

- `skills/api-helper/SKILL.md`
- `skills/api-helper/skill.yaml`

This file must centralize:

- workflow
- stop conditions
- reference-loading rules
- output schema requirements

### Step 3: Split generic knowledge into core references

Create:

- `skills/_shared/api-knowledge/api-identity.md`
- `skills/_shared/api-knowledge/bprop-inventory.md`

### Step 4: Split `mint-aclnn-precheck` into the `ascend` lens

Create:

- `skills/_shared/api-knowledge/backend-lens-ascend.md`

Move into it:

- `dispatch.enable`
- `auto_generate` vs `customize`
- `kbk`
- `pyboost`

### Step 5: Update builders to consume the wrapper

Each builder should explicitly state:

- that it first loads `skills/api-helper/SKILL.md`
- which reference files are needed for that builder path
- what evidence it must produce before implementation

### Step 6: Remove legacy helper surfaces

After migration:

- `mint-aclnn-precheck` should no longer exist as a separate public skill
- top-level legacy `api-helper` helper behavior should be retired
- shared knowledge should live canonically under `_shared/api-knowledge/`
- the wrapper should live canonically under `skills/api-helper/`

## Validation

The refactor is successful when:

- there is one canonical shared capability name: `api-helper`
- the capability surface is not narrower than the combined legacy helpers
- strict workflow is centralized in the wrapper
- factual knowledge is split into modular references
- builders consume one common API-evidence workflow
- the `ascend` inventory remains available without defining the helper as
  NPU-only
- CPU and GPU builders reuse the same generic API identity and backward
  inventory
- `op-agent` can reuse the same helper without owning it
- public taxonomy remains clean

## Summary

The right final shape for this repo is:

- `api-helper` as the canonical shared capability name
- `skills/api-helper/` as the wrapper home
- `skills/_shared/api-knowledge/` as the shared knowledge home
- one internal wrapper skill for strict flow
- modular references for long-lived factual knowledge
- `mint-aclnn-precheck` absorbed into the `ascend` lens
- no capability shrink during migration

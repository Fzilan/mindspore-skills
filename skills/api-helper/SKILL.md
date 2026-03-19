---
name: api-helper
description: Auto-invoked when users ask mindspore api questions. such as mint.*, tensor.*, forward, backward, cpu/gpu/npu.
---

# API Helper

This skill is the API-analysis reference flow for MindSpore operator questions.
It helps answer API identity, forward/backward mapping, and call-chain
questions by reading the shared knowledge under `skills/_shared/api-knowledge/`.

## When to Use

Use this skill when:
- Questions about mint.*, or tensor.* operators. 
- Questions about forward/backward operator/API
- Questions about API call chains

## Workflow

### Step 1: Resolve API Identity

Must read: `skills/_shared/api-knowledge/api-identity.md`

resolve:

- whether the public API entry exists
- export source and internal symbol
- `api_def`, if any
- active non-deprecated branches
- branch `op_yaml`
- branch Primitive

### Step 2: Resolve Backward Inventory For Each Active op Branch

Must read: `skills/_shared/api-knowledge/bprop-inventory.md`

resolve:

- whether bprop is defined
- which backward operators appear in the registered body

### Step 3: Resolve Backend Lens When Needed

If users have questions on Ascend static path facts, read: `skills/_shared/api-knowledge/backend-lens-ascend.md`

it help resolve:
- whether static Ascend path（aclnn backend） evidence is visible
- whether `kbk` / `pyboost` evidence is visible


### Step 4: Display Answer

- Do not collapse multiple active branches into one summary branch.
- Keep backward and backend details attached to the branch they belong to.
- Follow the shared report contract; do not invent per-builder output formats.
- Briefly state what was checked when needed, but do not turn the answer into an
  evidence dump.

## Rules

- If API identity cannot be resolved, stop there.
- Do not guess missing Primitive or branch facts.
- Do not turn missing source facts into positive support claims.
- Do not perform implementation work.
- Do not mix runtime observations into this static report unless explicitly
  requested.

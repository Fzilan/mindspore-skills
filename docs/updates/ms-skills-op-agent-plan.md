# ms-skills op-agent Plan

## Goal

Define a stricter operator-domain skill architecture under the constraints of
`docs/updates/ms-skills-update-plan.md`.

The goals are:

- `op-agent` is the only high-level entrypoint
- builders own implementation paths only
- phase 1 stays prompt-first and manual-first
- phase 1 does not introduce a separate discovery skill or implicit helper tooling

## Alignment With ms-skills-update-plan

This plan stays aligned with the parent update plan in four ways:

1. `op-agent` remains the diagnosis / routing / strategy layer
2. implementation-oriented skills remain below it
3. phase 1 still uses `SKILL.md` + `skill.yaml` + `tests/`
4. phase 1 does not depend on a shared helper-tool runtime

This plan also adds one stricter operator-domain rule:

- discovery is an internal capability of `op-agent`, not a separate top-level skill

## Structure

```text
skills/
├── op-agent/                  # discovery + routing single entrypoint
├── cpu-plugin-builder/        # CPU plugin implementation
├── cpu-native-builder/        # CPU native implementation
├── gpu-builder/               # GPU implementation
└── aclnn-builder/             # Ascend ACLNN implementation
```

## Layering Model

### Layer 1: Routing + Discovery

- `op-agent`

`op-agent` is the only high-level entry for operator-gap problems.
It performs two functions internally:

- minimal discovery
- routing decisions

### Layer 2: Implementation

- `cpu-plugin-builder`
- `cpu-native-builder`
- `gpu-builder`
- `aclnn-builder`

These skills implement concrete backend paths. They do not own high-level
discovery or routing.

## Naming Rules

Only keep two naming categories in the target taxonomy:

- `*-agent`: high-level diagnosis, routing, strategy
- `*-builder`: concrete implementation path

Do not keep the following as target taxonomy names:

- `*-helper`
- `*-precheck`
- `*-inventory`
- `*-devflow`

These names may only appear as:

- legacy names
- reference file names
- migration notes

## Skill Specs

### op-agent

**Purpose**

Drive missing-operator analysis and route to the right implementation
workflow.

**Recommended use**

- missing operator
- unsupported backend kernel
- operator implementation gap
- user does not know which implementation path to choose

**SKILL.md guidance**

The skill should instruct the agent to:

1. identify the missing operator and backend/platform gap
2. inspect Factory `operator` knowledge if available
3. perform minimal discovery inside the same skill
4. choose one implementation path
5. delegate to one builder skill where possible
6. summarize implementation and validation next steps

**Discovery Checklist**

The internal discovery phase of `op-agent` should only perform the minimum
necessary checks, typically including:

- API entrypoint / Primitive
- `op_def` / `api_def` mapping
- current backend support signals
- `dispatch` / `kbk` / `pyboost` / `bprop` in Ascend-related cases
- sink-path information in mint-related cases

These checks are prompt-guided manual inspection. They must not assume a
separate script, scanner, or shared helper tool in phase 1.

**Boundary**

- owns discovery + routing
- does not load a second top-level discovery skill
- does not expand into backend-specific implementation work
- does not assume stable automated static-analysis tooling in phase 1

### cpu-plugin-builder

**Purpose**

Implement CPU operators through ATen/libtorch in `mindspore_op_plugin`.

**Recommended use**

- CPU implementation is required
- ATen or `mindspore_op_plugin` is the selected path
- routing has already been decided

**Boundary**

- implementation only
- no native CPU path
- no GPU or Ascend path
- no cross-backend routing

### cpu-native-builder

**Purpose**

Implement native CPU kernels directly in MindSpore.

**Recommended use**

- CPU implementation is required
- native kernel is the selected path
- routing has already been decided

**Boundary**

- implementation only
- no ATen/plugin path
- no GPU or Ascend path
- no cross-backend routing

### gpu-builder

**Purpose**

Implement GPU operators through CUDA or GPU-side integration paths.

**Recommended use**

- GPU backend support is missing
- the GPU implementation path has been selected
- routing has already been decided

**Boundary**

- implementation only
- no CPU or Ascend path
- no cross-backend routing

### aclnn-builder

**Purpose**

Implement ACLNN-based Ascend operator adaptation as the selected implementation
path.

**Recommended use**

- Ascend backend support is missing
- ACLNN is the selected path
- work includes YAML, GeneralInfer, PyBoost, KBK, bprop, export, or tests

**Boundary**

- implementation only
- no global routing role
- no global discovery role
- no default ownership of RFC / feature-delivery / transfer-to-test workflows

## Builder Input Contract

Before handing work to a builder, `op-agent` should try to establish at least:

- `op_name`
- target backend
- selected implementation path
- forward / backward scope
- reference implementation or source clue

For `aclnn-builder`, it should ideally also establish:

- target `aclnnXxx`
- path-internal evidence for `auto-generate` vs `customize`
- dtype / layout / shape constraints
- dynamic-shape / dynamic-rank expectations

If these prerequisites are clearly missing, the builder may request more
information, but it should not collapse back into a high-level routing role.

## Builder Core Scope

The core scope of a builder is code implementation and code validation.

For `aclnn-builder`, the core scope includes:

- YAML
- codegen
- GeneralInfer
- PyBoost
- KBK
- bprop
- export
- tests

The following should not define the builder itself:

- feature-document workflow
- RFC / PR workflow
- transfer-to-test workflow
- generic discovery / call-chain inventory

If these are retained, they should be downgraded to references or checklists,
not kept as the builder's default main flow.

## Path-Internal Decisions

The plan must explicitly distinguish:

- global routing decisions
- path-internal implementation decisions

Specifically:

- `op-agent` owns the global routing decision  
  Example: CPU vs GPU vs ACLNN
- `aclnn-builder` owns only ACLNN-internal decisions  
  Example: `auto-generate` vs `customize`

A builder must not take global path selection back from `op-agent`.

## Builder Exit Criteria

When a builder finishes, it should at least provide:

- the implementation path used
- the key code change locations
- the core validation method and result
- the test coverage status
- the known residual risks

## Routing Contract

`op-agent` should follow this contract:

1. determine whether the request is an operator-gap problem
2. perform minimal discovery inside the same skill
3. choose one implementation path when possible
4. hand off to one builder skill
5. summarize the selected path, the reason, and the next validation steps

Default routing examples:

- CPU + ATen/op_plugin path -> `cpu-plugin-builder`
- CPU + native kernel path -> `cpu-native-builder`
- GPU path -> `gpu-builder`
- Ascend + ACLNN path -> `aclnn-builder`

`op-agent` must not load a separate top-level discovery skill in the same task.

## Legacy Mapping

Current non-target names should be handled as follows:

- `api-helper` -> merge into `op-agent` internal discovery references
- `mint-aclnn-precheck` -> merge into `op-agent` internal discovery references
- `mindspore-aclnn-operator-devflow` -> migrate to `aclnn-builder`
- `npu-builder` -> remove from the target taxonomy

These legacy names exist only for migration and should not define the target
architecture.

## Scope Discipline

Phase 1 should not add the following as top-level skills:

- discovery helper
- mint-only precheck skill
- backend-specific inventory skill
- tooling wrapper without stable runtime support

If phase-1 capability needs to grow, prefer:

- expanding the internal discovery checklist of `op-agent`
- tightening builder boundaries and builder input contracts
- moving lessons learned into references or checklists

Do not promote a sub-step into a top-level skill just because the sub-step
exists.

## Packaging Requirements

Each top-level skill in this plan must still satisfy the repository contract:

- `SKILL.md`
- `skill.yaml`
- `tests/`

Phase 1 still uses:

- `skill.yaml.entry.type: manual`
- `skill.yaml.entry.path: SKILL.md`

## Validation

After the restructuring:

```bash
python tools/check_consistency.py
pytest tests/contract
```

Priority invoke-ratio / step-compliance test targets:

- `op-agent`
- `aclnn-builder`

## Summary

The second-version operator skill design is:

- one high-level entrypoint: `op-agent`
- multiple implementation-path skills: builders

Discovery still exists, but it is strictly folded back into `op-agent`.
This is the cleanest way to satisfy all of the following at once:

- the prompt-first / manual-first constraints from the update plan
- the single-entry interaction model
- the boundary that builders are implementation-path skills

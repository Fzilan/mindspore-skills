# ms-skills op-agent Plan

## Goal

Refine the operator-domain skill design under the direction of
`docs/updates/ms-skills-update-plan.md`.

This document is intentionally stricter than the current repository state:

- design from the target role of `op-agent`
- keep the same prompt-first and manual-first principles
- describe skills using the same style as the update plan
- use clean target names instead of legacy accidental names

## Alignment With ms-skills-update-plan

This document stays aligned with the parent update plan in four ways:

1. `op-agent` remains a high-level diagnosis / routing / strategy skill
2. implementation-oriented skills remain below it
3. initial packaging remains `SKILL.md` + `skill.yaml` + `tests/`
4. helper tooling remains optional later work, not phase-1 scope

This document adds one supporting helper skill because the current operator
domain needs a unified evidence-collection layer. That helper is a support
skill for `op-agent`, not a peer high-level agent family.

## Target Skill Tree

The clean target tree should be:

```text
skills/
├── op-agent/
│   ├── SKILL.md
│   ├── skill.yaml
│   └── tests/
│
├── op-discovery-helper/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── reference/
│   │   ├── api-callchain.md
│   │   └── mint-aclnn-inventory.md
│   └── tests/
│
├── cpu-plugin-builder/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── reference/
│   └── tests/
│
├── cpu-native-builder/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── reference/
│   └── tests/
│
├── gpu-builder/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── reference/
│   └── tests/
│
├── aclnn-builder/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── workflows/
│   ├── templates/
│   ├── reference/
│   └── tests/
```

## Layering Model

### Layer 1: Routing

- `op-agent`

This is the high-level entry for operator-gap problems.

### Layer 2: Discovery

- `op-discovery-helper`

This is the supporting evidence-collection layer for `op-agent`.

### Layer 3: Implementation

- `cpu-plugin-builder`
- `cpu-native-builder`
- `gpu-builder`
- `aclnn-builder`

These skills are implementation workflows. They are not routing skills.

## Naming Rules

Use names that reflect layer semantics:

- `*-agent`: diagnosis, routing, strategy
- `*-helper`: evidence collection, inventory, lookup
- `*-builder`: concrete implementation workflow

Do not use target names like:

- `*-precheck`
- `*-inventory`
- `*-devflow`

unless they are references, subdocuments, or temporary migration names.

In particular:

- the clean target name is `aclnn-builder`
- `mindspore-aclnn-operator-devflow` is only a legacy migration reference
- it should not define the long-term skill taxonomy

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

1. identify the missing operator and platform gap
2. inspect the Factory `operator` card if Factory query is available
3. request discovery evidence if the current facts are incomplete
4. choose the right implementation path
5. delegate to an existing builder skill where possible
6. summarize implementation and validation next steps

**Boundary**

- owns diagnosis / routing / strategy
- does not perform full static inventory itself
- does not expand into detailed backend implementation workflow
- does not become a builder

### op-discovery-helper

**Purpose**

Provide the static evidence needed for operator routing decisions.

**Recommended use**

- API entrypoint is unclear
- Primitive mapping is unclear
- backend support status is unclear
- mint-to-ACLNN sink information is needed
- `op-agent` lacks enough evidence to select a builder path

**SKILL.md guidance**

The skill should instruct the agent to:

1. inspect API entrypoints and call-chain facts
2. inspect Primitive, `op_def`, and `api_def` mappings
3. inspect backend support signals
4. inspect Ascend dispatch mode, `kbk`, `pyboost`, `bprop`, and backward wiring when relevant
5. return only structured evidence and stop before route selection

**Boundary**

- owns static discovery only
- produces facts for `op-agent`
- does not choose the final path
- does not recommend code changes
- does not take over implementation

**Typical output**

- `api_entry`
- `primitive`
- `op_def_branches`
- `backend_support`
- `ascend_dispatch`
- `pyboost`
- `kbk`
- `bprop`
- `backward_ops`
- `deprecated_branches`
- `notes`

### cpu-plugin-builder

**Purpose**

Implement CPU operators through ATen/libtorch in `mindspore_op_plugin`.

**Recommended use**

- CPU implementation is required
- ATen or `mindspore_op_plugin` is the chosen path
- the routing decision has already been made

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
- native kernel path is preferred
- the routing decision has already been made

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
- GPU implementation path has been selected
- the routing decision has already been made

**Boundary**

- implementation only
- no CPU or Ascend path
- no cross-backend routing

### aclnn-builder

**Purpose**

Implement ACLNN-based Ascend operator adaptation end to end.

**Recommended use**

- Ascend backend support is missing
- ACLNN is the selected path
- work includes YAML, GeneralInfer, PyBoost, KBK, bprop, tests, or docs

**Boundary**

- implementation only
- no global routing role
- no generic discovery role

## Hard Boundaries

The following boundaries should be enforced across the operator skill family:

- `op-agent` owns routing
- `op-discovery-helper` owns static evidence collection
- each builder owns exactly one implementation path
- no helper may evolve into a builder
- no builder may absorb global routing

## Merge Decision: api-helper + mint-aclnn-precheck

The old split between generic API lookup and mint-to-ACLNN precheck should be
removed.

They should be merged into:

- `op-discovery-helper`

Reason:

- both are discovery-layer skills
- both exist to collect routing evidence before implementation
- splitting them by CPU-era vs ACLNN-era history creates the wrong boundary

After the merge:

- call-chain lookup becomes one discovery capability
- mint-to-ACLNN inventory becomes another discovery capability
- `op-agent` consumes one unified discovery schema

## Routing Contract

`op-agent` should follow this contract:

1. determine whether the request is an operator-gap problem
2. request evidence from `op-discovery-helper` if needed
3. choose one implementation path when possible
4. hand off to one builder skill
5. summarize the selected path, reason, and validation next steps

Default routing examples:

- CPU + ATen/op_plugin path -> `cpu-plugin-builder`
- CPU + native kernel path -> `cpu-native-builder`
- GPU path -> `gpu-builder`
- Ascend + ACLNN path -> `aclnn-builder`

`op-agent` should not load multiple full builder skills into one task unless a
single route genuinely cannot be selected.

## Scope Discipline

The following should not become new top-level operator skills in phase 1:

- mint-only precheck skills
- backend-specific inventory skills
- route-selection helper skills that duplicate `op-agent`
- tooling wrappers without stable upstream runtime support

If phase-1 capability needs to grow, prefer:

- adding instructions to `op-agent`
- adding references to `op-discovery-helper`
- tightening builder boundaries

Do not add a top-level skill only because a sub-step exists.

## Packaging Requirements

Each top-level skill in this plan should satisfy the repository contract:

- `SKILL.md`
- `skill.yaml`
- `tests/`

For the first phase:

- `skill.yaml.entry.type: manual`
- `skill.yaml.entry.path: SKILL.md`
- dependencies stay minimal and honest

## Validation

After restructuring the operator-domain skills:

```bash
python tools/check_consistency.py
pytest tests/contract
```

Each key skill should also have a small invoke-ratio / step-compliance test set,
especially:

- `op-agent`
- `op-discovery-helper`
- `aclnn-builder`

## Legacy Mapping

The clean target names above are design names. During migration, the current
repository may still contain legacy names.

Suggested mapping:

- `api-helper` + `mint-aclnn-precheck` -> `op-discovery-helper`
- `mindspore-aclnn-operator-devflow` -> `aclnn-builder`
- `npu-builder` -> remove from target taxonomy; migrate any still-useful content before deletion

Legacy names should be treated as migration artifacts, not as the target
taxonomy.

## Summary

The target operator-domain architecture is:

- one routing skill: `op-agent`
- one discovery support skill: `op-discovery-helper`
- several implementation skills: the backend builders

This keeps the operator domain aligned with the update plan while fixing the
current mixed-layer naming and boundary problems.

# ms-skills op-agent Plan

## Positioning

This document refines the `op-agent` design from
`docs/updates/ms-skills-update-plan.md` and focuses only on the operator
domain.

The core constraint is unchanged:

- `op-agent` is a high-level diagnosis and routing skill
- builder skills remain the implementation layer
- the first phase stays prompt-first and manual
- helper tools are optional later work, not a prerequisite

`op-agent` must not become another full implementation skill. Its job is to
identify the operator gap, select the correct implementation path, hand off to
the right skill, and summarize validation next steps.

## Intended Workflow

`op-agent` follows the workflow defined in the update plan:

1. identify the missing operator and backend/platform gap
2. query Factory `operator` knowledge if available
3. choose the right implementation path
4. delegate to an existing builder skill where possible
5. summarize implementation and validation next steps

## Target Skill Tree

The operator-domain skill family should be organized by layer, not by the
historical origin of each skill.

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
├── mindspore-aclnn-operator-devflow/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── workflows/
│   ├── templates/
│   ├── reference/
│   └── tests/
│
└── npu-builder/
    ├── SKILL.md
    ├── skill.yaml
    ├── reference/
    └── tests/
```

## Layering Model

### Layer 1: Routing

- `op-agent`

This is the single high-level entry for operator-gap problems.

Typical user intents:

- missing operator
- unsupported backend kernel
- operator implementation gap
- not sure which backend path to use

### Layer 2: Discovery

- `op-discovery-helper`

This is the single discovery and static-inventory helper. It replaces the split
between a generic API helper and a mint-to-ACLNN precheck helper.

This layer exists to produce structured facts for `op-agent`, not to compete
with it as another top-level operator agent.

### Layer 3: Implementation

- `cpu-plugin-builder`
- `cpu-native-builder`
- `gpu-builder`
- `mindspore-aclnn-operator-devflow`
- `npu-builder`

These skills implement a selected backend path. They assume routing is already
done.

## Naming Rules

To keep boundaries clear, names should encode layer semantics:

- `*-agent`: high-level diagnosis, routing, strategy
- `*-helper`: narrow evidence collection or inventory
- `*-builder`: concrete implementation workflow

Avoid adding more top-level names like `precheck`, `inventory`, or `devflow`
unless they clearly map to one of the three layers above.

`mindspore-aclnn-operator-devflow` is an implementation-layer skill even if its
name is legacy. In structure and behavior, it should be treated as a builder.

## Responsibilities and Boundaries

### op-agent

Responsibilities:

- recognize that the problem is an operator-gap problem
- collect the minimal facts needed for routing
- invoke `op-discovery-helper` when the current evidence is incomplete
- determine the implementation path
- hand off to the correct builder skill
- summarize implementation and validation next steps

Must do:

- state what gap was identified
- state which backend path was selected and why
- state which builder skill should take over

Must not do:

- perform full static inventory itself
- expand into detailed backend-specific implementation steps
- become a CPU/GPU/Ascend builder

### op-discovery-helper

Responsibilities:

- provide static evidence and structured inventory for operator analysis
- unify generic API call-chain lookup with mint-to-ACLNN inventory

Typical output fields:

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

Must do:

- return facts in a stable structure
- support both mint and non-mint operator entrypoints
- stop at evidence collection

Must not do:

- choose the final implementation route
- recommend code changes
- behave like a builder

### cpu-plugin-builder

Responsibilities:

- implement CPU operators through ATen/libtorch in `mindspore_op_plugin`

Must not do:

- native CPU implementation
- GPU or Ascend implementation
- cross-backend routing

### cpu-native-builder

Responsibilities:

- implement native CPU kernels directly in MindSpore

Must not do:

- ATen/plugin path work
- GPU or Ascend implementation
- cross-backend routing

### gpu-builder

Responsibilities:

- implement GPU operators through CUDA or GPU-side integration paths

Must not do:

- CPU or Ascend implementation
- cross-backend routing

### mindspore-aclnn-operator-devflow

Responsibilities:

- implement ACLNN-based Ascend operator adaptation end to end
- cover YAML, GeneralInfer, PyBoost, KBK, bprop, tests, and docs

Must not do:

- serve as the primary routing layer
- absorb generic operator discovery duties

### npu-builder

Responsibilities:

- cover Ascend/NPU implementation paths outside the ACLNN devflow when such a
  path is genuinely needed

Must not do:

- duplicate the ACLNN full-flow implementation path
- compete with `mindspore-aclnn-operator-devflow` for the same task by default

If future work shows that almost all real Ascend operator work is ACLNN-based,
`npu-builder` should be narrowed further or deprecated.

## Merge Decision: api-helper + mint-aclnn-precheck

The old split between generic API lookup and mint-to-ACLNN precheck should be
removed.

They should be merged into:

- `op-discovery-helper`

Reason:

- both are discovery-layer skills
- both exist to collect routing evidence before implementation
- splitting them by CPU-era vs ACLNN-era history creates backend-shaped
  coupling at the wrong abstraction level

After the merge:

- call-chain lookup becomes one capability of discovery
- mint-to-ACLNN inventory becomes another capability of discovery
- `op-agent` consumes one unified discovery output schema

## Routing Contract

`op-agent` should use a simple routing contract:

1. determine whether the request is an operator-gap problem
2. request structured evidence from `op-discovery-helper` if needed
3. choose exactly one implementation path when possible
4. hand off to exactly one builder skill
5. return a concise summary of selected path, why it was chosen, and what to
   validate next

Default routing examples:

- CPU + ATen/op_plugin path -> `cpu-plugin-builder`
- CPU + native kernel path -> `cpu-native-builder`
- GPU path -> `gpu-builder`
- Ascend + ACLNN adaptation path -> `mindspore-aclnn-operator-devflow`
- Ascend + non-ACLNN path -> `npu-builder`

`op-agent` should not load multiple full builder skills into one task unless
the situation genuinely cannot be resolved with a single selected path.

## Scope Discipline

The following should not become separate top-level operator skills in phase 1:

- mint-only precheck skills
- backend-specific inventory skills
- route-selection helper skills that duplicate `op-agent`
- execution/tool wrapper skills without stable runtime support

If additional capability is needed in phase 1, prefer:

- adding instructions to `op-agent`
- adding references to `op-discovery-helper`
- tightening builder boundaries

Do not add new top-level skills just because a sub-step exists.

## Packaging Requirements

Each top-level skill in this tree should satisfy the repository contract:

- `SKILL.md`
- `skill.yaml`
- `tests/`

For the first phase:

- `skill.yaml.entry.type: manual`
- `skill.yaml.entry.path: SKILL.md`
- dependencies remain minimal and honest

## Validation

After restructuring the operator-domain skills:

```bash
python tools/check_consistency.py
pytest tests/contract
```

Each skill should also have a small test set for invoke-ratio and step
compliance, especially:

- `op-agent`
- `op-discovery-helper`
- `mindspore-aclnn-operator-devflow`

## Summary

The clean target architecture is:

- one routing skill: `op-agent`
- one discovery skill: `op-discovery-helper`
- several implementation skills: the backend builders

This keeps the operator domain aligned with the update plan:

- prompt-first
- manual first
- high-level agents above specialized builders
- no premature tool sprawl
- no mixed-layer skill boundaries

# Workflow: ACLNN Precheck

## Goal

Before editing code, confirm that the resolved operator branch really needs an
ACLNN implementation, identify the implementation mode, and build a minimal
execution plan for the rest of the ACLNN lane.

This workflow absorbs the useful parts of the old ACLNN pre-check flow:

- repository inventory
- PTA/reference review
- ACLNN symbol/signature evidence
- `auto_generate` vs `customize` choice
- direct vs composite classification
- backward-needed decision

It intentionally does **not** require the old feature-document/reporting
ceremony.

## Inputs

- `resolved_api`
- `resolved_operator`
- optional PTA/reference API name when available
- current workspace

## Outputs

Produce an `AclnnExecutionPlan` with at least:

```text
AclnnExecutionPlan
- resolved_api
- resolved_operator
- backend_gap
- aclnn_symbol
- implementation_mode: auto_generate | customize
- implementation_kind: direct | composite
- backward_required: true | false
- export_required: true | false
- change_scope
- blocking_risks
```

## Rules

### Local Source Wins

When repository state and workflow text disagree, repository state wins.

### Do Not Guess

If the ACLNN symbol or signature cannot be confirmed from source, visible
headers, or user-provided docs/snippets, stop and report the missing evidence.

## Steps

### 1. Inventory the existing branch state

Search the current repository state for the resolved operator branch:

- `op_def` / `api_def` YAML
- infer implementation
- PyBoost ACLNN implementation or generated ACLNN evidence
- KBK ACLNN implementation or generated registration evidence
- BPROP registration
- export hooks

Record what already exists and what is still missing.

### 2. Review the upstream/reference implementation when available

When a PTA or other upstream reference exists:

- inspect the public API shape
- inspect backward registration when relevant
- inspect the real ACLNN invocation and argument preprocessing
- note overload/alias cases that affect the resolved operator identity

Use `templates/pta-analysis-report.md` only when a structured scratch artifact
is useful; it is optional.

### 3. Confirm ACLNN symbol and execution style

Confirm:

- the ACLNN symbol (for example `aclnnXxx`)
- whether the path is `auto_generate` or `customize`
- whether the implementation is a direct single-op call or a composite path

Suggested static evidence:

- operator YAML `dispatch` configuration
- `aclnn_config.yaml`
- customize PyBoost source
- customize KBK source
- existing ACLNN call sites

### 4. Determine backward/export requirements

Decide:

- whether backward support is required for the requested task
- whether public/internal Python exposure needs to be updated

### 5. Produce the execution plan

Summarize:

- what files/components will be touched
- what the forward implementation mode is
- whether `20-bprop.md` is required
- the main blockers or missing evidence

## Success Criteria

- the ACLNN symbol/path is confirmed from real evidence
- `auto_generate` vs `customize` is fixed
- direct vs composite classification is fixed
- backward/export requirements are fixed
- downstream workflows can run without repeating this analysis


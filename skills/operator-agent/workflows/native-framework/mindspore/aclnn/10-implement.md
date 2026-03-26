# Workflow: ACLNN Main Implementation

## Goal

Implement the forward ACLNN path for the resolved operator branch.

This workflow intentionally merges several old ACLNN-builder stages into one
execution file so that `operator-agent` can stay compact:

- YAML definition
- code generation
- GeneralInfer
- PyBoost implementation
- KBK implementation
- export hook-up

Backward/BPROP remains separated in `20-bprop.md`.

## Inputs

- `AclnnExecutionPlan`
- current repository state

## Required Sections

### 1. Operator definition and dispatch

Create or update the operator definition layer required by the resolved branch:

- `op_def` YAML
- `api_def` YAML when applicable
- doc YAML when applicable
- `dispatch` configuration for ACLNN

The YAML/dispatch outcome must match the precheck decision:

- `auto_generate`
- `customize`

### 2. Code-generation synchronization

After YAML changes:

- rerun the required generation step
- confirm generated artifacts required by the downstream implementation exist

Do not continue with stale generated files.

### 3. GeneralInfer

Implement or update:

- shape inference
- type inference
- dynamic-shape fallback behavior when required

Keep the infer responsibility boundary clean:

- infer computes shapes/types
- runtime legality remains a runtime concern

### 4. Forward runtime implementation

#### `auto_generate` path

Validate the generated ACLNN path:

- generated PyBoost call path exists
- generated KBK registration path exists
- generated call arguments/register evidence match the resolved operator branch

#### `customize` path

Implement the handwritten ACLNN runtime path:

- PyBoost customize implementation
- KBK customize kernel and registration

When the plan says the operator is `composite`, use the composite strategy
approved by precheck and do not silently downgrade it to a guessed direct ACLNN
call.

### 5. Export hook-up

When `export_required = true`, update the Python/API exposure surface required
by the resolved operator branch.

This includes the necessary interface hook-up for the resolved API surface, but
does not try to preserve the old documentation workflow.

## Must Not Do

- do not redo API/operator resolution
- do not redo backend-lane selection
- do not implement BPROP here
- do not treat documentation/testing maintenance as required for v1 execution

## Success Criteria

- the forward branch definition is complete
- generated files are synchronized
- infer is in place
- forward ACLNN runtime path exists and matches the planned implementation mode
- export changes are applied when required


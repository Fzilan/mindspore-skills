# Workflow: ACLNN BPROP

## Goal

Implement backward support for the ACLNN lane when the execution plan requires
it.

This workflow is only entered when:

- the request needs backward support, or
- the resolved branch must stay behaviorally complete for backward use

## Inputs

- `AclnnExecutionPlan`
- forward implementation result
- available backward/reference evidence when present

## Steps

### 1. Confirm whether BPROP is actually required

If `backward_required = false`, stop and record that no BPROP work is needed.

### 2. Choose the backward strategy

Use real source evidence to decide whether the backward path should be:

- a dedicated grad operator path
- an inline primitive-composition path
- another explicit project-local pattern already used by the repository

Do not invent a backward strategy without evidence.

### 3. Implement/update the BPROP registration

Update the correct BPROP source location for the resolved operator branch.

Focus on:

- differentiable inputs
- returned gradients per forward input
- zero/unused-input handling where applicable

### 4. Keep dynamic/runtime edge cases aligned with the repository

If the backward path depends on dynamic input shape/value behavior, follow the
repository's actual BPROP conventions instead of relying on stale text alone.

## Must Not Do

- do not redo forward implementation
- do not redo lane selection
- do not turn this into the final verification step

## Success Criteria

- backward requirement is resolved explicitly
- the chosen BPROP strategy matches real source evidence
- the target operator branch has the required backward registration/update


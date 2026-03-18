---
name: mint-aclnn-precheck
description: Static pre-check and inventory for a `mindspore.mint.*` API's ACLNN sink path. Use when the user wants to determine whether a mint API exists, which non-deprecated `api_def`/`op_yaml` branches it maps to, which Primitive each branch uses, whether it enters the Ascend dispatch path (`auto_generate`, `customize`, or unsupported), whether `kbk` and `pyboost` are present, and whether a bprop definition and `backward_ops` exist.
---

# Mint-to-ACLNN Precheck

This skill performs a static pre-check for a `mindspore.mint.*` API and reports its mint-to-ACLNN inventory fields.

## When to Use

Use this skill when:
- The user wants to check whether a `mindspore.mint.*` API has an ACLNN sink path.
- The user wants a static inventory of `api_def`, non-deprecated `op_yaml` branches, `primitive`, `ascend_dispatch`, `kbk`, `pyboost`, `backward_defined`, and `backward_ops`.
- The user needs a mint pre-check before ACLNN adaptation or call-chain review.

Do not use this skill for:
- Non-`mindspore.mint.*` APIs.
- Full ACLNN runtime call-chain tracing.
- Runtime validation or operator implementation work.

## Instructions

### Step 1: read `./reference/mint_to_aclnn_precheck_guide.md` and follow its Step 1-3 exactly

### Step 2: only handle `mindspore.mint.*` APIs; if there is no `mint` entry, stop and report `mint_entry=✖️`

### Step 3: output only the result fields defined in the reference, and only for non-deprecated branches

### Step 4: deliver the inventory report using the display style defined in the reference

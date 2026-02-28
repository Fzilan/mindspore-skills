---
name: hf-transformers-components-upgrade-migrate
description: Migrate individual Hugging Face Transformers component files from v4.57.1 to v5.0.0 for mindone.transformers. Use when upgrading specific files like cache_utils.py, masking_utils.py, modeling_utils.py.
---

# HF Transformers Components Upgrade Migrate

Migrate individual Hugging Face Transformers files from v4.57.1 to v5.0.0 for mindone.transformers.

## When to Use

- Migrate a single file from transformers v4.57.1 to v5.0.0
- Update a specific component in mindone.transformers
- Perform granular, file-level migrations

## Repository Structure

Source: `transformers/src/transformers/`
Target: `mindone/mindone/transformers/`

Migration tracking: `upgrade_data_v4.57.1_to_v5.0.0.xlsx`

## Workflow

### Step 1: Analyze

**Analysis A: mindone vs transformers (same version v4.57.1)**
1. Read current mindone file (v4.57.1)
2. Read transformers v4.57.1 file
3. Compare to identify existing MindSpore-specific modifications
4. **Document MindSpore helper functions** (CRITICAL - do not lose these):
   - `dtype_to_min()` - replaces `torch.finfo(dtype).min`
   - Other dtype-specific constants like `_MIN_FP16`, `_MIN_FP32`
   - Any utility functions added for MindSpore compatibility
5. Document other MindSpore adaptations already in place

**Analysis B: transformers version diff (v4.57.1 → v5.0.0)**
1. Generate diff between transformers v4.57.1 and v5.0.0
2. Identify changes: additions, deletions, API breaking changes
3. Note v5.0.0 NEW functions that need MindSpore definitions (e.g., `is_flash_attention_requested`)
4. Note v5.0.0 NEW constants that should be removed (e.g., `_is_torch_xpu_available`)
5. Note tracing/dynamo related changes that should be DELETED (not replaced)

<IMPORTANT>
- Only add functions/definitions that are NEW in v5.0.0 AND needed by the code
- Do NOT add constants like `_is_torch_xpu_available` - these should be removed
- Do NOT define tracing/dynamo functions (like `is_tracing`) - DELETE the calls instead
</IMPORTANT>

### Step 2: Choose Migration Method

**Method 1: Full Replacement (Recommended for high complexity)**
1. Copy transformers v5.0.0 file to mindone
2. Run auto_convert.py:
   ```bash
   python skills/hf-transformers-components-upgrade-migrate/scripts/auto_convert.py mindone/transformers/file.py
   ```
3. Inspect output (check for existing logger, remaining torch refs)
4. Apply MindSpore adaptations (see references/mindspore-adaptations.md)
5. Handle file-specific cases

**Method 2: Diff Application (for low complexity)**
1. Generate diff between v4.57.1 and v5.0.0
2. Apply diff to mindone current version
3. Resolve conflicts

### Step 3: Verification

Run verification after migration:

```bash
# Syntax check
python -m py_compile mindone/transformers/file.py

# Import check
cd mindone && python -c "from mindone.transformers.file import *"

# Full verification
python skills/hf-transformers-components-upgrade-migrate/scripts/verify_migration.py mindone/transformers/file.py
```

## Key Adaptations

Critical MindSpore adaptations for v5.0.0+ files:

1. **Delete PyTorch compatibility constants** (v5.0.0+):
   - Remove `_is_torch_xpu_available`, `_is_torch_greater_or_equal_than_2_6`, etc.
   - Simplify conditionals that use these constants

2. **Add v5.0.0 NEW function definitions** (only if needed):
   - Check Step 1 Analysis B for NEW functions in v5.0.0 (not present in v4.57.1)
   - Add MindSpore versions only for functions the code actually uses
   - Example: `is_flash_attention_requested()` if it's NEW in v5.0.0

3. **Handle flex_attention**: Replace with NotImplementedError

4. **Remove XPU-specific code**: Delete `_can_skip_causal_mask_xpu` and simplify conditionals

5. **Delete tracing/dynamo code**: Remove `is_tracing()` calls and related checks (don't define the function)

6. **Replace torch.finfo**:
   - If mindone v4.57.1 has `dtype_to_min()` helper: use `dtype_to_min(dtype)`
   - Otherwise: `ms.tensor(float('-inf'), dtype=dtype)`

See [references/mindspore-adaptations.md](references/mindspore-adaptations.md) for complete adaptation guide.

## Guardrails

- Do NOT migrate `__init__.py` until all components are updated
- Always run auto_convert.py before manual edits:
  ```bash
  python skills/hf-transformers-components-upgrade-migrate/scripts/auto_convert.py mindone/transformers/file.py
  ```
- Check for existing logger definition before adding one
- Add new function definitions identified in Step 1

## References

- [MindSpore Adaptations Guide](references/mindspore-adaptations.md) - Complete adaptation checklist
- [Troubleshooting](references/troubleshooting.md) - Common errors and fixes
- [Migration Examples](references/examples.md) - Example migrations

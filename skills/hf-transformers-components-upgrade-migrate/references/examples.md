# Migration Examples

Real examples from migrations.

## Example 1: masking_utils.py

### Step 1: Analysis

**Analysis A (mindone vs transformers v4.57.1):**
- Existing MindSpore adaptations: `torch` → `ms`, `forward` → `construct`
- **CRITICAL - MindSpore helper functions to preserve:**
  - `dtype_to_min()` - helper for `torch.finfo(dtype).min`
  - `_MIN_FP16`, `_MIN_FP32`, `_MIN_FP64`, `_MIN_BF16` constants

**Analysis B (transformers v4.57.1 → v5.0.0):**
- Tracing changes: v5.0.0 extracts `is_tracing` to a function (was local variable in v4.57.1) - DELETE calls
- New constants: `_is_torch_greater_or_equal_than_2_6`, `_is_torch_xpu_available` (to be deleted)
- New XPU function: `_can_skip_causal_mask_xpu` (to be deleted)
- New function: `is_flash_attention_requested` (NEW in v5.0.0, needs definition)
- v5.0.0 renamed `PretrainedConfig` → `PreTrainedConfig`

### Step 2: Migration

**Deleted PyTorch compatibility constants:**
```python
# Deleted from v5.0.0 code:
# _is_torch_xpu_available = ...
# _is_torch_greater_or_equal_than_2_6 = ...
# _is_torch_greater_or_equal_than_2_5 = ...
```

**Deleted tracing/dynamo code (not replaced):**
```python
# v4.57.1: local variable
is_tracing = torch.jit.is_tracing() or ...
if not is_tracing and condition:
    ...

# v5.0.0: function call
if not is_tracing(padding_mask) and condition:
    ...

# MindSpore: DELETE tracing checks entirely
if condition:
    ...
```

**Added v5.0.0 NEW function definitions (only needed ones):**
```python
def is_flash_attention_requested(config) -> bool:
    return getattr(config, "_attn_implementation", None) in [
        "flash_attention_2", "flash_attention_3"
    ]
```

**Removed XPU function:**
```python
# Deleted entire _can_skip_causal_mask_xpu function
```

**Simplified XPU conditional:**
```python
# Before
if _is_torch_xpu_available:
    allow_is_causal_skip = not (getattr(past_key_values, "is_compileable", False)
                                and cache_position.shape[0] == 1)
else:
    allow_is_causal_skip = not getattr(past_key_values, "is_compileable", False)

# After
allow_is_causal_skip = not getattr(past_key_values, "is_compileable", False)
```

**Replaced torch.finfo (preserving existing helper):**
```python
# Analysis A found mindone v4.57.1 has dtype_to_min() helper

# Before
min_dtype = torch.finfo(dtype).min

# After (using existing helper)
min_dtype = dtype_to_min(dtype)
```

**Or if no helper exists:**
```python
# After (direct replacement)
min_dtype = ms.tensor(float('-inf'), dtype=dtype)
```

**Handled flex_attention:**
```python
def flex_attention_mask(...):
    raise NotImplementedError(
        "flex_attention is not supported in MindSpore. "
        "Please use 'sdpa', 'eager', or 'flash_attention_2' instead."
    )
```

### Step 3: Verification

```bash
python scripts/verify_migration.py mindone/transformers/masking_utils.py
```

Output:
```
[OK] No duplicate definitions found
[OK] No undefined references found
[OK] No specific issues found
```

## Example 2: cache_utils.py

### Key Adaptations

**Removed deprecated classes:**
```python
# Removed from __init__.py imports:
# - HybridCache
# - MambaCache
# - OffloadedStaticCache
# - SlidingWindowCache
```

**Updated type annotations:**
```python
# Before
cache_kwargs: dict[str, Any] | None = None

# After
cache_kwargs: Optional[dict[str, Any]] = None
```

**Updated imports:**
```python
# Before
from .configuration_utils import PreTrainedConfig

# After (v5.0.0 uses PretrainedConfig)
from transformers.configuration_utils import PretrainedConfig
```

## Common Migration Patterns

### Pattern A: High Complexity File (Method 1)

For files with many changes:

1. Copy v5.0.0 file
2. Run auto_convert.py
3. Read file and check what auto_convert did
4. Delete PyTorch compatibility constants
5. Add NEW v5.0.0 function definitions (only if needed)
6. Delete tracing/dynamo code (don't define functions)
7. Remove XPU code
8. Update docstrings
9. Verify with script

### Pattern B: Low Complexity File (Method 2)

For files with few changes:

1. Generate diff v4.57.1 → v5.0.0
2. Apply diff to mindone file
3. Resolve conflicts manually
4. Run verify_migration.py

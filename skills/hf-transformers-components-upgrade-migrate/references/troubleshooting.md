# Troubleshooting Guide

Common migration errors and their fixes.

## Duplicate Definition Error

**Symptom:**
```
SyntaxError: duplicate argument 'logger'
```

**Cause:** auto_convert preserved logger, manual edit added another.

**Fix:**
```bash
# Check for existing logger
grep -n "logger = logging" file.py

# Remove duplicate, keep only one
```

**Prevention:** Always run Step 2.3 inspection before manual edits.

## Undefined Function Error

**Symptom:**
```
NameError: name 'is_flash_attention_requested' is not defined
```

**Cause:** v5.0.0 introduced NEW functions that need MindSpore definitions.

**Fix:**
Add the missing function definition (only for NEW functions in v5.0.0):
```python
def is_flash_attention_requested(config) -> bool:
    return getattr(config, "_attn_implementation", None) in [
        "flash_attention_2", "flash_attention_3"
    ]
```

**Special Case - Tracing/Dynamo Functions:**
If you see `is_tracing` undefined, **DO NOT define it**. Instead, DELETE the calls:

```python
# Before
if not is_tracing(padding_mask) and condition:
    ...

# After
if condition:
    ...
```

**Prevention:** In Step 1, distinguish between:
- NEW v5.0.0 functions → Add definitions
- Existing tracing/dynamo code → Delete calls

## Missing Version Constant Error

**Symptom:**
```
NameError: name '_is_torch_greater_or_equal_than_2_6' is not defined
```

**Cause:** v5.0.0 added PyTorch version constants that don't exist in MindSpore.

**Fix:**
**DELETE the code that uses these constants, DO NOT add them.**

```python
# Before (v5.0.0 code)
if not _is_torch_greater_or_equal_than_2_6:
    raise ValueError("require torch>=2.6")
result = some_operation()

# After (MindSpore)
# Remove the version check entirely
result = some_operation()
```

Or for XPU checks:
```python
# Before
if _is_torch_xpu_available:
    return xpu_logic()
else:
    return default_logic()

# After
return default_logic()
```

## XPU Code Not Removed

**Symptom:** Code contains XPU-specific logic that fails in MindSpore.

**Fix:**
- Delete `_can_skip_causal_mask_xpu` function
- Simplify conditionals to remove XPU branches

## Import Error

**Symptom:**
```
ImportError: cannot import name 'PretrainedConfig'
```

**Fix:**
v5.0.0 renamed `PretrainedConfig` to `PreTrainedConfig`:
```python
# Before
from transformers.configuration_utils import PretrainedConfig

# After
from transformers.configuration_utils import PreTrainedConfig
```

## torch.finfo Error

**Symptom:**
```
AttributeError: module 'torch' has no attribute 'finfo'
```

**Fix:**
```python
# Before
torch.finfo(dtype).min

# After
ms.tensor(float('-inf'), dtype=dtype)
```

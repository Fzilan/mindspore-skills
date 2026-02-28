# MindSpore Adaptations Guide

Complete reference for adapting HuggingFace Transformers v5.0.0 code to MindSpore.

## Quick Reference

### Import Sources

**Preserve original mindone v4.57.1 import sources:**

| If original imports from | Keep importing from | Example |
|--------------------------|---------------------|---------|
| `.utils` | `.utils` | `is_mindspore_tensor`, `requires_backends` |
| `transformers` | `transformers` | `cached_file`, `safe_load_json_file` |

**Handle v5.0.0 NEW functions:**

```python
# Does NOT depend on PyTorch -> Import from transformers
from transformers.utils import safe_load_json_file

# DEPENDS on PyTorch -> Add MindSpore version to mindone .utils
def _is_tensor_or_array_like(x):
    if is_numpy_array(x):
        return True
    if is_mindspore_available() and is_mindspore_tensor(x):
        return True
    return False
```

### Code Structure to Preserve

**Do NOT delete when adapting v5.0.0 code:**

```python
# Availability checks
if not is_mindspore_available():
    raise ImportError("Unable to convert output to MindSpore tensors format, MindSpore is not installed.")
import mindspore as ms  # noqa

# Backend requirements
requires_backends(self, ["mindspore"])
```

**Common mistake**: When replacing `TensorType.PYTORCH` with `TensorType.MINDSPORE`, only replace framework-specific API calls, keep all other logic.

## Detailed Adaptations

### Basic Conversions

| From | To |
|------|-----|
| `import torch` | `import mindspore as ms` |
| `import torch.nn as nn` | `from mindspore import mint, nn` |
| `torch.nn.Module` | `ms.nn.Cell` |
| `def forward(self, ...)` | `def construct(self, ...)` |
| `torch.zeros(..., device=device)` | `mint.zeros(...)` (remove device) |
| `torch.arange(..., device=device)` | `mint.arange(...)` (remove device) |
| `tensor.item()` | `tensor.asnumpy().item()` |
| `torch.finfo(dtype).min` | `ms.tensor(float('-inf'), dtype=dtype)` |

### v5.0.0+ Specific Changes

**Delete these PyTorch constants:**
- `_is_torch_xpu_available`
- `_is_torch_greater_or_equal_than_2_6`
- `_is_torch_greater_or_equal_than_2_5`

**Delete these patterns:**
```python
# Remove version checks
if not _is_torch_greater_or_equal_than_2_6:
    raise ValueError("... require torch>=2.6")

# Remove XPU code
if _is_torch_xpu_available:
    return _can_skip_causal_mask_xpu(...)

# Remove tracing/dynamo (don't replace, DELETE)
if not is_tracing(padding_mask) and condition:  # -> Keep only: if condition:
```

**Handle flex_attention:**
```python
def flex_attention_mask(...):
    raise NotImplementedError(
        "flex_attention is not supported in MindSpore. "
        "Please use 'sdpa', 'eager', or 'flash_attention_2' instead."
    )
```

### Decorators to Remove

- `@torch.jit.script`
- `@torch.compile`
- `@use_kernel_func_from_hub`
- `@deprecate_kwarg` (if not in mindone)
- `@auto_docstring` (v5.0.0+, mindone doesn't need)

Remove imports when removing decorators.

### Docstring Replacements

| Original | Replacement |
|----------|-------------|
| `torch.Tensor` | `ms.Tensor` |
| `torch.arange` | `mint.arange` |
| `torch.float32` | `ms.float32` |
| `torch.dtype` | `ms.Type` |
| `torch.device` | Remove or adapt |
| `forward()` | `construct()` |

## Common Patterns

### Device Handling Removal

```python
# Before
def process(self, x, device):
    x = x.to(device)
    y = torch.zeros(..., device=device)

# After
def process(self, x):
    y = mint.zeros(...)
```

### Cache with Offloading

```python
# In __init__, add validation
if kwargs.get("offload"):
    raise NotImplementedError("mindspore do not support offload/prefetch yet")
```

### Logger Check

```bash
# Check before adding
grep -n "logger = logging" file.py

# Only add if missing
logger = logging.get_logger(__name__)
```

## Verification Checklist

### Import Verification
- [ ] Original mindone v4.57.1 import sources preserved
- [ ] `.utils` imports from `.utils`, `transformers` imports from `transformers`
- [ ] NEW v5.0.0 functions checked for PyTorch dependency

### Code Preservation
- [ ] `is_mindspore_available()` checks preserved
- [ ] `requires_backends(self, ["mindspore"])` preserved
- [ ] Function-level imports preserved (`import mindspore as ms  # noqa`)
- [ ] Error handling logic preserved

### PyTorch Removal
- [ ] PyTorch compatibility constants deleted
- [ ] Tracing/dynamo code removed (not replaced)
- [ ] XPU code removed
- [ ] No torch imports remain
- [ ] No `torch.` references remain

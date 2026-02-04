---
name: hf-transformers-migrate
description: Migrate Hugging Face transformers models to mindone.transformers. Use when porting BERT, GPT, LLaMA, or other transformer models.
---

# HF Transformers Migration

Migrate Hugging Face transformers models to MindOne's transformers implementation with standard workflow, tool-assisted conversion, and registration updates.

## When to Use

- Porting Hugging Face transformers models like LLaMA, BERT, Qwen to MindSpore
- Migrating transformers models to MindONE with repo-specific rules.
- Adding new transformer architectures

## Repository

Source Repository: **huggingface transformers**: https://github.com/huggingface/transformers
- **core**: `transformers/src/transformers`
- **model tests**: `transformers/tests/models`

Target Repository: **mindone**: https://github.com/mindspore-lab/mindone
- **mindone.transformers core**: `mindone/mindone/transformers`
- **model tests**: `mindone/tests/transformers_tests`


## Instructions

A standard workflow for transformer Model migration from PyTorch to MindSpore.

### Step 1. Intake to Collect

1. Identify the target and source repositories' path and structure, and check the similarity.
2. Identify the excact model name from prompt as the `{model_name}` of migration task. 
- default source path: `transformers/src/transformers/models/{model_name}/`.
- default target path : `mindone/mindone/transformers/models/{model_name}/`.

<IMPORTANT>Prioritize `model_name` precision. If the name is ambiguous or incomplete, pause and confirm the exact version with the user before proceeding.</IMPORTANT>

### Step 2. Modeling files Migration with Auto-convert Tool

1. Copy the intended files from source to target.

The intended files are:
- modeling files: `modeling_*.py`
- any processing files to migrate: `processing_*.py`, `image_processing_*.py`, `video_processing_*.py`.

2. Do single file in-place conversion for the files. The fixed mapping script is within this skill folders.

Single file in-place:
```bash
python tools/auto_convert.py \
  --src_file path/to/file.py --inplace
```
<NOTES> Install requirements of the auto_convert tool first. </NOTES>
```bash
pip install -r tools/requirements.txt
```

<MUST> MUST: Run auto_convert script before any manual edits. </MUST>

### Step 3. Manual fix checklist

#### 3.1 Structural and API
- `torch.nn.Module` -> `mindspore.nn.Cell`.
- `forward` -> `construct`.
- `torch.nn.Parameter` -> `mindspore.Parameter`.
- Replace `torch` and `torch.nn.functional` usages with `mindspore.mint` or `mindspore.ops`.
- Prefer `mindspore.mint`, then `mindspore.ops`, then `mindspore.nn`.
- Drop unsupported `inplace=True` args.

#### 3.2 Device Handling

- Remove torch.device, .to(device), and .cuda() calls. 
- Remove device code: `.to(device)`, `.cuda()`, `torch.device`, `mps` branches.
- Should check the device related code and remove it.

<EXAMPLE>

<BEFORE>

```python
def _dynamic_frequency_update(self, position_ids, device):
    seq_len = mint.max(position_ids) + 1
    if seq_len > self.max_seq_len_cached:  # growth
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, seq_len=seq_len)
        self.register_buffer("inv_freq", inv_freq, persistent=False)  # TODO joao: may break with compilation
        self.max_seq_len_cached = seq_len

    if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:  # reset
        self.original_inv_freq = self.original_inv_freq.to(device)
        self.register_buffer("inv_freq", self.original_inv_freq, persistent=False)
        self.max_seq_len_cached = self.original_max_seq_len
    ...
    device_type = x.device.type
    device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"	
```

<AFTER>

```python
def _dynamic_frequency_update(self, position_ids):
    seq_len = mint.max(position_ids) + 1
    if seq_len > self.max_seq_len_cached:  # growth
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, seq_len=seq_len)
        self.inv_freq = inv_freq  # TODO joao: may break with compilation
        self.max_seq_len_cached = seq_len

    if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:  # reset
        self.inv_freq = self.original_inv_freq
        self.max_seq_len_cached = self.original_max_seq_len
    ...
    # all device related code should be removed  
```


#### 3.3 Imports and decorators
- Keep config/tokenizer imports from HF `transformers`.
- Use `mindone.transformers.modeling_utils` for modeling utilities.
- Remove unused or PyTorch-only imports that are not migrated. This avoids false positives later.
- Remove decorators, likes:
  - `@torch.jit.script` - PyTorch-specific
  - `@auto_docstring` - do not migrate and use
- Remove kernel hub decorators belows as we use mindspore local implementation:
  - `@use_kernel_func_from_hub`
  - `@use_kernelized_func`
  - `@use_kernel_forward_from_hub`
- If a decorator is not migrated, delete both its import and usage.

#### 3.4 Tensors and shapes
- Use `mindspore.Tensor` in docstrings.
- Wrap shape arguments in tuples, e.g. `.view((b, s, h))`.


### Step 4. Registration and exports

Update these files to register the model:

- Add config to `mindone/mindone/transformers/models/auto/configuration_auto.py`.
- Add model class to `mindone/mindone/transformers/models/auto/modeling_auto.py`.
- Update processor maps if processor files are migrated.
  - `mindone/mindone/transformers/models/auto/processing_auto.py` (if needed)
  - `mindone/mindone/transformers/models/auto/image_processing_auto.py` (if needed)
  - `mindone/mindone/transformers/models/auto/video_processing_auto.py` (if needed)
- Export chain updates:
  - `mindone/mindone/transformers/models/{model_name}/__init__.py`
  - `mindone/mindone/transformers/models/__init__.py`
  - `mindone/mindone/transformers/__init__.py`
- Update `mindone/mindone/transformers/models/{model_name}/__init__.py`:
  - Do not remove the file header comment at the top; preserve it exactly.
  - After the header, allow zero or more lines that match the import form: from .<module> import *
  - All other non-header lines must be removed
  - For each retained import line, verify that the module exists in the same directory
  - If a referenced module does not exist, drop that import line

Tip: use HF auto files as a reference to insert in the correct order.

### Step 5. Done criteria
- Model imports cleanly in MindOne.
- Auto mappings and exports are updated.

## Guardrails
- Universal constraints are documented here; repo-specific rules live in `references/guardrails.md` and take precedence if they conflict.
- Do not migrate `configuration_*.py`, `tokenization_*.py`, or `*moduler_*.py`. Any configurations and tokenizations should be directly import from huggingface transformers.
- Only migrate processing files if they manipulate torch tensors; otherwise use HF implementations.

## References
- Environment and test commands: `references/env.md`
- Model tests generation skills: `hf-transformers-test-builder`

## Output
- Files changed and why.
- Tests generation/run or suggested.
- Any remaining TODOs or risks.


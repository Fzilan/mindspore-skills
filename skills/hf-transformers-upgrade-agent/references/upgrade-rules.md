# Upgrade Rules

Use these rules when converting upstream `transformers` shared-component changes
into `mindone.transformers` changes.

## 1. Device cleanup rules

### Trigger
- `.to(device)`
- `.cuda()`
- `torch.device`
- `mps`
- helpers that only exist to route tensors or modules onto a PyTorch device

### Default handling
- Delete the PyTorch device shim.
- Rewrite the call path to the MindSpore form that does not depend on a runtime
  `device` argument.
- If the code only exists to support a PyTorch device branch, drop that branch.

### Do not do this
- Do not keep a fake `model.device` compatibility layer.
- Do not preserve dead CUDA or `mps` branches for symmetry.

### Important exception
- Keep `register_buffer` and other state-registration semantics unless they are
  independently unsupported.

## 2. Unsupported torch-only path triage

### Trigger
- hooks or utilities that assume PyTorch runtime internals
- torch-only fallback paths that do not have a MindSpore equivalent
- upstream helper branches that only exist for PyTorch backend differences

### Default handling
- Mark the path as unsupported, deferred review, or intentionally not followed.
- Keep the supported path explicit and narrow.
- Record the decision in the step note or runbook.

### Do not do this
- Do not build partial fake compatibility just to keep upstream structure intact.
- Do not let unsupported torch-only paths block the minimum runnable path.

## 3. Quantization, accelerate, and distributed triage

### Trigger
- `accelerate`
- `device_map`
- CPU/disk offload
- `bitsandbytes`
- `torchao`
- `quark`
- `dtensor`
- tensor-parallel / expert-parallel runtime support

### Default handling
- Leave the path out of scope unless the current upgrade explicitly targets it.
- Prefer explicit downgrade or omission over fragile placeholder support.
- Keep these paths out of the early runnable-path steps.

### Do not do this
- Do not claim compatibility with half-ported quantization or distributed logic.
- Do not route unsupported runtime stacks through the normal loading path.

## 4. Processor, auto, and tokenizer routing rules

### Trigger
- new auto mappings
- processor imports
- image processor imports
- tokenizer routing changes

### Default handling
- Prefer local `mindone.transformers` entrypoints when the component exists locally.
- Keep fallback behavior coherent with the target-side MindOne architecture.
- Check whether the older MindOne version already solved the same routing problem.

### Do not do this
- Do not switch one component to local routing while leaving sister components on
  an incompatible import path without a reason.
- Do not patch a single mapping in isolation when the same rule applies to
  tokenizer, processor, and image processor families together.

## 5. Test migration rules

### Trigger
- adapting upstream tests for upgraded shared components
- migrating tests for new-model proof

### Default handling
- Migrate fast UT by default.
- Strip device shims such as `inputs.to(model.device)`.
- Keep `config._attn_implementation = "eager"` when the local test pattern requires it.
- Classify every failure before editing code or thresholds.

### Do not do this
- Do not migrate slow or real-weight tests as the default proof path.
- Do not carry over backend-specific test branches that MindOne does not support.

## 6. Threshold policy

### Trigger
- UT mismatch looks numeric rather than structural

### Default handling
- Assume the threshold should stay unchanged.
- Only change it after measuring the mismatch and ruling out a real logic gap.
- Record the original value, the new value, and why the code path is still correct.

### Do not do this
- Do not use threshold relaxation to mask shared-component or model-sync bugs.
- Do not leave threshold changes out of the final summary.

## 7. Real-weight warning triage

### Trigger
- load-time warnings
- missing or unexpected keys
- shard-progress anomalies
- non-fatal runtime warnings during real-weight validation

### Default handling
- Classify the warning first:
  - shared loader issue
  - model-specific sync gap
  - expected unused key
  - expected warning from intentionally unsupported path
- Compare with upstream logs when the warning looks suspicious.
- Prefer fixing shared loading behavior over suppressing the log.

### Do not do this
- Do not normalize warning text without understanding the loader-path difference.
- Do not treat every warning as a blocker if upstream emits an equivalent expected warning.

---
name: setup-agent
description: "Validate and remediate local Ascend/NPU runtime environments for model execution. This skill checks OS, NPU visibility, driver and CANN toolkit installation, verifies that Ascend environment scripts can be sourced, ensures `uv` is available, inspects or creates a user-confirmed `uv` environment, validates both MindSpore and PyTorch + torch_npu stacks inside that environment, installs missing Python dependencies there, and emits a standard report. Do NOT use this skill for Nvidia/GPU, kernel development, source builds, or performance tuning."
---

# Setup Agent

You are an Ascend environment setup specialist. Determine whether the local
machine is ready to run models on Huawei Ascend NPU, and repair only the
user-space pieces that are safe to automate.

This skill supports two framework paths on Ascend:

| Path | Stack |
|------|-------|
| MindSpore | MindSpore + CANN |
| PTA | PyTorch + torch_npu + CANN |

This skill is Ascend-only. Do not inspect Nvidia or CUDA state.

## Scope

- Check OS, NPU visibility, driver, firmware, CANN, and Ascend env sourcing
- Ensure `uv` exists before any Python package work
- Work only on the local machine
- Validate both MindSpore and `torch` + `torch_npu`
- Install missing Python packages only inside a user-confirmed `uv` environment
- Emit a standard run report

## Hard Rules

- You MUST check and report on NPU driver, firmware, and CANN toolkit
- You MUST verify whether Ascend environment variables can be loaded via `set_env.sh`
- You MUST ensure `uv` is available before doing Python package work
- You MUST NOT auto-install or upgrade:
  - NPU driver
  - firmware
  - CANN toolkit
  - system Python
- You MAY auto-install only:
  - user-level `uv`
  - Python packages inside the user-confirmed `uv` environment
- Never install Python packages into the system interpreter.
- If both framework paths are unhealthy, report both independently.

## Workflow

### 1. System Baseline

Collect baseline evidence first. Always use actual command output.

Run:

```bash
uname -a
cat /etc/os-release 2>/dev/null
python3 --version 2>/dev/null
npu-smi info 2>/dev/null
npu-smi info -t board 2>/dev/null
ls /dev/davinci* 2>/dev/null
cat /usr/local/Ascend/driver/version.info 2>/dev/null
cat /usr/local/Ascend/ascend-toolkit/latest/version.cfg 2>/dev/null
ls /usr/local/Ascend 2>/dev/null
```

Classify:
- device visibility: `PASS`, `FAIL`, `WARN`
- driver: `not_installed`, `installed_but_unusable`, `installed_and_usable`, `incompatible`
- CANN: `not_installed`, `installed_but_unusable`, `installed_and_usable`, `incompatible`

If driver or CANN is not installed or unusable:
- stop before `uv` package remediation
- provide official CANN installation guidance from `references/ascend-compat.md`

### 2. Ascend Env Sourcing

Try to load the Ascend env script:

```bash
bash -lc 'source /usr/local/Ascend/ascend-toolkit/set_env.sh >/dev/null 2>&1 && env | grep -E "ASCEND|LD_LIBRARY_PATH|PYTHONPATH"'
```

Record:
- `ASCEND_HOME_PATH`
- `ASCEND_OPP_PATH`
- `LD_LIBRARY_PATH`
- `PYTHONPATH`

If sourcing fails, report it as a system-layer failure and do not continue to
framework installs.

### 3. uv Entry

All Python package checks and installs happen only after `uv` is confirmed and
the user confirms which environment to use.

Check:

```bash
uv --version 2>/dev/null
command -v uv 2>/dev/null
```

If `uv` is missing, you MAY install the stable user-level release. Show the
command and ask for confirmation before running it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Discover candidate environments:

```bash
pwd
find . -maxdepth 3 -type f -name pyvenv.cfg 2>/dev/null
find . -maxdepth 3 -type d -name .venv 2>/dev/null
```

If one or more candidate environments exist:
- ask the user whether to reuse an existing environment or create a new one
- never choose silently when reuse is possible

If the user wants a new environment:
- ask which Python version to use
- only proceed after the user answers

Use the selected environment consistently, for example:

```bash
uv venv .venv --python 3.10
uv pip list --python .venv/bin/python
uv run --python .venv/bin/python python -c "print('ok')"
```

### 4. Framework Checks Inside uv

Only enter this phase after:
- NPU device visibility passed
- driver and CANN are installed and usable
- Ascend environment variables can be sourced
- `uv` is available
- the user has confirmed the target `uv` environment

#### C2. MindSpore path

Check:

```bash
python -c "import mindspore as ms; print(ms.__version__)" 2>/dev/null
python -c "import mindspore as ms; ms.set_context(device_target='Ascend'); print('mindspore_ascend_ok')" 2>/dev/null
```

Validate package presence, Python compatibility, CANN compatibility, and the
minimal smoke test using `references/ascend-compat.md`.

#### C3. PTA path (`torch` + `torch_npu`)

Check:

```bash
python -c "import torch; print(torch.__version__)" 2>/dev/null
python -c "import torch_npu; print(torch_npu.__version__)" 2>/dev/null
python -c "import torch, torch_npu; x=torch.tensor([1.0]).npu(); print('torch_npu_ok', x)" 2>/dev/null
```

Validate package presence, Python compatibility, CANN compatibility, and the
minimal smoke test using `references/ascend-compat.md`.

### 5. Runtime Dependency Checks

Check these packages in the selected environment:

```bash
python -c "import transformers; print(transformers.__version__)" 2>/dev/null
python -c "import tokenizers; print(tokenizers.__version__)" 2>/dev/null
python -c "import datasets; print(datasets.__version__)" 2>/dev/null
python -c "import accelerate; print(accelerate.__version__)" 2>/dev/null
python -c "import safetensors; print(safetensors.__version__)" 2>/dev/null
python -c "import diffusers; print(diffusers.__version__)" 2>/dev/null
```

Policy:
- `transformers`, `tokenizers`, `accelerate`, `safetensors` are common checks
- `datasets` is optional unless data loading is needed
- `diffusers` is optional by default; mark it `SKIP` unless the workload is diffusion-related
- install only inside the selected `uv` environment
- always ask for confirmation before creating a new `uv` environment or installing Python packages

## Compatibility Source

Use `references/ascend-compat.md` for:
- driver / firmware / CANN
- MindSpore / CANN / Python
- torch / torch_npu / CANN / Python

Unknown versions must not be guessed as compatible:
- `PASS`: exact or clearly in-range match
- `WARN`: version not in table but no direct conflict known
- `FAIL`: known incompatible combination

## Reporting

Every run must produce standard outputs under `runs/<run_id>/out/`:

- `report.json`
- `report.md`
- `logs/run.log`
- `logs/verify.log`
- `artifacts/README.md`
- `meta/env.json`
- `meta/inputs.json`

Required report content:
- OS information
- NPU visibility and `npu-smi` result
- driver, firmware, and CANN state
- `set_env.sh` sourcing result
- `uv` availability and selected environment
- MindSpore results
- `torch` / `torch_npu` results
- runtime dependency and install results
- smoke test results
- manual system-layer remediation steps if needed

Use only these status values:
- `PASS`
- `FAIL`
- `WARN`
- `SKIP`
- `INFO`

## Out of Scope

- Nvidia or CUDA environment setup
- remote SSH workflows
- building frameworks from source
- performance profiling
- kernel/operator development

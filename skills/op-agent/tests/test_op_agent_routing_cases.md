# op-agent Routing Cases

Prompt-eval style samples for the navigator skill. These are not executable
tests; they define the expected routing behavior and wording discipline.

## Case 1: CPU plugin path

### Input

```text
api_name: mindspore.mint.xxx
target_backend: CPU
problem_type: operator-gap
known_evidence:
  - The missing implementation should reuse an external plugin-style path.
  - CPU backend currently does not support this operator.
```

### Expected

- explain the two ways first: build inside MindSpore vs build through plugin
- explain the six builders, then focus on the CPU pair
- restate the CPU operator gap
- route to `cpu-plugin-builder`
- state why plugin is the best-fit support class

## Case 2: CPU native path

### Input

```text
api_name: mindspore.mint.xxx
target_backend: CPU
problem_type: operator-gap
known_evidence:
  - The gap should be solved through MindSpore's native CPU integration path.
```

### Expected

- explain the two ways first
- explain the six builders, then focus on the CPU pair
- route to `cpu-native-builder`
- keep the answer at navigator level

## Case 3: GPU unsupported

### Input

```text
api_name: mindspore.mint.xxx
target_backend: GPU
problem_type: operator-gap
known_evidence:
  - The operator is unsupported on GPU.
```

### Expected

- explain the two ways first
- explain the six builders, then focus on the GPU pair
- when no contrary evidence exists, prefer `gpu-native-builder`
- keep the explanation user-facing

## Case 4: Ascend ACLNN maps to NPU native

### Input

```text
api_name: mindspore.mint.xxx
target_backend: NPU
problem_type: operator-gap
known_evidence:
  - The issue belongs to the ACLNN path on Ascend.
```

### Expected

- explain the two ways first
- explain the six builders, then focus on the NPU pair
- apply the explicit rule that Ascend ACLNN belongs to the NPU Native path
- route to `npu-native-builder`
- explain why the native NPU path is the better fit

## Case 5: Native vs Plugin ambiguity

### Input

```text
api_name: mindspore.mint.xxx
target_backend: CPU
problem_type: operator-gap
known_evidence:
  - CPU backend is unsupported.
  - No evidence yet distinguishes native from plugin.
```

### Expected

- explain the two ways first
- explain the six builders, then focus on the CPU pair
- explicitly state the ambiguity
- present both `cpu-native-builder` and `cpu-plugin-builder`
- ask for the missing decision input instead of guessing

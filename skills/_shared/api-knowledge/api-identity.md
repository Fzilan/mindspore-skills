# MindSpore API Identity Reference

This reference collects the static facts used to resolve a public MindSpore API
into its internal API-level identity.

### Scope

This reference focuses on the following questions:

- Whether the public API entry exists.
- Which public surface the entry belongs to, such as `mindspore.mint`,
  `mindspore.Tensor`, `mindspore.ops.function`, or `mindspore.ops.auto_generate`.
- Which export form the API uses, such as `functional_overload`, alias export,
  direct auto-generate export, or function wrapper export.
- Which internal symbol the public API resolves to.
- Which `api_def` file applies, if any.
- Which non-deprecated `op_yaml` branches apply.
- Which Primitive each active branch maps to.

This reference describes identity facts only. It does not cover backward
inventory or backend dispatch evidence.

### Common Identity Facts

When tracing a public API into its operator identity, the facts that usually
matter are:

- public API name
- export source
- internal symbol
- `api_def`, if any
- active `op_yaml`
- Primitive

These are common identity facts, not a required output schema in this
reference.

### Source-of-Truth Paths

| Purpose | Path |
| --- | --- |
| `mindspore.mint.*` public exports | `mindspore/python/mindspore/mint/__init__.py` |
| `mindspore.Tensor.*` methods | `mindspore/python/mindspore/common/tensor/tensor.py` |
| Function wrappers | `mindspore/python/mindspore/ops/function/*.py` |
| Overload entry definitions | `mindspore/ops/api_def/*.yaml` |
| Operator definitions | `mindspore/ops/op_def/yaml/*_op.yaml` |
| Auto-generated Primitive exports | `mindspore/python/mindspore/ops/auto_generate/gen_ops_prim.py` |

### mint entry -> op yaml

This section focuses on the forward identity path:

- public API entry
- inner function or exported symbol
- `api_def`, if any
- non-deprecated `op_yaml`
- Primitive naming clue

#### Case 1: `functional_overload` export

exported from `mindspore.ops.functional_overload` -> it has multiple implementations, do not infer a single primitive directly -> check `ops/api_def/<api>.yaml` first -> continue with each non-deprecated `op_yaml` branch

e.g.

```python
from mindspore.ops.functional_overload import max
```

the public API `max` is exported through `mindspore.ops.functional_overload` -> check `mindspore/ops/api_def/max.yaml` first -> continue with each non-deprecated `op_yaml` branch independently

e.g. a branch list from `mindspore/ops/api_def/max.yaml` may look like:

```yaml
max:
  - op_yaml: max_op.yaml
    py_method: tensor_max
    Ascend: pyboost
    CPU: pyboost
    GPU: pyboost
    interface: tensor, function

  - op_yaml: max_dim_op.yaml
    py_method: tensor_maxdim
    Ascend: pyboost
    CPU: pyboost
    GPU: pyboost
    disable_scalar_tensor: dim
    interface: tensor, function

  - op_yaml: maximum_op.yaml
    py_method: tensor_maximum
    Ascend: pyboost
    CPU: pyboost
    GPU: pyboost
    interface: function
```

This further tells you:

- `max_op.yaml`, `max_dim_op.yaml`, and `maximum_op.yaml` are different active candidates
- one public API may map to multiple branches
- branch reality matters more than the public name alone

#### Case 2: alias export

exported `xxx_ext as xxx` -> primitive is `XxxExt` not `Xxx` -> `xxx_ext_op.yaml`

e.g.

```python
from mindspore.ops.function.math_func import linspace_ext as linspace
```

- the public API name is `linspace`
- the internal function name is `linspace_ext`
- the mapping should keep the `_ext` suffix
- the forward YAML is `linspace_ext_op.yaml`
- the corresponding Primitive family is `LinSpaceExt`

Do not collapse `linspace_ext` back to plain `linspace`.

#### Case 3: `ops.auto_generate` direct export

When a symbol is exported directly from `mindspore.ops.auto_generate`, it usually points to one Primitive family directly.

- start from `<symbol>_op.yaml`
- still confirm the final Primitive from the YAML top-level operator name

#### Case 4: `ops.function` wrapper export

exported from `mindspore.ops.function` means the wrapper body itself is part of the identity evidence. 
You should inspect the wrapper body first, the wrapper may continue through `api_def`, or directly through one `op_yaml`

Example 1:

`from mindspore.ops.function.math_func import divide` -> navigate to the definition of `divide` -> `return div(input, other, rounding_mode=rounding_mode)` -> check `ops/api_def/div.yaml` -> continue with its non-deprecated branches `divs_op.yaml`, `div_op.yaml`, `divmods_op.yaml`, `divmod_op.yaml`

Example 2

`from mindspore.ops.function.array_func import full_ext as full` -> navigate to the definition of `full_ext` -> `return fill_scalar_(size, fill_value, dtype)` -> `ops/op_def/yaml/fill_scalar_op.yaml`

Example 3:

`from mindspore.ops.function.nn_func import softmax_ext` -> navigate to the definition of `softmax_ext` -> the function first normalizes `dim` and `dtype`, then `return softmax_impl(input, dim)` -> directly check `ops/op_def/yaml/softmax_op.yaml`

#### Case 5: Tensor inplace method

`Tensor.xxx_` should be treated as a distinct public entry.

e.g. `Tensor.sub_`

- the trailing `_` is part of the identity
- the method is an inplace variant, not the plain `sub` family
- the delegated internal symbol should be resolved before deciding the final
  `op_yaml`


### Primitive Naming Conventions

Primitive naming facts:

- The YAML top-level operator name is the source of truth for Primitive naming.
- The name is typically converted to UpperCamelCase.
- Meaningful suffixes such as `Ext`, `Scalar`, `Inplace`, and `Grad` are kept.

Examples:

- `fill_scalar` -> `FillScalar`
- `sub_ext` -> `SubExt`
- `add_scalar` -> `AddScalar`
- `softmax_backward` -> `SoftmaxBackward`

### Local Correctness Facts

- Source evidence is stronger than naming intuition.
- Overloaded APIs remain branch-based.
- Deprecated branches should not be treated as active branches.
- Primitive identity should come from resolved YAML when YAML is available.
- Alias targets should not be collapsed back to the public name.

### Worked Examples

#### Example 1: alias export

```python
from mindspore.ops.function.math_func import linspace_ext as linspace
```

Resolved facts:

- `mindspore.mint.linspace` ->
  `mindspore.ops.function.math_func.linspace_ext` ->
  `linspace_ext_op.yaml` -> `LinSpaceExt`

#### Example 2: overload export

```python
from mindspore.ops.functional_overload import max
```

Resolved facts:

- `mindspore.mint.max` -> `mindspore.ops.functional_overload.max` ->
  `ops/api_def/max.yaml` -> multiple non-deprecated `op_yaml` branches

This tells you:

- one public API may split into multiple active operator branches
- Primitive identity must be checked branch by branch

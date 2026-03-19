# MindSpore Ascend Backend Lens Reference

This reference collects the static Ascend dispatch facts attached to one active
branch that has already been resolved at the API identity layer.

### Scope

This lens focuses on the following questions, per active branch:

- Whether Ascend dispatch is visible from static source layout.
- Whether the branch is `auto_generate`, `customize`, or unsupported.
- Whether `kbk` evidence is present.
- Whether `pyboost` evidence is present.

This is a static inventory lens only. It does not prove runtime success.

### Common Ascend Facts

This lens assumes that branch identity is already known, including:

- resolved `op_yaml`
- resolved `primitive`
- branch context from identity resolution

### Source-of-Truth Paths

| Purpose | Path |
| --- | --- |
| Operator YAML | `mindspore/ops/op_def/yaml/*_op.yaml` |
| Auto-generated ACLNN mapping | `mindspore/python/mindspore/ops_generate/pyboost/aclnn_config.yaml` |
| Customize PyBoost implementations | `mindspore/ccsrc/plugin/device/ascend/kernel/pyboost_impl/customize/` |
| Customize KBK implementations | `mindspore/ccsrc/plugin/device/ascend/kernel/opapi/aclnn_kernel/mod_impl/customize/` |
| Generated KBK registration evidence | `aclnn_kernel_register_auto.cc` |

### Resolve Forward Fields from `op_yaml`

For each active `op_yaml`, check the corresponding file in
`mindspore/ops/op_def/yaml/`.

- read `dispatch.enable`
- check whether an explicit `Ascend: XxxAscend` entry is present
- infer `dispatch`, `kbk`, and `pyboost` from YAML and source layout only

Common facts:

- `dispatch` values: `auto_generate`, `customize`, `unsupported`
- evidence is branch-local
- missing evidence should stay conservative

#### Case 1: `dispatch.enable: True` and no `Ascend: XxxAscend`

This usually means the branch goes through the auto-generated Ascend path.

Common evidence:

- Primitive presence in `aclnn_config.yaml`
- generated registration evidence such as `aclnn_kernel_register_auto.cc`

#### Case 2: `dispatch.enable: True` and `Ascend: XxxAscend`

This usually means the branch uses a handwritten Ascend customize path.

Common customize evidence locations:

- `.../kernel/pyboost_impl/customize/xxx.h` and `.cc`
- `.../kernel/opapi/aclnn_kernel/mod_impl/customize/xxx_aclnn_kernel.h` and
  `.cc`

#### Case 3: no `dispatch.enable`

This usually means no static Ascend ACLNN path is visible from the branch YAML.

### Local Correctness Facts

- Ascend evidence is branch-local, not public-API-global.
- `dispatch.enable` is the first gate.
- `customize` requires explicit source evidence.
- This lens reports static inventory only.

### Worked Examples

#### Example 1: auto-generated Ascend path

```yaml
dispatch:
  enable: True
  GPU: None
```

gives:

- `op_yaml` -> `dispatch.enable: True` -> auto-generated Ascend path
- generated registration and mapping evidence are expected in the checked tree

#### Example 2: customize Ascend path

```yaml
dispatch:
  enable: True
  Ascend: AddScalarAscend
```

gives:

- `op_yaml` -> `dispatch.enable: True` + `Ascend: XxxAscend` -> customize Ascend path
- customize kernel and customize PyBoost evidence should be checked explicitly

# MindSpore Backward Inventory Reference

This reference collects the static facts used to inspect branch-level backward
evidence after API identity is already known.

### Scope

This reference focuses on the following questions:

- Whether a Primitive has a registered bprop definition.
- Whether the backward path uses inline computation or a dedicated grad op.
- Which backward operator calls appear in the registered body.

This is a generic Primitive-level reference. It is not specific to Ascend.

### Common Backward Facts

This reference assumes that API identity is already known, including:

- `api`
- resolved branch context
- resolved `primitive`

Backward inventory is branch-local. One public API may produce different
backward facts for different branches.

The facts that usually matter are:

- whether bprop is defined
- whether the backward path is dedicated grad or inline composition
- which backward operators appear in the registered body

### Source-of-Truth Paths

| Purpose | Path |
| --- | --- |
| Gradient registrations | `mindspore/ccsrc/frontend/expander/grad/` |
| Primary search token | `REG_BPROP_BUILDER("<primitive>")` |

### primitive -> bprop

```text
REG_BPROP_BUILDER("<primitive>")
```

This tells you:

- search with the resolved Primitive, not the public API name
- registration presence is the first backward evidence gate
- if there is no registration hit, that branch has no static bprop evidence

Common backward body patterns:

- `Emit("XxxGrad", ...)` -> dedicated grad path
- `ib->Mul(...)`, `ib->Rsqrt(...)`, `ib->Sub(...)`, `ib->Square(...)` ->
  inline operator composition

The backward inventory should stay branch-local:

- one branch may have a registered bprop while another branch does not
- operator names should come from visible registered-body evidence
- repeated operator names may be de-duplicated when repetition adds no new fact

### Local Correctness Facts

- The public API name alone is not enough for bprop lookup.
- The Primitive from identity resolution is the actual search token.
- Dedicated grad dispatch and inline composition are distinct patterns.
- Backward operators should come from visible registered-body evidence.

### Worked Examples

#### Example 1: inline backward

For `AcosExt`, a bprop body such as:

```cpp
dx = ib->Neg(dout) * ib->Rsqrt(ib->Sub(ib->Tensor(1, ib->GetDtype(x)), ib->Square(x)));
```

gives:

- `AcosExt` -> `REG_BPROP_BUILDER("AcosExt")` -> inline composition ->
  `Neg, Mul, Rsqrt, Sub, Square`

#### Example 2: dedicated grad operator

If the bprop body calls:

```cpp
Emit("SoftmaxBackward", ...)
```

gives:

- `<primitive>` -> `REG_BPROP_BUILDER("<primitive>")` ->
  `Emit("SoftmaxBackward", ...)` -> dedicated grad path ->
  `SoftmaxBackward`

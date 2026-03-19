### VALIDATION CHECKLIST FOR ANSWERING MINT.* BACKWARD QUESTIONS

Use this checklist when a user asks about `mint.*` operators to avoid common mistakes.

## Question Type: "What is the backward operator of mint.X?"

### ☑️ Pre-Answer Validation (DO THIS FIRST!)

- [ ] **Did I read `mindspore/python/mindspore/mint/__init__.py`?**
  - If NO → STOP and read it first!
  - If YES → Continue

- [ ] **Did I identify the correct operator name?**
  - Example: `mint.acos` → `acos_ext` → `AcosExt` (NOT `ACos`)
  - Write down: mint.X uses operator `___________`

- [ ] **Did I search for the CORRECT operator in grad_math_ops.cc?**
  - ✅ Searched for: `REG_BPROP_BUILDER("AcosExt")`
  - ❌ Searched for: `REG_BPROP_BUILDER("ACos")` (WRONG!)

### ☑️ Answer Validation (BEFORE SENDING TO USER!)

- [ ] **Did I verify the operator name matches the mint import?**
  - mint/__init__.py import: `_________`
  - Operator searched: `_________`
  - Do they match? ⬜ YES ⬜ NO (If NO, fix it!)

- [ ] **Did I check if it's a dedicated backward operator or inline computation?**
  - ⬜ Dedicated operator (uses `ib->Emit("XxxGrad", ...)`)
  - ⬜ Inline computation (uses elementary ops like `Neg`, `Mul`, `Rsqrt`, etc.)

- [ ] **Did I list the ACTUAL operator calls (not just the math formula)?**
  - ✅ Listed: `Neg`, `Mul`, `Rsqrt`, `Sub`, `Square`
  - ❌ Only wrote: "dx = -dout / sqrt(1 - x²)"

- [ ] **Did I avoid checking PyTorch/ATen for the answer?**
  - ⬜ Yes, only checked MindSpore code
  - ⬜ No, I looked at PyTorch (DON'T DO THIS!)

### ☑️ Common Mistakes to Avoid

| Mistake | How to Avoid |
|---------|--------------|
| Assuming `mint.acos` uses `ACos` | ✅ Always check mint/__init__.py first |
| Returning `ACosGrad` for `mint.acos` | ✅ Verify AcosExt doesn't use dedicated grad op |
| Only giving mathematical formula | ✅ List actual operator calls (Neg, Mul, Rsqrt, etc.) |
| Checking PyTorch code | ✅ Only search MindSpore codebase |
| Skipping operator name verification | ✅ Read mint/__init__.py BEFORE searching backward |

### ☑️ Final Check Before Sending Answer

**Question**: What is the backward operator of mint.X?

**My answer includes**:
- [ ] Statement: "mint.X maps to operator `___________`"
- [ ] Backward type: ⬜ Dedicated operator ⬜ Inline computation
- [ ] List of actual operator calls (if inline)
- [ ] Reference to source file and line numbers
- [ ] NO mathematical formulas ONLY (must include operator names)

### Quick Self-Test

**Q**: User asks "what is backward operator of mint.acos?"

**Before answering, check**:
1. Did I read mint/__init__.py? → `acos_ext as acos`
2. What operator does mint.acos use? → `AcosExt` (NOT ACos!)
3. Did I search for `REG_BPROP_BUILDER("AcosExt")`? → Yes
4. What did I find? → Inline computation with Neg, Mul, Rsqrt, Sub, Square
5. Did I mention the operator name `AcosExt` in my answer? → Yes

If all checks pass → Answer is likely correct! ✅

If any check fails → Review and fix before answering! ❌

---

## Reference Files

- `./mint_operator_mappings.md` - Common mint.* operator name mappings
- `./how_to_find_op_name.md` - How to find the correct operator name
- `./how_to_write_backward_op.md` - Backward operator implementation guide

# Guardrails for HF Transformers Components Upgrade

## Scope Constraints

### Included
- Components in `transformers/src/transformers/` (excluding `models/`)
- Git tags for source and target versions
- File-level changes: Add, Delete, Modify, Rename

### Excluded
- Model-specific files in `models/` directory
- Test files
- Documentation files
- Build/configuration files at repo root

## Version Detection

### Auto-Detection
If source version not specified, the tool will:
1. Read `mindone/mindone/transformers/__init__.py`
2. Extract `__version__` variable
3. Convert to tag format (add 'v' prefix if needed)

Example:
```python
__version__ = "4.57.1"  # -> v4.57.1
```

### Manual Specification
User can specify both versions via command line:
- `--source v4.57.1` or `-s v4.57.1`
- `--target v5.0.0` or `-t v5.0.0` (required)

## Analysis Principles

### Principle 1: Same Version Comparison First
Always compare source transformers version with mindone current version to identify intentionally omitted files.

These files should NOT be added during upgrade, even if they appear in target version additions.

### Principle 2: Evaluate True New Files
For target version additions (status 'A'), only files that don't exist in source version are "true new" features.

Files that exist in source transformers but not in mindone are intentionally omitted.

### Principle 3: Context-Aware Priority
Priority should be determined based on:
- File's role in the architecture
- Impact on API compatibility
- Usage frequency in typical workflows
- MindONE's specific requirements and limitations

### Principle 4: Action Classification

For each file, determine:
- **Action**: What to do (Modify/Delete/Rename/Add)
- **Classification**: For additions (Recommended/Optional/Ignorable)
- **Priority**: How urgent (High/Medium/Low)
- **Rationale**: Why this decision was made

## Output Format

### Excel Structure
- Single sheet named "Upgrade Plan"
- Color-coded rows by action type
- Sorted by folder, then action priority

### Color Coding

**Tool-generated colors** (data collection stage):
| Action | Color | RGB | Meaning |
|--------|-------|-----|---------|
| Modify | Yellow | FFEB9C | File modified in target version (exists in mindone) |
| Delete | Red | FFC7CE | File deleted in target version (exists in mindone) |
| Rename | Blue | BDD7EE | File renamed in target version (old file exists in mindone) |
| Add | Dark Green | C6EFCE | True new feature (not in source transformers) |
| Add | Light Green | E2EFDA | Check against same-version comparison |

**Note**: Modify/Delete/Rename rows are automatically filtered to only include files that exist in mindone.

**After manual analysis** (update Action column for Additions):
| Action | Color | RGB |
|--------|-------|-----|
| Add (Recommended) | Dark Green | C6EFCE |
| Add (Optional) | Light Green | E2EFDA |
| Add (Ignorable) | Gray | D9D9D9 |

### File Naming
Output file naming convention:
```
upgrade_data_{source_version}_to_{target_version}.xlsx
```

Example: `upgrade_data_v4.57.1_to_v5.0.0.xlsx`

## Dependencies

Required Python packages:
```
openpyxl>=3.0.0
```

Required repositories:
- `transformers/` - Hugging Face transformers (with required git tags)
- `mindone/` - MindONE repository with mindone.transformers

## Error Handling

1. **Missing repositories**: Tool will fail with clear error message
2. **Missing git tags**: Run `git fetch --tags` in transformers repo
3. **Cannot detect mindone version**: Check `mindone/mindone/transformers/__init__.py` exists and contains `__version__`
4. **Permission errors**: Ensure write access to output directory

## Usage Examples

### Collect data with auto-detected source version
```bash
python collect_upgrade_data.py --target v5.0.0
```

### Collect data with specified versions
```bash
python collect_upgrade_data.py --source v4.57.1 --target v5.0.0
```

### Custom repository paths
```bash
python collect_upgrade_data.py     --source v4.57.1     --target v5.0.0     --mindone-path /path/to/mindone     --tf-path /path/to/transformers
```

## Analysis Guidelines

### High Priority Indicators
- Core API files (`__init__.py`)
- Model base classes (`modeling_*.py`)
- Training framework (`trainer*.py`)
- Generation utilities (`generation/*.py`)

### Medium Priority Indicators
- Framework integrations (`integrations/*.py`)
- Pipeline implementations (`pipelines/*.py`)
- Utility functions (`utils/*.py`)

### Low Priority / Ignorable Indicators
- CLI tools (`cli/*.py`) - mindone doesn't use CLI
- PyTorch-specific features not applicable to MindSpore
- Platform-specific code

### Addition Classification Guidelines

**Recommended when:**
- File provides core functionality
- Missing it would break API compatibility
- It's widely used across the codebase

**Optional when:**
- File provides specific feature support
- It's not critical to core operation
- Can be added later if needed

**Ignorable when:**
- File is CLI-related
- It's PyTorch-specific not applicable to MindSpore
- mindone explicitly doesn't support this feature

## Execution Guardrails

### Step sequencing

**Trigger**: expanding execution steps from the spreadsheet or broad directory lists.

**Default action**:
- Do not create execution steps directly from spreadsheet row order.
- Prioritize the minimum runnable path first:
  - `from_pretrained()`
  - minimal model load
  - minimal forward
  - `generate()`
- Stop broadening scope when the current blocker belongs to the runnable path.

**Forbidden**:
- Starting pipelines, trainer, integrations, or trailing utilities before the
  runnable path is stable.
- Treating "many modified files" as a reason to skip blocker ordering.

**Exception**:
- A direct dependency of the current runnable-path blocker may be pulled forward.

### Runbook creation

**Trigger**: a new step is about to start.

**Default action**:
- Classify the step with the scope framework before editing.
- Create a runbook only when the step is medium/major or otherwise runbook-worthy.
- Use a short checklist for small patches.

**Forbidden**:
- Pre-authoring all runbooks before execution starts.
- Creating a runbook for every step by default.
- Skipping step notes and relying on the runbook alone as the execution record.

**Exception**:
- An existing runbook for the same component may be extended instead of creating a new file.

### Device handling

**Trigger**: `.to(device)`, `.cuda()`, `torch.device`, `mps`, model-device helpers.

**Default action**:
- Remove the PyTorch device shim.
- Rewrite the path to the MindSpore execution form that does not depend on a
  runtime `device` argument.

**Forbidden**:
- Keeping a fake `model.device` compatibility layer.
- Carrying over `mps` or CUDA branches as dead compatibility code.

**Exception**:
- Preserve semantics that are not device shims, such as `register_buffer`.

### Unsupported PyTorch-only features

**Trigger**: accelerate, quantization, offload, distributed, PyTorch runtime-only hooks.

**Default action**:
- Mark the path as unsupported, deferred, or intentionally not followed.
- Record the downgrade explicitly in notes, runbooks, or closure summary.

**Forbidden**:
- Partial fake compatibility for `accelerate`, `device_map`, `bitsandbytes`,
  `torchao`, offload stacks, `dtensor`, tp/ep, or other unsupported runtime features.
- Pulling unsupported stacks into the critical path just to mirror upstream structure.

**Exception**:
- Only implement the path if the current MindOne upgrade explicitly targets that capability.

### Test migration and thresholds

**Trigger**: migrating tests or fixing UT/runtime mismatches.

**Default action**:
- Migrate fast UT by default.
- Classify the failure before editing.
- Keep numeric thresholds unchanged unless measurement proves they are the right fix.

**Forbidden**:
- Migrating slow or real-weight tests as the default new-model proof path.
- Using threshold changes as the first-line fix.
- Leaving threshold changes undocumented.

**Exception**:
- Slow or real-weight proof may be added only when the user explicitly asks.

### File normalization

**Trigger**: adding new upstream-adapted files or touching package initializers.

**Default action**:
- Add the MindOne provenance header to new upstream-adapted source files.
- Keep intentionally empty files, especially test package `__init__.py`, empty.

**Forbidden**:
- Adding header text to files that are intentionally required to stay empty.
- Leaving new upstream-adapted files without provenance normalization.

## Validation layering

**Trigger**: the shared-component path starts to pass local smoke checks.

**Default action**:
- Separate structural validation, UT sweep, real-weight validation, and
  new-model migration proof.
- Treat these as independent gates with separate records.

**Forbidden**:
- Treating one passing UT file as completion of the library upgrade.
- Treating real-weight validation as a replacement for UT sweep.

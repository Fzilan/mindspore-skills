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
python collect_upgrade_data.py \
    --source v4.57.1 \
    --target v5.0.0 \
    --mindone-path /path/to/mindone \
    --tf-path /path/to/transformers
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

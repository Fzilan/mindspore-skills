---
name: hf-transformers-components-upgrade-plan
description: Generate upgrade plan for mindone.transformers components between specified versions. Analyzes differences between Hugging Face transformers versions and creates comprehensive upgrade plans.
---

# HF Transformers Components Upgrade Plan

Analyze differences between Hugging Face transformers versions and generate comprehensive upgrade plans for mindone.transformers components.

## When to Use

- Comparing different transformers versions for component changes
- Analyzing mindone.transformers vs transformers differences
- Generating upgrade plans for mindone.transformers version migration
- Creating Excel reports of file-level changes

## Repositories

**Source Repository**: huggingface transformers (local clone)
- Path: `transformers/`
- Core: `transformers/src/transformers/`

**Target Repository**: mindone
- Path: `mindone/`
- Core: `mindone/mindone/transformers/`

## Instructions

### Step 1. Verify Repository Structure

Ensure both repositories are present:
```bash
ls transformers/src/transformers/  # HF transformers source
ls mindone/mindone/transformers/   # mindone transformers target
```

### Step 2. Determine Versions

#### Option A: Auto-detect (Default)
The tool will automatically detect:
- MindONE current version from `mindone/mindone/transformers/__init__.py`
- User provides target transformers version

#### Option B: Manual Specification
User specifies both versions:
- Source version: current mindone version (e.g., `v4.57.1`)
- Target version: desired transformers version (e.g., `v5.0.0`)

### Step 3. Collect Data

**IMPORTANT**: Both source and target versions are variables determined by the user or auto-detection. Do NOT assume fixed versions.

Execute the data collection tool:

```bash
# Option A: Auto-detect mindone version, specify target version only
# Source version will be auto-detected from mindone/__init__.py
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py --target <target_version>

# Option B: Manually specify both versions
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py --source <source_version> --target <target_version>

# Option C: Use short options
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py -s <source_version> -t <target_version>
```

**Version Format**: Use git tag format (e.g., `v4.57.1`, `v5.0.0`, `v4.46.0`)

**Examples**:
```bash
# Example 1: Auto-detect mindone version, upgrade to v5.0.0
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py --target v5.0.0

# Example 2: Explicitly upgrade from v4.57.1 to v5.0.0
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py --source v4.57.1 --target v5.0.0

# Example 3: Upgrade from v4.46.0 to v4.57.1
python skills/hf-transformers-components-upgrade-plan/tools/collect_upgrade_data.py -s v4.46.0 -t v4.57.1
```

This generates `upgrade_data_{source}_to_{target}.xlsx` containing filtered data:
- Header section with title, statistics, rules guide
- **Additions**: All added files (need manual verification if truly new)
- **Deletions**: Only files that exist in mindone (automatically filtered)
- **Modifications**: Only files that exist in mindone (automatically filtered)
- **Renames**: Only when old file exists in mindone (automatically filtered)
- Color-coded rows by action type
- Empty Priority column for manual filling
- Pre-filled Note column with guidance

**Note**: Delete/Modify/Rename actions are automatically filtered to only include files that actually exist in mindone.

### Step 4. Understand Excel Structure and Rules

Open the generated Excel file and understand the data structure before editing:

#### 4.1 Key Rule: Same-Version Comparison

**Critical Rule**: Files that exist in source transformers but NOT in mindone (same version) are intentionally omitted by mindone. These should NOT be added during upgrade.

Check the tool output for "Files only in transformers" count - this is your reference list.

#### 4.2 Understanding Row Colors

| Color | Action | Meaning |
|-------|--------|---------|
| Yellow (FFEB9C) | Modify | File modified in target version (exists in mindone) |
| Red (FFC7CE) | Delete | File deleted in target version (exists in mindone) |
| Blue (BDD7EE) | Rename | File renamed in target version (old file exists in mindone) |
| Dark Green (C6EFCE) | Add | True new feature (NOT in source transformers) |
| Light Green (E2EFDA) | Add | Need to check against same-version comparison |

**For Light Green Add rows**: Check if the file exists in the "Files only in transformers" list. If yes → mark as Ignorable. If no → evaluate as new feature.

#### 4.3 Priority Guidelines

When filling Priority column (Column E), use these guidelines:

**High Priority**: Core API files (`__init__.py`), model base classes (`modeling_*.py`), training framework (`trainer*.py`), generation utilities (`generation/*.py`)

**Medium Priority**: Framework integrations (`integrations/*.py`), pipelines (`pipelines/*.py`), utility functions (`utils/*.py`)

**Low Priority**: CLI tools (`cli/*.py`), platform-specific files, deprecated features

### Step 5. Fill in the Excel Document [REQUIRED - MUST NOT SKIP]

**⚠️ WARNING**: This step is MANDATORY. The generated Excel contains placeholder data that MUST be replaced with actual analysis. Do NOT skip this step.

**⚠️ IMPORTANT - Modification Restrictions**:
- **Column D (Action)**: Only modify "Add" rows to specify classification. **DO NOT change Modify/Delete/Rename to other types.**
- **Column E (Priority)**: Fill in for ALL rows.
- **Column F (Note)**: Replace auto-generated text with your analysis for ALL rows.
- **Row 5**: Replace placeholder with your transformers repo change summary.

**Edit the Excel file and complete ALL of the following:**

#### 5.1 Update Row 5 - Transformers Repo Change Summary

Replace the placeholder text in Row 5 with your actual analysis:
1. Review all additions/deletions/modifications between versions
2. Identify major patterns (e.g., "Removed TF/Flax support", "Added MoE integration")
3. Note breaking changes affecting mindone
4. Write a concise summary (2-3 sentences)

**Example**: "Transformers v5.0 removed TensorFlow and Flax support, added MoE integration, restructured CLI from 'commands/' to 'cli/' directory. Core modeling files saw significant refactoring."

#### 5.2 Fill Priority Column (Column E)

Fill Priority for **EVERY data row** (starting from row 10):
- **High** - Core API, training, generation files
- **Medium** - Integrations, pipelines, utilities
- **Low** - CLI, platform-specific, deprecated

Do not leave ANY cell in this column empty.

#### 5.3 Update Action Column for Additions (Column D)

**Restriction**: ONLY modify rows where Action is "Add". **DO NOT change Modify/Delete/Rename actions.**

For "Add" rows, update Action to specify classification:
- **Add(Recommended)** - True new features, core functionality
- **Add(Optional)** - Optional features, can be added later
- **Add(Ignorable)** - Files in same-version comparison list, CLI tools, PyTorch-specific

For Add(Ignorable) rows, change the row color to **Gray (D9D9D9)**.

#### 5.4 Update Note Column (Column F)

Replace ALL auto-generated notes with your detailed analysis:
- Why you set this priority
- For Additions: justification for Recommended/Optional/Ignorable classification
- Any dependencies or related files
- Warnings or special considerations

Every row must have a meaningful note, not the auto-generated placeholder.

### Step 6. Final Review [REQUIRED - MUST NOT SKIP]

⚠️ **WARNING**: This step is MANDATORY. Do NOT save the document until ALL items are checked.

**Verification Checklist** - ALL items must be checked before saving:
- [ ] **Row 5**: Contains actual transformers repo change summary (NOT placeholder text)
- [ ] **Column E (Priority)**: EVERY data row has High/Medium/Low filled (no empty cells)
- [ ] **Column D (Action)**: ALL Add rows updated to Recommended/Optional/Ignorable
- [ ] **Colors**: ALL Ignorable Add rows are colored Gray (D9D9D9)
- [ ] **Column F (Note)**: ALL rows have meaningful analysis (NOT auto-generated text)
- [ ] **File name**: Follows convention `upgrade_data_{source}_to_{target}.xlsx`

**CRITICAL**: If any item is unchecked, return to Step 5 and complete it. The Excel is NOT complete until all items are verified.

## Command Line Options

```
usage: collect_upgrade_data.py [-h] [-s SOURCE] -t TARGET [--mindone-path MINDONE_PATH] [--tf-path TF_PATH]

Collect upgrade data for mindone.transformers

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Source transformers version (e.g., v4.57.1). If not specified, auto-detected from mindone.
  -t TARGET, --target TARGET
                        Target transformers version (e.g., v5.0.0). Required.
  --mindone-path MINDONE_PATH
                        Path to mindone repository (default: mindone)
  --tf-path TF_PATH     Path to transformers repository (default: transformers)
```

## Output Summary

The data collection tool generates an Excel file with:

**File naming convention**:
```
upgrade_data_{source_version}_to_{target_version}.xlsx
```

Example: `upgrade_data_v4.57.1_to_v5.0.0.xlsx`

**Sheet structure**:

| Row | Content |
|-----|---------|
| 1-5 | Header section (title, statistics, rules, priority guide) |
| 6-8 | Instructions and empty rows |
| 9 | Column headers (Folder, Filename, Full Path, Action, Priority, Note) |
| 10+ | Data rows with color coding |

**Color Coding**:
| Action | Color | RGB |
|--------|-------|-----|
| Modify | Yellow | FFEB9C |
| Delete | Red | FFC7CE |
| Rename | Blue | BDD7EE |
| Add (True new feature) | Dark Green | C6EFCE |
| Add (Need to check) | Light Green | E2EFDA |
| Add (Ignorable) | Gray | D9D9D9 |

See Step 4-6 above for how to analyze and fill in the Excel document.

## References

- Guardrails: `references/guardrails.md`

## Notes

- The analysis excludes `models/` directory (model-specific files)
- The comparison uses git tags
- Files in source transformers but not in mindone are intentionally omitted
- Analysis should be done manually based on collected data
- Excel generation requires manual review and decision-making

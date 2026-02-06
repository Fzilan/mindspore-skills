---
name: hf-transformers-components-upgrade-migrate
description: Upgrade mindone.transformers public components to synchronize with a specified transformers version. Use when upgrading transformers version compatibility.
---

# HF Transformers Components Upgrade Migration

Upgrade the public components of mindone.transformers to be fully synchronized with a specified transformers version, ensuring functional and interface consistency while maintaining the stability of the mindone project.

## When to Use

- Upgrading mindone.transformers to match a new transformers library version
- Synchronizing public APIs, utilities, and configuration classes with upstream transformers
- Performing version migration for non-model components (excludes transformers/models/)
- Updating base classes, mixins, and shared utilities

## Repository

Source Repository: **huggingface transformers**: https://github.com/huggingface/transformers
- **core**: `transformers/src/transformers`
- **public components**: `transformers/src/transformers/` (excluding `models/`)

Target Repository: **mindone**: https://github.com/mindspore-lab/mindone
- **mindone.transformers core**: `mindone/mindone/transformers`
- **public components**: `mindone/mindone/transformers/` (excluding `models/`)

## Prerequisites

- The working directory contains the mindone project
- Git is installed and available
- Access to the transformers repository (local clone or remote)

## Instructions

### Step 1: Environment Preparation and Version Confirmation

1. Check the current working directory structure
   - Confirm the mindone project exists at the expected location
   - Verify the mindone/transformers directory structure

2. Check if the transformers project already exists
   - Look for a local transformers repository
   - If not present, clone from https://github.com/huggingface/transformers

3. Acquire or Update the Transformers Repository
   - Fetch the target version/tag from the transformers repository
   - Ensure the repository is at the correct commit/branch

### Step 2: User Input Validation and Processing

1. Receive User Input
   - Obtain the user-specified target transformers version (e.g., "v4.40.0")
   - Obtain the user-specified module/file list (optional)
   - Identify the current base version of mindone.transformers

2. Validate User Input
   - Check if the target version exists in the transformers repository
   - Validate the legitimacy of specified modules/files
   - Confirm if user-specified paths exist within the transformers project

3. Input Processing Decision
   - If user specifies specific modules/files → migrate those only (Targeted Mode)
   - If no modules specified → analyze all public component files (Full Upgrade Mode)

### Step 3: Version Comparison and Change Analysis

1. Determine Comparison Scope
   - Identify the transformers base version on which mindone.transformers is built
   - Use git tags, commit history, or version markers to determine base

2. Obtain differences between the two versions
   - Use Git commands to compare base version with target version
   - Focus on files outside the `transformers/models/` directory

3. Generate Change File List
   - **Exclusion Scope**: All content under `transformers/models/` directory
   - **Inclusion Scope**: 
     - Public API components
     - Utility functions and helpers
     - Configuration classes
     - Base classes and mixins
     - Processing utilities (if they don't depend on model-specific code)
     - Tokenization utilities (if applicable)

### Step 4: Dependency Analysis and Filtering

1. Work Mode Determination
   - **Targeted Module Migration Mode**: Process only user-specified modules/files
   - **Full Upgrade Mode**: Perform priority sorting before processing all changed files

2. Migration File List Determination
   - For Targeted Mode: Use the user-provided list directly
   - For Full Upgrade Mode:
     - Sort files by dependency order (base classes first)
     - Identify files with no dependencies (can be migrated independently)
     - Identify files with dependencies (must wait for dependencies)
     - Create a migration priority list

### Step 5: Migration Execution Preparation

1. For each file in the migration list:
   - Analyze the changes between versions
   - Identify API changes, new methods, deprecated methods
   - Note any breaking changes

2. Create migration plan per file:
   - Map old APIs to new APIs
   - Identify MindSpore-specific adaptations needed
   - Document any compatibility shims required

### Step 6: Reference Skills /hf-transformers-migrate for File Migration

For each file requiring migration:

1. **Copy the source file** from transformers to mindone (if new) or identify existing file

2. **Apply auto-conversion** using the tools from hf-transformers-migrate:
   ```bash
   python skills/hf-transformers-migrate/tools/auto_convert.py \
     --src_file path/to/file.py --inplace
   ```
   <MUST> Run auto_convert script before any manual edits. </MUST>

3. **Manual fixes** following the patterns from hf-transformers-migrate:
   - Structural and API changes (torch.nn.Module → mindspore.nn.Cell, etc.)
   - Device handling removal
   - Import and decorator adjustments
   - Tensor and shape handling

4. **Update registration and exports** if the file affects public APIs:
   - Update `mindone/mindone/transformers/__init__.py`
   - Update any auto-configuration files
   - Ensure proper exports in `__init__.py` files

### Step 7: Verification and Testing

1. **Import verification**
   - Ensure all migrated modules import cleanly
   - Check for circular dependencies

2. **API compatibility check**
   - Verify public API signatures match expected transformers version
   - Check for missing methods or attributes

3. **Integration testing**
   - Run existing tests to ensure no regressions
   - Test with model loading if applicable

## Guardrails

- **DO NOT migrate** any files under `transformers/models/` directory
- **DO migrate** public components, utilities, base classes, and configuration classes
- Keep changes minimal and focused on version synchronization
- Maintain backward compatibility where possible
- Document any breaking changes

## References

- Environment and setup: `references/env.md`
- Guardrails and constraints: `references/guardrails.md`
- Migration tools: Use `skills/hf-transformers-migrate/tools/`

## Output

- List of files migrated and changes made
- Version compatibility notes
- Any breaking changes or deprecated APIs
- Suggested tests to run
- Migration summary report

## Done Criteria

- All targeted public components are synchronized with the specified transformers version
- Modules import cleanly without errors
- No regressions in existing functionality
- Documentation updated with version compatibility info

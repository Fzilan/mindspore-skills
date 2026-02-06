# Environment Notes

## MindOne setup
```bash
# Install from source (recommended for development)
cd mindone
pip install -e .

# Install with optional dependencies
pip install -e ".[dev]"  # All dev tools
pip install -e ".[lint,tests]"  # Linting and testing only
pip install -e ".[training]"  # Training utilities
```

## Transformers setup
```bash
cd transformers
pip install -e .
```

## Version Comparison Commands

### Check current version
```bash
cd transformers
git describe --tags --abbrev=0  # Get latest tag
git log --oneline -1  # Get current commit
```

### Compare versions
```bash
# Get list of changed files between two versions
git diff --name-only <base-version> <target-version>

# Get diff for specific file
git diff <base-version> <target-version> -- <file-path>

# Get list of changed files excluding models directory
git diff --name-only <base-version> <target-version> | grep -v "^src/transformers/models/"
```

## Code quality & formatting

**transformers/** uses a Makefile:
```bash
# Format code (run on feature branches)
make style                    # Format all files with ruff
make modified_only_fixup      # Format only modified files (auto-detects branch)

# Check code quality
make quality                  # Run all linting checks

# Repository consistency checks
make repo-consistency         # Validate copies, dummies, inits, configs, etc.

# Auto-generate code
make autogenerate_code        # Update dependency tables

# Fix everything
make fixup                    # Runs modified_only_fixup + extra_style_checks + autogenerate_code + repo-consistency

# Fix marked code copies
make fix-copies               # Update marked code sections across files
```

**mindone/** uses pyproject.toml configuration:
- Formatting: Black (line length 120)
- Import sorting: isort with MindSpore-specific sections

## Testing

**mindone/**:
```bash
# Run all the transformers tests with pytest
pytest tests/transformers_tests/ -v

# Run specific module tests
pytest tests/transformers_tests/test_configuration_utils.py -v
pytest tests/transformers_tests/test_modeling_utils.py -v
```

## Common Migration Commands

### Auto-convert single file
```bash
python skills/hf-transformers-migrate/tools/auto_convert.py \
  --src_file path/to/file.py --inplace
```

### Install auto-convert requirements
```bash
pip install -r skills/hf-transformers-migrate/tools/requirements.txt
```

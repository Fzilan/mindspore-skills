# Guardrails and expectations

## Scope and precedence
- This file contains repo-specific rules for the current target repo.
- If any rule conflicts with SKILL.md, follow this file.

## Scope Limitations
- **DO NOT migrate** any files under `transformers/models/` directory
- **DO migrate** public components including:
  - Base classes and mixins
  - Configuration classes and utilities
  - Model utilities (modeling_utils.py, etc.)
  - Processing utilities (if not model-specific)
  - Tokenization utilities (if applicable)
  - Public API exports

## Guardrails
- Avoid custom compatibility wrappers unless required.
- Use diff-based insertion when updating auto maps.
- Keep changes minimal and aligned with existing MindOne patterns.
- `register_buffer` is supported in MindSpore; do not remove it as part of device-handling cleanup.
- Model coding standards:
  - Import MindSpore as `import mindspore` (avoid `import mindspore as ms`).
  - Use `from mindspore import nn` and define modules as `nn.Cell`.

## Version Upgrade Specific Rules
- Maintain backward compatibility where possible
- Document all breaking changes
- Update version compatibility notes in documentation
- Ensure all public APIs remain functional after upgrade
- Test with existing models to ensure no regressions

## Response expectations
- List reference files consulted.
- Summarize edits and note any risks or TODOs.
- Suggest next tests when appropriate.
- Provide version compatibility matrix.

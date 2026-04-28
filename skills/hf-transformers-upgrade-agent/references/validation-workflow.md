# Validation Workflow

Validation should happen in layers.

## Structural validation

Use lightweight checks first:

- `python -c "import ..."`
- export checks
- grep-based guardrails
- py_compile for newly added or heavily edited files

## Targeted validation reports

Write focused validation documents when a core file or core path needs its own
summary, for example:

- `modeling_utils.py`
- import verification
- major public stack transitions

Validation reports should summarize what was checked and what remains outside
scope.

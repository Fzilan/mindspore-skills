# Planning

Use the planning stage to generate the file-level upgrade spreadsheet.

Inputs:

- local `mindone` repository
- local `transformers` repository
- source version tag
- target version tag

Required action:

- run `scripts/collect_upgrade_data.py`

Primary output:

- `upgrade_data_{source}_to_{target}.xlsx`

Planning is complete only when the spreadsheet exists and is ready for manual
classification.

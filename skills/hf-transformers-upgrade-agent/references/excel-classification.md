# Excel Classification

The spreadsheet is a work pool, not an execution order.

Required classification tasks:

- replace the row-5 placeholder with a real repo change summary
- fill Priority for every row
- classify every addition as:
  - `Add(Recommended)`
  - `Add(Optional)`
  - `Add(Ignorable)`
- replace auto-generated Note text with actual analysis

Classification rules:

- same-version omissions in MindOne are not automatically “must-add”
- CLI and clear PyTorch-only additions are usually ignorable
- additions that unblock core API compatibility or common workflows are usually
  recommended
- uncertain additions should still be classified, not left blank

Do not leave the spreadsheet half-complete before execution starts.

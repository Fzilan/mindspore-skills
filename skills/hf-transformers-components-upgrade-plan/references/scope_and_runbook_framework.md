# Scope And Runbook Framework (Small Patch vs. Refactor Upgrade)

This document defines a repeatable way to (1) estimate the change magnitude for a transformers upgrade, (2) decide whether a component needs a dedicated runbook, and (3) standardize the runbook structure so both developers and agents can execute it reliably.

## 1. Problem

For a given version jump (e.g. `v4.57.1 -> v5.0.0`), some files are:
- small patches (imports, renamed symbols, minor API adjustments)
- medium refactors (one file, multiple call sites, limited new modules)
- major restructures (logic moved to new modules, new abstractions, removed features)

A single "upgrade plan" (Excel file list) is necessary but not sufficient for major restructures. Major restructures require an explicit, ordered execution plan (runbook) that enumerates the dependency chain and the minimal compatible surface area.

## 2. Inputs (What You Always Have)

- Upgrade spreadsheet: `upgrade_data_{source}_to_{target}.xlsx` (file-level changes + priority)
- Upstream git diff between versions (source -> target)
- Current MindONE implementation of the same component

## 3. Magnitude Classification (Heuristics)

Use these signals to classify each target file into one of the buckets below.

### 3.1 Metrics To Collect (fast, automatable)

File-level:
- `git diff --stat <src>..<tgt> -- path/to/file.py`
- `git diff <src>..<tgt> -- path/to/file.py | head` (detect rewrites)
- `git blame` hotspots are optional; do not block on them.

Repo-level (for dependency chain):
- `git diff --name-status <src>..<tgt> -- transformers/src/transformers/`
- `rg -n "from .* import .*<symbol>"` on MindONE for import/callers

### 3.2 Buckets

Small Patch (no runbook; short checklist is enough)
- Diff stats: low churn (e.g. < ~200 LOC net changes; no large block rewrite)
- No new module introduced as a required dependency
- No feature removal affecting this component (e.g. TF/Flax removal not touched)
- No signature-level breaking changes that ripple to many call sites

Medium Refactor (runbook recommended if component is core or widely imported)
- Diff stats: moderate churn (e.g. ~200-1000 LOC, multiple blocks rewritten)
- Some new helper module(s) introduced upstream, but can be stubbed or inlined
- A few API changes that require coordinated changes in 2-5 MindONE files

Major Restructure (runbook required)
- Diff stats: high churn (e.g. > ~1000 LOC, "rewrite" vibe; lots of deletions/additions)
- New upstream modules become the new "center of gravity" (e.g. logic split out)
- Deletions of entire feature paths (common examples in v5: TF/Flax removal, URL download helpers removed)
- Many new abstractions (new dataclasses, new return structures, new logging/reporting)
- The file is core and widely depended upon (e.g. `modeling_utils.py`, generation core, trainer core)

Notes:
- Thresholds are guidance; "core-ness" increases sensitivity. A 200 LOC change in `modeling_utils.py` is not "small".
- If a file is marked `High` priority in the spreadsheet and shows medium-or-higher churn, treat it as runbook-worthy.

## 4. Decision Rule: When To Write A Runbook

Write a dedicated runbook if ANY is true:
- The change is Major Restructure.
- The change is Medium Refactor AND the file is a core entrypoint (`modeling_utils.py`, `generation/utils.py`, `trainer.py`, `__init__.py` exports).
- The file imports upstream symbols that were removed/moved (import breakage risk is high).
- The component is a "hub" (many internal importers in MindONE).

Otherwise: use a "patch checklist" (imports + small behavioral alignment + minimal validation note).

## 5. Runbook Structure (Standard Template)

Keep runbooks short, executable, and stable under iteration. Use an "S1..Sn" step graph with clear done-conditions.

## 5.0 Runbook Examples

If you are unsure how detailed a runbook should be, start from an existing example and edit it.

- Example (major restructure, core component): `skill/hf-transformers-components-upgrate-plan/examples/runbook_modeling_utils.md`
- Skeleton/template (copy & fill): `skill/hf-transformers-components-upgrate-plan/examples/runbook_.md`

### 5.1 Runbook Header
- Inputs (source/target tags, spreadsheet name)
- Outputs (new files, modified files)
- Upgrade Graph: `S1 -> S2 -> ... -> Sn`

### 5.2 Dependency Chain Section ("Upgrade Graph Support")

For the target component, enumerate:
- Upstream file chain: new modules added/required by upstream
- MindONE reverse deps: who imports/calls this component
- External deps: `transformers.utils.*`, `huggingface_hub`, `safetensors`, etc.

Minimum commands:
- Upstream: `git diff --name-status <src>..<tgt> -- transformers/src/transformers/`
- Reverse deps: `rg -n "from .*modeling_utils import|import .*modeling_utils" mindone/mindone/transformers`

### 5.3 Steps Section (S1..Sn)

Each step must contain:
- Files: explicit list of files to change (add/modify)
- Change: 3-8 bullet items max (what to implement/remove/rename)
- Not Supported: explicit degradations (if any)
- Done when: 1-3 objective checks (import succeeds, symbol exists, grep-based guardrail passes)

Prefer objective checks that do not require network / heavyweight execution:
- `python -c "import X"` (import-level)
- `rg -n "<forbidden_symbol>" file.py` (guardrails)
- `python -c "from pkg import symbol"` (export-level)

### 5.4 Checklist Section

Split into:
- Structural (files exist, imports stable)
- API semantics (key defaults, deprecated args normalization)
- Consolidation (single entrypoints, no duplicated loading logic)

### 5.5 Guardrails Section (Automatable)

List:
- banned imports/symbols
- must-exist modules + exported symbols
- single-entrypoint requirements (e.g. one "core load" function call)

## 6. Patch Checklist Structure (For Small Changes)

When change is "Small Patch", do NOT write a runbook; use a short checklist:
- imports updated (moved/removed symbols)
- deprecated args normalized (if applicable)
- minimal behavior alignment note
- reverse deps smoke import check

## 7. Example: Why `modeling_utils.py` Typically Needs A Runbook In v5

Typical v5 signals:
- high churn in upstream `modeling_utils.py`
- loading logic split into new modules (e.g. `core_model_loading.py`)
- removed helpers/symbols (URL download helpers, TF/Flax-related constants/paths)

Conclusion: treat as Major Restructure -> runbook required.

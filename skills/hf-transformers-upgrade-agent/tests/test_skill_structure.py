from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"


def test_skill_markers_present():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "## Workflow" in text
    assert "## Stage 1. Planning and Classification" in text
    assert "## Stage 2. Tracker Bootstrap" in text
    assert "## Stage 3. Step Sequencing" in text
    assert "## Stage 4. Step Execution Loop" in text
    assert "## Stage 5. Validation and Testing" in text
    assert "## Stage 6. Closure and Proof" in text


def test_reference_and_script_files_exist():
    for rel in (
        "references/planning.md",
        "references/excel-classification.md",
        "references/step-sequencing.md",
        "references/scope_and_runbook_framework.md",
        "references/scope_and_runbook_framework.zh.md",
        "references/tracker-workflow.md",
        "references/execution-records.md",
        "references/validation-workflow.md",
        "references/testing-workflow.md",
        "references/closure-checklist.md",
        "references/guardrails.md",
        "references/upgrade-rules.md",
        "references/case-study-v4.57.1-to-v5.0.0.md",
        "examples/runbook_modeling_utils.md",
        "scripts/collect_upgrade_data.py",
        "scripts/bootstrap_upgrade_tracker.py",
        "scripts/bootstrap_runbook.py",
        "scripts/bootstrap_step_note.py",
        "scripts/summarize_upgrade_state.py",
    ):
        assert (SKILL_ROOT / rel).exists(), rel

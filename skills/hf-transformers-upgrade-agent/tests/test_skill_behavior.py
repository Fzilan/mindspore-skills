from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"


def test_skill_keeps_excel_as_work_pool_not_execution_order():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "Treat the spreadsheet as a work pool, not as the execution order." in text
    seq = (SKILL_ROOT / "references" / "step-sequencing.md").read_text(encoding="utf-8")
    assert "Do not create steps directly from spreadsheet row order." in seq
    assert "`from_pretrained()`" in seq
    assert "`generate()`" in seq


def test_runbooks_are_created_on_demand():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "Do not pre-author all runbooks at the start." in text
    assert "Do not create a runbook for every step by default." in text
    framework = (SKILL_ROOT / "references" / "scope_and_runbook_framework.md").read_text(encoding="utf-8")
    assert "Major Restructure" in framework
    assert "When To Write A Runbook" in framework


def test_skill_keeps_main_prompt_concise_and_stage_routed():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert "Load only the references needed by the current stage:" in text


def test_hard_rules_require_strict_step_accounting_and_fast_proof_only():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "Every execution step must explicitly record step target, blocker role, scope" in text
    assert "A step without both a tracker update and a step record is incomplete." in text
    assert "migrate fast UT by default" in text


def test_guardrails_cover_device_quantization_and_threshold_defaults():
    guardrails = (SKILL_ROOT / "references" / "guardrails.md").read_text(encoding="utf-8")
    assert "Keeping a fake `model.device` compatibility layer." in guardrails
    assert "Partial fake compatibility for `accelerate`, `device_map`, `bitsandbytes`" in guardrails
    assert "Using threshold changes as the first-line fix." in guardrails


def test_closure_requires_new_model_proof_and_migrate_agent_reuse():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "reuse `migrate-agent`" in text
    closure = (SKILL_ROOT / "references" / "closure-checklist.md").read_text(encoding="utf-8")
    assert "new-model migration proof" in (SKILL_ROOT / "references" / "testing-workflow.md").read_text(
        encoding="utf-8"
    )
    assert "`__version__`" in closure


def test_templates_force_blocker_and_threshold_fields():
    step_template = (SKILL_ROOT / "scripts" / "bootstrap_step_note.py").read_text(encoding="utf-8")
    assert "## Runnable-Path Blocker" in step_template
    assert "## Threshold Touched" in step_template
    runbook_template = (SKILL_ROOT / "scripts" / "bootstrap_runbook.py").read_text(encoding="utf-8")
    assert "## Why This Runbook Exists" in runbook_template
    assert "threshold changes allowed:" in runbook_template

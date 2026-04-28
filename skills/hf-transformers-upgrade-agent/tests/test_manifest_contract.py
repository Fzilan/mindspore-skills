from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = SKILL_ROOT / "skill.yaml"
SKILL = SKILL_ROOT / "SKILL.md"

def _manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def test_manifest_contract_fields_present():
    text = _manifest_text()
    assert 'name: "hf-transformers-upgrade-agent"' in text
    assert 'display_name: "HF Transformers Upgrade"' in text
    assert 'version: "0.1.0"' in text
    assert 'type: "manual"' in text
    assert 'path: "SKILL.md"' in text
    assert 'network: "none"' in text
    assert 'filesystem: "workspace-write"' in text


def test_manifest_declares_upgrade_inputs_and_outputs():
    text = _manifest_text()
    assert 'name: "source_version"' in text
    assert 'name: "target_version"' in text
    assert 'name: "mode"' in text
    assert 'choices: ["plan-only", "execute", "execute-and-validate"]' in text
    assert 'name: "upgrade_plan"' in text
    assert 'name: "tracker"' in text
    assert 'name: "runbook_set"' in text
    assert 'name: "validation_summary"' in text


def test_skill_describes_upgrade_workflow():
    text = SKILL.read_text(encoding="utf-8")
    assert "# HF Transformers Upgrade Agent" in text
    assert "1. `planning-and-classification`" in text
    assert "2. `tracker-bootstrap`" in text
    assert "3. `step-sequencing`" in text
    assert "4. `step-execution-loop`" in text
    assert "5. `validation-and-testing`" in text
    assert "6. `closure-and-proof`" in text


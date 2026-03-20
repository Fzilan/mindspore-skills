import re
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_DIR = SKILL_ROOT / "references"
SKILL_MD = SKILL_ROOT / "SKILL.md"
SKILL_YAML = SKILL_ROOT / "skill.yaml"
ROOT_AGENTS = SKILL_ROOT.parents[1] / "AGENTS.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_yaml(path: Path):
    return yaml.safe_load(read_text(path))


def test_skill_references_only_ascend_compat():
    content = read_text(SKILL_MD)
    assert "references/ascend-compat.md" in content
    assert "references/nvidia-compat.md" not in content


def test_ascend_reference_exists_and_has_required_sections():
    path = REFERENCES_DIR / "ascend-compat.md"
    content = read_text(path)
    assert path.exists()
    assert "Driver / Firmware / CANN Matrix" in content
    assert "MindSpore on Ascend" in content
    assert "PyTorch + torch_npu on Ascend" in content
    assert "Official Installation Guides" in content


def test_ascend_reference_has_torch_npu_rows():
    content = read_text(REFERENCES_DIR / "ascend-compat.md")
    rows = re.findall(r"^\|\s*2\.\d+\.x\s*\|\s*2\.\d+\.x\s*\|", content, re.MULTILINE)
    assert len(rows) >= 3, f"Expected >=3 torch/torch_npu matrix rows, found {len(rows)}"


def test_skill_no_longer_mentions_gpu_or_nvidia_path():
    content = read_text(SKILL_MD)
    assert "This skill is Ascend-only." in content
    assert "Nvidia or CUDA environment setup" in content
    assert "remote SSH workflows" in content
    assert "## Remote Environments" not in content
    assert "### Step 1 — Detect Hardware" not in content


def test_skill_requires_uv_before_python_installs():
    content = read_text(SKILL_MD)
    assert "All Python package checks and installs happen only after `uv` is confirmed" in content
    assert "Never install Python packages into the system interpreter." in content


def test_skill_forbids_auto_installing_driver_and_cann():
    content = read_text(SKILL_MD)
    assert "You MUST NOT auto-install or upgrade:" in content
    assert "- NPU driver" in content
    assert "- CANN toolkit" in content


def test_skill_requires_confirming_uv_env_choice_and_python_version():
    content = read_text(SKILL_MD)
    assert "ask the user whether to reuse an existing environment or create a new one" in content
    assert "ask which Python version to use" in content


def test_skill_stops_before_package_install_when_system_layer_fails():
    content = read_text(SKILL_MD)
    assert "If driver or CANN is not installed or unusable:" in content
    assert "- stop before `uv` package remediation" in content
    assert "If sourcing fails, report it as a system-layer failure and do not continue to" in content


def test_skill_reports_both_framework_paths():
    content = read_text(SKILL_MD)
    assert "### C2. MindSpore path" in content
    assert "### C3. PTA path (`torch` + `torch_npu`)" in content
    assert "If both framework paths are unhealthy, report both independently" in content


def test_skill_documents_standard_reporting_contract():
    content = read_text(SKILL_MD)
    assert "runs/<run_id>/out/" in content
    assert "report.json" in content
    assert "report.md" in content
    assert "meta/env.json" in content
    assert "meta/inputs.json" in content


def test_manifest_matches_ascend_only_scope_and_permissions():
    manifest = read_yaml(SKILL_YAML)
    assert manifest["permissions"]["network"] == "required"
    assert manifest["permissions"]["filesystem"] == "workspace-write"
    assert manifest["composes"] == []
    assert "torch_npu" in manifest["tags"]
    assert "nvidia" not in manifest["tags"]
    choices = manifest["inputs"][0]["choices"]
    assert choices == ["local"]


def test_manifest_declares_uv_and_framework_inputs():
    manifest = read_yaml(SKILL_YAML)
    input_names = {item["name"] for item in manifest["inputs"]}
    assert {"target", "frameworks", "task_type", "uv_env_mode", "python_version"} <= input_names


def test_root_agents_exposes_setup_agent():
    content = read_text(ROOT_AGENTS)
    assert "| setup-agent | skills/setup-agent/ |" in content
    assert "**setup-agent**" in content
    assert "torch_npu" in content

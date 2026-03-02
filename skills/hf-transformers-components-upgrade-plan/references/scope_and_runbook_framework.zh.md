# 范围与 Runbook 框架（小改动 vs. 重构升级）

本文档给出一套可复用的方法，用于：(1) 评估 Transformers 升级的改动量级；(2) 决定某个组件是否需要单独 Runbook；(3) 统一 Runbook 的结构，方便开发者与 Agent 按步骤执行。

## 1. 问题定义

同一次版本跨度（例如 `v4.57.1 -> v5.0.0`）里，不同文件的改动性质可能完全不同：
- 小改动：import 调整、符号改名、参数默认值变化、少量逻辑修补
- 中等重构：单文件多处改写，或引入少量新模块，影响有限的调用点
- 大重构：核心逻辑被拆分到新模块、引入新抽象、删除整条能力路径（breaking change）

升级计划（Excel 的文件列表）是必要输入，但对于“大重构”不够用。大重构需要额外产出**可执行 Runbook**：明确依赖链、最小兼容面、以及按顺序的落地步骤。

## 2. 固定输入（每次都会有）

- 升级计划表：`upgrade_data_{source}_to_{target}.xlsx`（文件级 Add/Delete/Modify/Rename + 优先级）
- 上游版本差异：upstream `git diff`（source -> target）
- MindONE 当前同名组件实现（用于对照与二次修改点提取）

## 3. 量级划分（可操作的经验规则）

对每个目标文件，建议收集下列“快指标”，然后归类为：小改动 / 中等重构 / 大重构。

### 3.1 快指标（可自动化、耗时低）

文件级：
- `git diff --stat <src>..<tgt> -- path/to/file.py`
- `git diff <src>..<tgt> -- path/to/file.py | head`（判断是否接近“重写”）

仓库级（用于依赖链）：
- `git diff --name-status <src>..<tgt> -- transformers/src/transformers/`
- MindONE 反向依赖：`rg -n "<import-or-symbol>" mindone/mindone/transformers`

> 备注：`git blame`/热点分析可选，不要作为阻塞项。

### 3.2 三类改动桶（Buckets）

小改动（通常不需要 Runbook；用短 checklist 即可）
- diff 变更量小（例如 < ~200 行级别的 churn；没有大段逻辑重写）
- 没有引入“必须新增”的新模块依赖
- 没有删除整条能力路径（例如 TF/Flax 被移除但该文件不涉及）
- 不引发大范围签名/返回结构变化（不会波及大量调用点）

中等重构（若是核心文件或被广泛 import，建议写 Runbook）
- diff 变更量中等（例如 ~200-1000 行 churn，多处块级改写）
- 引入少量新 helper 模块（可以先 stub/裁剪实现）
- 需要协调修改 2-5 个 MindONE 文件才能对齐主链路

大重构（必须 Runbook）
- diff 变更量大（例如 > ~1000 行 churn，整体呈现“重写感”）
- 上游把逻辑拆到新模块，新的模块成为“重心”（center of gravity）
- 删除整条能力路径（常见：v5 移除 TF/Flax；移除 URL 下载 helper 等）
- 引入大量新抽象（dataclass、统一返回结构、loading report、转换链等）
- 该文件是核心枢纽（MindONE 内部大量 import/继承/调用：如 `modeling_utils.py`、generation 核心、trainer 核心等）

注意：
- 阈值是指导值；“核心程度”会放大风险：即使只有 200 行改动，`modeling_utils.py` 也可能需要 Runbook。
- 若 Excel 中优先级是 `High` 且变更量达到中等及以上，建议直接按 Runbook 路径走。

## 4. 何时需要写 Runbook（决策规则）

满足以下任意条件就写 Runbook：
- 判定为“大重构”
- 判定为“中等重构”且文件是核心入口（例如 `modeling_utils.py`、`generation/utils.py`、`trainer.py`、`__init__.py` 的导出）
- 该文件 import 的上游符号在目标版本中被删除/迁移（ImportError 风险高）
- 该文件是 MindONE 内部“枢纽”（很多反向依赖）

否则：写“补丁 checklist”（imports + 小语义对齐 + 最小自检）即可。

## 5. Runbook 标准结构（模板）

Runbook 的目标是“可执行、短、稳定”。推荐使用 `S1..Sn` 步骤图，并且每步都有客观 Done 条件。

## 5.0 Runbook 样例

如果你不确定 Runbook 需要写到什么粒度，建议直接从现有样例复制修改。

- 样例（大重构/核心组件）：`skill/hf-transformers-components-upgrate-plan/examples/runbook_modeling_utils.md`
- 空模板（复制后填写）：`skill/hf-transformers-components-upgrate-plan/examples/runbook_.md`

### 5.1 Runbook 头部
- Inputs：source/target tags、Excel 名称
- Outputs：新增/修改文件清单
- Upgrade Graph：`S1 -> S2 -> ... -> Sn`

### 5.2 依赖链（支撑 Upgrade Graph）

最少要列清楚：
- Upstream 文件链：上游新增/拆分出的关键模块（哪些变成必依赖）
- MindONE 反向依赖：谁 import/调用该组件（改动面）
- 外部依赖：`transformers.utils.*`、`huggingface_hub`、`safetensors` 等

最低命令集：
- Upstream：`git diff --name-status <src>..<tgt> -- transformers/src/transformers/`
- 反向依赖：`rg -n "from .*modeling_utils import|import .*modeling_utils" mindone/mindone/transformers`

### 5.3 步骤（S1..Sn）

每一步必须包含：
- Files：明确列出要改/要新增的文件
- Change：3-8 条以内，写“要做什么”（可执行的动词）
- Not Supported：明确降级/不实现项（避免误用）
- Done when：1-3 条客观检查（import 成功、符号存在、grep guardrail 通过）

推荐 Done when 采用轻量、无需网络/重执行的检查：
- `python -c "import X"`（import-level）
- `python -c "from pkg import symbol"`（export-level）
- `rg -n "<forbidden_symbol>" file.py`（guardrails）

### 5.4 Checklist（交付验收清单）

建议分三类：
- Structural：文件存在、导入稳定
- API Semantics：关键默认值/弃用参数归一、行为对齐点
- Consolidation：关键路径是否收敛到单一入口（避免逻辑散落）

### 5.5 Guardrails（可自动化）

列出：
- 禁止出现的 imports/symbol（黑名单）
- 必须存在的模块与导出符号（白名单）
- 必须满足的“单入口”约束（例如加载逻辑只能从某个函数进入）

## 6. 小改动的补丁 Checklist 模板（无需 Runbook）

当判定为“小改动”，建议使用短 checklist：
- imports 更新（符号迁移/删除）
- deprecated 参数归一（如 `use_auth_token -> token`）
- 小语义对齐说明（默认值、fallback 行为）
- 反向依赖最小 import 自检（确保不炸）

## 7. 示例：为什么 v5 的 `modeling_utils.py` 通常需要 Runbook

典型信号：
- 上游 `modeling_utils.py` diff churn 很大
- 加载逻辑被拆分到新模块（例如 `core_model_loading.py`）
- 多条能力路径被移除（TF/Flax、URL 下载 helper 等）

结论：按“大重构”处理 -> 必须 Runbook。

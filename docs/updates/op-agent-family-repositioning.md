# op-agent Family Repositioning

## 1. 目标

本次重新定位的目标不是继续围绕已有零散 skill 做局部修补，而是先建立一套**形式上完全正交、命名统一、可扩展**的 operator skill taxonomy。

该 taxonomy 需要满足：

- 顶层命名反映架构抽象，而不是当前某个具体技术栈
- 能覆盖 CPU / GPU / NPU 三类后端
- 能覆盖 Native / Plugin 两类接入方式
- 当前尚未实现的格子允许作为 placeholder 保留
- 当前已存在的 skill 能逐步迁移进这套 taxonomy

## 2. 核心定位

`op-agent` 家族整体重新定位为两层结构：

- 导航层：负责判断应进入哪个原子能力格子
- 原子能力层：负责回答“这个格子的算子应该怎么写”

这里的关键变化是：

- 不再按零散技术名词组织顶层 taxonomy
- 不再让某个具体技术路径直接定义整体架构
- 先建立完整矩阵，再逐步补齐每个格子的实现能力

## 3. 二层架构

### 3.1 导航层

- `op-agent`

职责：

- 接收上游 analysis agent 传来的 handoff
- 判断目标 backend
- 判断更适合 Native 还是 Plugin 接入
- 选择唯一目标 builder

边界：

- 不直接写实现代码
- 不承担具体 kernel 开发
- 不承担完整 PTA 深挖和 delivery 流程

### 3.2 原子能力层

builder 只提供**特定后端 + 特定接入方式**的实现能力。

这里的“原子能力”指的是：

- 明确知道目标 backend
- 明确知道接入范式是 Native 还是 Plugin
- builder 专注回答该路径下“怎么写”

## 4. 正交接入矩阵

operator skill family 采用如下 2x3 正交矩阵作为目标 taxonomy：

| Integration Type | CPU | GPU | NPU |
| --- | --- | --- | --- |
| Native | `cpu-native-builder` | `gpu-native-builder` | `npu-native-builder` |
| Plugin | `cpu-plugin-builder` | `gpu-plugin-builder` | `npu-plugin-builder` |

解释：

- `Native`：在 MindSpore 内部仓库中实现并集成内核能力
- `Plugin`：通过外部三方库或外部接入路径完成算子能力接入

注意：

- 该矩阵是**目标 taxonomy**
- 并不意味着 phase 1 所有格子都已具备成熟实现
- 未实现格子可以显式保留为 placeholder

## 5. 标准命名规范

所有 builder 统一采用：

`{backend}-{integration_type}-builder`

其中：

- `backend`：`cpu` / `gpu` / `npu`
- `integration_type`：`native` / `plugin`

该命名规范的目的：

- 保证 taxonomy 对称
- 保证未来扩展时命名规则稳定
- 避免让 ACLNN、ATen、cuDNN 等具体技术名直接污染顶层分类

## 6. 目标 Taxonomy

### 6.1 Navigator

- `op-agent`

说明：

- 继续保留 `agent` 命名，以便与 `setup-agent`、`failure-agent` 等高层 agent 保持阵型一致
- 但其 persona 必须明确为 Router / Navigator，而不是 implementation agent

### 6.2 Atomic Builders

- `cpu-native-builder`
- `cpu-plugin-builder`
- `gpu-native-builder`
- `gpu-plugin-builder`
- `npu-native-builder`
- `npu-plugin-builder`

## 7. 当前阶段的实现范围

phase 1 允许 taxonomy 完整，但实现覆盖不完整。

建议当前状态按以下方式表达：

- `cpu-native-builder`
  - current scope: 已有真实能力

- `cpu-plugin-builder`
  - current scope: 已有真实能力

- `gpu-native-builder`
  - current scope: 承接当前 `gpu-builder`

- `gpu-plugin-builder`
  - current scope: placeholder

- `npu-native-builder`
  - current scope: placeholder

- `npu-plugin-builder`
  - current scope: **currently ACLNN-only**

这里需要特别强调：

- `npu-plugin-builder` 是 taxonomy 名
- 它当前 phase-1 的真实实现范围只覆盖 ACLNN 路径
- 未来如果出现其他 NPU plugin 路径，不需要改 taxonomy，只需扩展其内部 scope

## 8. ACLNN 的定位

ACLNN 在本方案中不再作为顶层 taxonomy 名存在。

原因：

- ACLNN 是当前已知的一条具体 NPU plugin 实现路径
- 但顶层 taxonomy 需要表达的是“后端 + 接入范式”，而不是某个当前技术实现

因此：

- 顶层命名使用 `npu-plugin-builder`
- phase-1 scope 明确写为 ACLNN-only
- `aclnn-builder` 只能作为迁移期 legacy 名存在

这意味着：

- 当前能力不丢
- 顶层命名更稳定
- 后续扩展其他 NPU plugin 路径时，不需要再改 taxonomy

## 9. Legacy Mapping

建议迁移关系如下：

- `gpu-builder` -> `gpu-native-builder`
- `mindspore-aclnn-operator-devflow` -> `npu-plugin-builder`
- `aclnn-builder` -> `npu-plugin-builder`
- `cpu-native-builder` -> keep
- `cpu-plugin-builder` -> keep

对于尚未形成稳定能力的格子：

- `gpu-plugin-builder` -> placeholder
- `npu-native-builder` -> placeholder

## 10. 与现有 update plan 的关系

本需求稿不否定 `ms-skills-update-plan.md` 中对 `op-agent` 的高层定位：

- `op-agent` 仍然负责 missing-operator analysis 和 routing
- builder 仍然位于其下

本需求稿补充的是 operator 领域更底层的 taxonomy 设计：

- 如何统一命名 builder
- 如何定义 builder 的原子能力
- 如何在 phase 1 接受 placeholder 的存在

因此，这份需求稿是对 operator 子域架构的进一步收口，而不是对总 plan 的否定。

## 11. 设计原则

### 11.1 先建立 taxonomy，再补齐实现

本次优先建立完整 taxonomy，不要求一次性补齐全部 builder 实现。

### 11.2 名字服务于架构，不服务于当前技术细节

顶层 taxonomy 名字优先体现 backend + integration type，而不是当前具体技术栈。

### 11.3 placeholder 是允许的

只要明确写清当前 scope，placeholder 是可接受的，不视为设计错误。

### 11.4 builder 仍然是 implementation-path skill

builder 的职责仍然是实现路径能力，不应退化为高层路由，也不应默认吞掉整个 delivery 流程。

## 12. 需要写入正式 Plan 的关键点

后续更新 `ms-skills-op-agent-plan.md` 时，至少应写入以下内容：

- `op-agent` 是 Navigator
- builder taxonomy 采用 2x3 正交矩阵
- builder 命名统一为 `{backend}-{integration_type}-builder`
- `npu-plugin-builder` 当前 scope 为 ACLNN-only
- `gpu-plugin-builder` / `npu-native-builder` 可先保留为 placeholder
- legacy mapping 必须写清

## 13. 一句话总结

这次重新定位的核心不是把 ACLNN 做大，而是把 operator skill family 统一重构成一套：

- 顶层对称
- 命名稳定
- 可接受 placeholder
- 当前能力不丢失

的正交 taxonomy。







# api-helper 重新定位

Shared API Helper Refactor Proposal (Updated)

## Goal
Transform the legacy `api-helper` and `mint-aclnn-precheck` skills into a **passive, shared knowledge base** (Shared References) consumed directly by backend builders, eliminating them as standalone top-level routing skills.

## Core Architecture: Core + Lenses
The shared capability operates on the MindSpore API-level object model. It is physically split into generic cores and backend-specific lenses to maximize reuse and prevent context bloat.

### 1. Core A: API Identity (`api-identity.md`)
Used by ALL builders (CPU/GPU/NPU).
**Purpose**: Resolve `mindspore.mint.xxx` -> internal function -> `api_def` -> non-deprecated `op_yaml` branches -> exact `Primitive` names.

### 2. Core B: Backward Inventory (`bprop-inventory.md`)
Used by ALL builders (CPU/GPU/NPU).
**Purpose**: Search `REG_BPROP_BUILDER` to determine if a backward definition exists and extract the list of actual backward operator calls (dedicated `Emit` vs inline `ib->Xxx`).

### 3. Backend Lenses (`backend-lens-<backend>.md`)
Read ONLY by specific builders.
**Purpose**: Extend the generic identity with static dispatch evidence (e.g., `dispatch.enable`, `auto_generate` vs `customize`, `kbk`).
- **Phase 1 Active Lens**: `backend-lens-ascend.md` (Consumed strictly by NPU builders).
- **Placeholders**: CPU and GPU lenses do not exist physically in Phase 1 to prevent token waste, as they currently lack complex static dispatch tags.

## Consumption Model (No Sub-Agent Invocation)
Shared helpers are **NOT** executable skills. They do not have `skill.yaml` files.
Builders consume them via explicit `Read` instructions in their `SKILL.md` files.

**Example in `cpu-plugin-builder/SKILL.md`:**
> ### Step 1: Resolve API Identity and Backward Ops
> Read the following shared references to map the public API to its Primitive and backward ops:
> - `skills/_shared/api-helper/reference/api-identity.md`
> - `skills/_shared/api-helper/reference/bprop-inventory.md`
> *(Note: CPU builder explicitly ignores the Ascend lens).*

## Standardized Output Schema
Builders must output the collected evidence in a strict tree format (defined in the reference documents) before proceeding to write C++/YAML code. This ensures deterministic context preservation.

## Migration & Deprecation
- Merge `api-helper/reference/mindspore_api_call_chain.md` into Core A & B.
- Merge `mint-aclnn-precheck/reference/mint_to_aclnn_precheck_guide.md` into Core A, Core B, and Lens Ascend.
- **DELETE** the top-level `api-helper/` and `mint-aclnn-precheck/` directories containing `skill.yaml` and `SKILL.md`.
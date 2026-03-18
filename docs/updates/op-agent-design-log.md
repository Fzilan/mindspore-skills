# op-agent 设计日志

## V1

### Structure

```text
skills/
├── op-agent/                  # 高层路由
├── op-discovery-helper/       # discovery / 静态盘点
├── cpu-plugin-builder/        # CPU plugin 实现
├── cpu-native-builder/        # CPU native 实现
├── gpu-builder/               # GPU 实现
└── aclnn-builder/             # Ascend ACLNN 实现
```

### 预期

- `op-agent` 做高层路由
- `op-discovery-helper` 做证据收集和静态盘点
- builder 做具体实现
- `api-helper` 和 `mint-aclnn-precheck` 合并为统一 discovery 层

## V2

### 存量问题

- `op-agent` 与 `op-discovery-helper` 都是 top-level manual skill 时，交互机制不清晰
- 容易违反 update plan 的单任务单技能倾向
- `op-discovery-helper` 容易滑向过早工具化，和 phase-1 prompt-first/manual-first 冲突
- `aclnn-builder` 需要防止重新膨胀成 discovery + delivery 混合 skill

### 预期

- `op-agent` 成为 discovery + routing 单入口
- builder 只做实现路径
- `api-helper` 与 `mint-aclnn-precheck` 不再作为 top-level skill 发展
- helper 变成 `op-agent` 内部的 helper phase / supporting step

### Structure

```text
skills/
├── op-agent/                  # discovery + routing 单入口，内部含 helper phase
├── cpu-plugin-builder/        # CPU plugin 实现
├── cpu-native-builder/        # CPU native 实现
├── gpu-builder/               # GPU 实现
└── aclnn-builder/             # Ascend ACLNN 实现
```

### 改动点

- 删除 top-level `op-discovery-helper`，why：避免 skill 间调用冲突
- 将 discovery 能力收回 `op-agent` 内部，why：保证单任务单入口
- 将 `api-helper` 与 `mint-aclnn-precheck` 迁移为 `op-agent` 的 reference/checklist 能力，why：避免过早工具化
- 保持实现层只保留 builder，why：收紧边界，防止角色混叠

## V3

### 存量问题

- V2 虽然把 discovery 收回了 `op-agent`，但没有把上游 handoff 前提提升到设计头部
- 这样会让 `op-agent` 的定位仍然显得偏宽，像是在重新承担“识别问题是否属于 operator gap”这类 analysis 职责

### 预期

- `op-agent` 的定位以前置 assumption 为起点
- 默认假设 analysis agent 已经确认：`mindspore.mint.xxx` 在某 backend 跑不起来
- helper 明确只是 `op-agent` 内部用于理解代码映射和支持路由的 phase

### Structure

```text
skills/
├── op-agent/                  # analysis handoff 后的单入口，内部含 helper phase
├── cpu-plugin-builder/        # CPU plugin 实现
├── cpu-native-builder/        # CPU native 实现
├── gpu-builder/               # GPU 实现
└── aclnn-builder/             # Ascend ACLNN 实现
```

### 改动点

- 将 `Upstream Handoff Assumption` 提升到 plan 头部，why：这是 `op-agent` 的定位前提，不是普通步骤说明
- 明确 `op-agent` 默认承接 analysis agent 的 handoff，why：避免它重新承担 analysis 职责
- 明确 helper 只是 `op-agent` 内部用于理解 MindSpore 映射关系和支持路由的 phase，why：进一步收紧 discovery 的角色边界

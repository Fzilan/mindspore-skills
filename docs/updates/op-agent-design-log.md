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

### Structure

```text
skills/
├── op-agent/                  # discovery + routing 单入口
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

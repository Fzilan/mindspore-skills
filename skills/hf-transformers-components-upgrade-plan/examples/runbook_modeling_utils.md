# modeling_utils 升级 Runbook（MindONE transformers -> 兼容 HF transformers v5）

面向开发/Agent 的可执行文档：按顺序改哪些文件、每步改什么、做到什么算完成。

## Inputs
- 上游仓库（只读对照）：`transformers/`（目标 tag：`v5.0.0rc2`）
- 当前 mindone：`mindone/`（当前兼容 tag：`v4.57.1`）
- 升级计划输出件：`upgrade_data_v4.57.1_to_v5.0.0.xlsx`

## Outputs（本次产出）
- 新增：`mindone/mindone/transformers/core_model_loading.py`（裁剪版，MindSpore 侧可用）
- 修改：`mindone/mindone/transformers/modeling_utils.py`（import/加载主链路/参数语义对齐）
- 可选修改（按触发）：`mindone/mindone/transformers/integrations/peft.py` 等

## Upgrade Graph（执行链路）
S1 -> S2 -> S3 -> S4 -> S5

## Steps（按顺序执行；每步都可独立提交）

### S1. 引入裁剪版 core loader（对齐 v5 的模块拆分）
- Files
  - + `mindone/mindone/transformers/core_model_loading.py`
- Goal
  - 提供一个“统一加载入口”，让 `modeling_utils.py` 后续收敛到单点调用。
- API（先做最小可用；接口尽量对齐 HF v5 命名）
  - `@dataclass WeightRenaming(source_patterns: list[str], target_patterns: list[str])`
  - `@dataclass WeightConverter(WeightRenaming, op: Any | None = None)`（先占位，不实现复杂 op 链）
  - `convert_and_load_state_dict_in_model(model, state_dict, weight_mapping=None, **kwargs)`
    - 返回：`missing_keys, unexpected_keys, mismatched_keys, disk_offload_index, conversion_errors`
    - MindONE 最小实现：只做 `weight_mapping` rename + 调用 mindone 现有加载/映射逻辑；其余 kwargs 忽略或记录到 `conversion_errors`
  - `revert_weight_conversion(model, state_dict)`（先允许 no-op，给 `save_pretrained` 留口子）
- Not Supported（明确裁剪边界，避免误用）
  - accelerate/device_map/offload/meta device/dtensor/tp/ep：不实现；kwargs 进入后忽略或给出明确错误信息
  - `ConversionOps`（Chunk/Concatenate/…）：不实现
- Done when
  - `python -c "from mindone.transformers.core_model_loading import convert_and_load_state_dict_in_model"` 成功

### S2. 清理 modeling_utils 的 v5 破坏性 import（先保证能 import）
- Files
  - * `mindone/mindone/transformers/modeling_utils.py`
- Change（把“依赖 HF v4 的 symbol”改成 v5 可用的来源）
  - 移除：`download_url`, `is_remote_url`
  - 移除/下线：`TF_WEIGHTS_NAME`, `TF2_WEIGHTS_NAME`, `FLAX_WEIGHTS_NAME`（v5 已移除 TF/Flax 支持）
  - offline：使用 `from huggingface_hub import is_offline_mode`
  - logging：用子模块导入（避免依赖 `transformers.utils.__init__` 的 re-export）
    - 推荐：`from transformers.utils import logging`（导入子模块）
  - hub 相关：优先从 `transformers.utils.hub` 导入（更稳定）
    - 如：`cached_file`, `has_file`, `extract_commit_hash`, `get_checkpoint_shard_files`, `convert_file_size_to_int`
  - safetensors：改为本地 try/except 检测 `_HAS_SAFETENSORS`（替代 `is_safetensors_available`）
- Done when
  - `python -c "import mindone.transformers.modeling_utils as m; print('ok')"` 成功

### S3. 下线 v5 已移除能力（URL 直链、TF/Flax）
- Files
  - * `mindone/mindone/transformers/modeling_utils.py`
- Change
  - URL 直链：检测 `http(s)://` 直接报错（提示用 repo_id + hub cache 或本地目录）
  - TF/Flax：保留参数也可以，但执行时一旦 `from_tf/from_flax=True` 直接 `NotImplementedError`（明确说明 v5 移除）
- Done when
  - 代码里不再出现：`download_url` / `is_remote_url` / `TF_WEIGHTS_NAME|TF2_WEIGHTS_NAME|FLAX_WEIGHTS_NAME`

### S4. 把“加载主动作”收敛到 core loader（为后续联动留单点）
- Files
  - * `mindone/mindone/transformers/modeling_utils.py`
- Change
  - 将 “state_dict -> load into model” 的关键路径改为调用：
    - `from .core_model_loading import convert_and_load_state_dict_in_model`
  - 保留 mindone 的差异化逻辑（PT->MS param name mapping / shape 处理 / safetensors(ms) load 等）
  - 但对外输出结构尽量对齐 v5（missing/unexpected/mismatch/errors）
- Done when
  - `modeling_utils.py` 内部存在单点调用 `convert_and_load_state_dict_in_model(...)`，并用于主加载路径

### S5. 对齐关键参数语义（减少上层连锁修改）
- Files
  - * `mindone/mindone/transformers/modeling_utils.py`
- Change（重点对齐项）
  - `use_auth_token`：仅兼容；统一归一为 `token`
  - `use_safetensors`：建议签名对齐 v5：`Optional[bool] = True`
    - True：优先/强制 safetensors（找不到就报错或走 auto_conversion）
    - False：强制走非 safetensors
    - None：兼容模式（允许 fallback）
  - `save_pretrained`：在保存 state_dict 前接入 `revert_weight_conversion(model_to_save, state_dict)`
- Done when
  - `use_auth_token` 与 `token` 不会同时生效（冲突时报错）
  - `use_safetensors` 的三态分支在代码中清晰可见、默认值可控

## Quick Checklist（开发完成后勾选）
- [ ] `mindone/mindone/transformers/core_model_loading.py` 存在且可 import
- [ ] `mindone/mindone/transformers/modeling_utils.py` 不依赖 v5 已移除 symbol（URL/TF/Flax）
- [ ] offline mode 来源为 `huggingface_hub.is_offline_mode`
- [ ] 主加载路径已收敛到 `convert_and_load_state_dict_in_model(...)`
- [ ] `use_auth_token` -> `token` 归一逻辑存在，冲突有报错
- [ ] `use_safetensors` 默认与三态语义明确
- [ ] `save_pretrained` 接入 `revert_weight_conversion(...)`

## Guardrails
- 禁止导入（黑名单）：`download_url`, `is_remote_url`, `TF_WEIGHTS_NAME`, `TF2_WEIGHTS_NAME`, `FLAX_WEIGHTS_NAME`, `is_safetensors_available`
- 强制存在（白名单）：`mindone/mindone/transformers/core_model_loading.py` 且导出 `convert_and_load_state_dict_in_model`
- 强制收敛点：`modeling_utils.py` 里只能有一个“核心加载入口”（调用 core loader）


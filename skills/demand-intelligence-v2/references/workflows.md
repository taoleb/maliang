# 需求情报工作流

## DEM-SCN：场景清单

### 当前场景

每个场景记录：

```text
scene_id / parent_scene_id / name / definition / boundary
user_groups / lifecycle_stage / time_conditions / space_conditions
environment_conditions / tags / related_scenes / evidence_ids
```

场景关系类型：依赖、强关联、弱关联、冲突、前后序。关联强度如果没有计算依据，仅使用定性等级。

### PESTEL与未来场景

每条趋势记录维度、事实、时间范围和来源。趋势影响、新场景、出现时间和机会等级写入 inference。

未来场景四维评估：用户价值、技术可行性、商业价值、政策合规。缺少任一维度时保留缺口，不计算伪精确总分。

### 验证闭环

功能上线前后比较必须包含：样本、指标定义、观察窗口、对照条件和显著差异。没有前后数据时只能设计验证方案。

反馈入口需要写入授权。反馈保存原文、提交时间、关联 scene_id、状态和处理记录。

## DEM-CARD：需求卡片

每张卡片至少包含：

```text
demand_id / scene_id / user_group / behavior_step / need
pain_point / original_quotes / current_satisfaction
competitor_coverage / solution_gap / opportunity / evidence_ids
```

### 强度评分

满足数据条件时，可采用：

```text
强度 = 频次归一化40% + 不满意度30% + 业务关联度30%
```

把计算方法、样本范围和分项值写入 inference.method。缺少频次或满意度时不输出1-5精确值，可输出“待评估”。

### 竞品满足度

分开记录功能覆盖、用户口碑和体验评分。不要用“功能存在”代替“用户满意”。

## DEM-OPP：机会长名单

每条需求保留唯一 demand_id、标准标签、场景、用户群体、渠道和来源。

主题聚合应记录聚类或人工归类方法。热度1-10需要明确：

- 样本渠道
- 统计周期
- 去重规则
- 渠道权重
- 归一化方法

月度或季度趋势要求至少两个可比期间；只有一个期间时建立数据缺口。

## 输出建议

- Markdown：场景树、卡片、机会榜单和方法说明。
- Excel：场景、需求、原始表述、样本、来源五个Sheet。
- 网页：用于树形浏览和筛选，但原始情报包仍是事实载体。


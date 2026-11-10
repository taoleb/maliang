# 政策工作流

## POL-ARC-001 政策全量信息

结构：

```text
policy_id / title / document_number / issuing_authority
publication_date / effective_date / expiry_date / status
jurisdiction / policy_type / industry_sectors / keywords
full_text_ref / attachments / source_ids
```

“全量”指本次数据源范围内的记录，不得在没有覆盖率证明时声称所有政策。

## POL-ARC-002 政策文本摘录

每条摘录保存：

```text
excerpt_id / policy_id / verbatim_text / article_or_page
context_before / context_after / selected_by / source_id
```

总结和解读另存，不放入 `verbatim_text`。

## POL-CORE-001 产业引导方向

先建立政策事实，再生成 inference：

- 支持发展的产业和环节
- 约束或限制
- 目标时间和量化指标
- 适用主体和地域
- 与现行政策的关系
- 对产业结构、需求或企业行动的可能影响

结论必须引用条款ID，避免只引用整份政策标题。

## POL-CORE-002 核心条款

条款分类：

- 支持类：补贴、税收、融资、用地、人才、研发等
- 约束类：准入、环保、安全、数据、地域、资质等
- 量化指标：金额、比例、产能、时间、面积、排放、技术指标等

量化值拆成 `value`、`unit`、`condition` 和 `deadline`，不要只保留一段文本。

## 交互功能边界

上传、编辑、关联报告、替换关联和附件下载需要应用或存储工具。本 Skill 负责生成结构和调用已提供工具，不假装页面已存在。


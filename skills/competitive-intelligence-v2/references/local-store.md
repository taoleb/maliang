# 本地存储模型

默认数据库位于 `%LOCALAPPDATA%\hermes\intelligence-v2\intelligence.db`。

## 表

- `runs`：一次研究或监控运行。
- `sources`：脱敏后的来源和原始引用。
- `facts`：来源支持的事实。
- `inferences`：推断、评分和建议。
- `gaps`：数据缺口。
- `entities`：企业、产业、场景、产品、政策等实体。
- `entity_aliases`：别名和标准名称。
- `collections`：收藏或人工归档。
- `feedback`：用户反馈和审核意见。

## 写入语义

- `run_id`、`fact_id`、`inference_id`、`gap_id`、`source_id` 用于幂等写入。
- 同ID再次写入会更新同一记录，不重复插入。
- 不同来源支持同一事实时，保留多个 `source_ids`。
- 不同口径的数值必须是不同 fact。
- 用户编辑通过 feedback 或新事实记录保存，不覆盖原始来源。

## 使用限制

当前 v2 SQLite 是本地研究工作台，不是多用户生产数据库。权限、并发、审计和网页CRUD如要生产使用，应迁移到服务化数据库和API。


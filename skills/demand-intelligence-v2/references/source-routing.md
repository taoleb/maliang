# 需求情报来源路由

## Hermes MCP 配置边界

- 使用已启用的 `internal-knowledge`、`competitive-kb`、`expert-knowledge-base`、`tech-cards` 和 `pci-kb`。
- 公司内部知识只调用 `internal-knowledge`。
- 默认只调用读取类工具；任何反馈、收藏或知识库写入仍需用户明确授权。

## 核心来源：internal-knowledge

1. `search_internal_knowledge` 搜索场景、需求、痛点、用户画像和调研样本。
2. 重要候选使用 `get_internal_knowledge_card` 取得完整卡片、原始引用和审核状态。
3. 根据卡片 scope 标记 `internal_direct`、`benchmark` 或 `external_context`；不把对标和外部背景改写为公司自身事实。

内部来源被用户禁用或不可用时，不阻断任务，将缺口记入 `run_manifest` 和 `gaps`。

## 其他可用 MCP

| 问题 | MCP 与读取工具 | 使用边界 |
|---|---|---|
| 竞品功能覆盖与满足度 | `competitive-kb`: `get_enterprise_list` 确认企业，`smart_search` 或 `search_profiles` 找条目，`get_item_detail`/`get_profile` 取详情 | 功能存在不等于用户满意；口碑和体验分别取证 |
| 用户、场景和需求深度研究 | `expert-knowledge-base`: 覆盖不明时先 `list_topics`，再 `search_knowledge` → `get_knowledge`，必要时 `get_related` | 专家判断与原始用户样本分开 |
| 未来需求的技术可行性 | `tech-cards`: `search_tech_cards` → `get_card_detail`；按功能查找时可用 `get_tech_by_function` | 技术热度或成熟度不等于用户需求频次 |
| PESTEL 中的政策和法律因素 | `pci-kb`: `search_articles(dimension="policy")` → `get_article_detail` | 作为场景驱动因素，不代替需求样本 |
| 产业环境和市场背景 | `pci-kb`: `search_articles(dimension="industry")` → `get_article_detail`；数据库范围统计才用 `get_statistics` | 只作 external context，统计必须声明数据库范围 |
| 资本热度与赛道关注 | `pci-kb`: `search_articles(dimension="capital")` → `get_article_detail` | 只作机会环境，不等于用户需求 |

## competitive-kb 搜索规则

- `smart_search` 使用单一主题关键词，并通过 enterprise 和 dimension 限定。
- 重要条目调用 `get_item_detail` 或对应详情档案，不从搜索列表直接生成完整企业画像。
- 只读任务不调用 `kb_upsert_*`、`kb_set_item_status`、`kb_batch_archive`、`kb_add_*` 或其他写入类工具。

## 外部来源与降级

- 公开用户研究、调研机构、官方统计、论坛和评论可按任务需要补充，必须记录渠道、时间、样本量和样本选择方法。
- 搜索结果数量不是需求频次。
- 无内部数据：输出行业/竞品背景，不写成公司自身需求。
- 无样本数据：只提供定性需求假设并建立 `gap`。
- 无竞品体验数据：只列功能覆盖，不生成满意度评分。

# 资本来源路由

## Hermes MCP 配置边界

- 使用已启用的 `pci-kb`、`competitive-kb`、`internal-knowledge`、`expert-knowledge-base` 和 `tech-cards`。
- 内部资本口径只调用 `internal-knowledge`。
- 默认只调用读取类工具；任何知识库或本地数据写入仍需用户明确授权。

## 核心来源：pci-kb capital

1. 需要了解资本标签和数据覆盖时，先调用 `get_tags(dimension="capital")` 或 `get_statistics`。
2. `search_articles(dimension="capital", keyword=<企业/机构/赛道短词>)` 发现投融资候选。
3. 重要候选调用 `get_article_detail`，优先读取结构化的投资机构、被投企业、金额、估值、轮次和事件日期。
4. `get_shareholders` 和 `get_personnel` 只作股东/主要人员补充；空结果不代表企业没有股东或人员。
5. `get_statistics` 只能用于声明过的 `pci-kb` 数据库范围聚合，不直接写成全市场总量。

## 车企资本动作：competitive-kb

1. `get_enterprise_list` 确认企业 ID 和覆盖范围。
2. `smart_search` 使用单一主题关键词、enterprise 和 `dimension="资本"`。
3. 重要结果用 `get_item_detail`；需要完整资本档案时用 `search_profiles` → `get_profile(profile_type="capital")`。
4. 只读任务不调用 `kb_upsert_*`、`kb_set_item_status`、`kb_batch_archive`、`kb_add_*` 或其他写入类工具。

## 其他可用 MCP

| 问题 | MCP 与读取工具 | 使用边界 |
|---|---|---|
| 公司内部资本口径 | `internal-knowledge`: `search_internal_knowledge` → `get_internal_knowledge_card` | 按卡片 scope 使用，不覆盖公开披露事实 |
| 专家资本研究和行业解读 | `expert-knowledge-base`: `search_knowledge` → `get_knowledge`，必要时 `get_related` | 观点与交易事实分开 |
| 技术成熟度 | `tech-cards`: `search_tech_cards` → `get_card_detail`，或 `get_tech_by_function` | 只能作为估值判断的依据之一，不直接推导估值 |
| 产业赛道背景 | `pci-kb`: `search_articles(dimension="industry")` → `get_article_detail` | 用于解释赛道环境，不代替资本事件 |
| IPO 和上市公司交易 | 交易所、证监机构、公司公告原文 | 状态、问询、回复和交易条款需要官方原文核验 |

## 降级

- `pci-kb` 不可用：使用公司公告、投资机构公告和可信商业信息源。
- 金额冲突：保留不同来源，检查币种、投前/投后和累计/本轮口径。
- 股东字段为空：建立 `gap`，不写“无股东信息”。
- IPO 缺少官方原文：不得声称“实时状态”。

## 禁止推断

- 专利数量不能直接转换为企业估值。
- 新闻热度不能直接等于资本流入。
- 未披露金额不能按行业平均数补齐。

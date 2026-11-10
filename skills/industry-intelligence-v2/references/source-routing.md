# 产业来源路由

## Hermes MCP 配置边界

- 使用已启用的 `pci-kb`、`competitive-kb`、`expert-knowledge-base`、`tech-cards` 和 `internal-knowledge`。
- 公司内部产业口径只调用 `internal-knowledge`。
- 默认只调用读取类工具；知识库写入仍需用户明确授权。

## 核心来源：pci-kb industry

1. 需要了解产业标签和覆盖时，先调用 `get_tags(dimension="industry")` 或 `get_statistics`。
2. `search_articles(dimension="industry", keyword=<产业/环节短词>)` 发现产业档案和研究文章。
3. 重要候选调用 `get_article_detail`，读取完整内容、标签和已抽取产业字段。
4. `get_statistics` 只表达 `pci-kb` 当前数据库范围内的数量和标签分布，不直接转换为市场规模或完整企业数。
5. 产业任务同时涉及政策准入或资本热度时，再按需使用 `dimension="policy"` 或 `dimension="capital"`，不与产业事实混为同一口径。

## 企业×产业节点：competitive-kb

1. `search_nodes` 按产业主题定位节点，同名节点先确认 enterprise。
2. `get_profile(profile_type="industry")` 获取指定企业×节点的完整产业档案；需要发现档案时先用 `search_profiles`。
3. 遍历多个企业档案的市场格局、参与者和趋势字段，不把单家企业档案当作产业汇总。
4. 不依赖宽泛 `smart_search(source_type="industry_profile")` 列表直接组装产业结论。
5. 只读任务不调用 `kb_upsert_*`、`kb_set_item_status`、`kb_batch_archive`、`kb_add_*` 或其他写入类工具。

## 其他可用 MCP

| 问题 | MCP 与读取工具 | 使用边界 |
|---|---|---|
| 产业深度研究和壁垒解读 | `expert-knowledge-base`: 覆盖不明时先 `list_topics`，再 `search_knowledge` → `get_knowledge`，必要时 `get_related` | 专家观点与可核验产业事实分开 |
| 技术成熟度和赋能关系 | `tech-cards`: `search_tech_cards` → `get_card_detail`，或 `get_tech_by_function` | 使用通用技术词；不直接推导市场份额 |
| 公司内部产业口径 | `internal-knowledge`: `search_internal_knowledge` → `get_internal_knowledge_card` | 根据 scope 区分 `internal_direct`、`benchmark` 和 `external_context` |
| 政策准入与产业引导 | `pci-kb`: `search_articles(dimension="policy")` → `get_article_detail` | 政策条款与产业阶段判断分开 |
| 赛道融资和资本环境 | `pci-kb`: `search_articles(dimension="capital")` → `get_article_detail` | 资本热度只是产业阶段证据之一 |
| 最新市场规模和参与者 | 官方统计、公司公告和可信研究 | 保留地域、统计对象、实际/预测和时间口径 |

## 降级与专利缺口

- `pci-kb` industry 不可用：组合 `expert-knowledge-base`、`competitive-kb` 产业档案和公开来源，并标记覆盖限制。
- 非汽车关联产业：不假设 `competitive-kb` 覆盖。
- 市场规模口径冲突：保留地域、统计对象和预测/实际差异。
- 联系方式不可得：留空，不猜测。
- 用户明确要求专利精确数据时，记录 `patsnap-search` 不可用；若没有其他授权的专利数据源，建立 `gap`，不生成伪精确总量。

# 竞争来源路由

## Hermes MCP 配置边界

- 使用已启用的 `competitive-kb`、`internal-knowledge`、`expert-knowledge-base`、`tech-cards` 和 `pci-kb`。
- 内部对标口径只调用 `internal-knowledge`。
- 默认只调用读取类工具；`competitive-kb` 的维护、归档和 upsert 工具只在用户明确要求写入时使用。

## 核心来源：competitive-kb

1. `get_enterprise_list` 动态确认企业 ID 和覆盖范围。
2. `get_enterprise_intelligence` 获取企业概览、条目统计和维度覆盖。
3. `smart_search` 使用单一主题关键词、enterprise 和 dimension；不使用“公司名 + 空格 + 关键词”代替结构化过滤。
4. 重要知识条目用 `get_item_detail`。
5. 深度档案使用 `search_profiles` → `get_profile`，按任务选择 `strategy`、`product`、`tech`、`industry` 或 `capital`；不从混合搜索列表直接推断完整企业画像。
6. 多企业总览可用 `compare_enterprises`，但具体事实仍回到条目或档案详情。

不要硬编码库中条目数、档案数或数据截止日期；运行时用 `get_kb_stats`、企业覆盖工具或条目日期确认。

## 其他可用 MCP

| 问题 | MCP 与读取工具 | 使用边界 |
|---|---|---|
| 公司内部对标口径 | `internal-knowledge`: `search_internal_knowledge` → `get_internal_knowledge_card` | 根据 scope 区分内部事实、benchmark 和 external context |
| 战略、行业和商业解读 | `expert-knowledge-base`: 覆盖不明时先 `list_topics`，再 `search_knowledge` → `get_knowledge`，必要时 `get_related` | 专家观点不改写为企业事实 |
| 技术路线、成熟度和功能映射 | `tech-cards`: `search_tech_cards` → `get_card_detail`，或 `get_tech_by_function` | 技术卡与企业已量产应用事实分开 |
| 产业环境和产业链背景 | `pci-kb`: `search_articles(dimension="industry")` → `get_article_detail` | 用于解释企业布局环境，不代替企业动作事实 |
| 政策影响 | `pci-kb`: `search_articles(dimension="policy")` → `get_article_detail` | 政策条款与企业应对分开 |
| 资本动作背景 | `pci-kb`: `search_articles(dimension="capital")` → `get_article_detail`，股东/人员按需用 `get_shareholders`/`get_personnel` | 融资、并购、股权和发债不列入 `COM-*` 核心结果 |
| 最新财务、销量、产品和合作 | 公司公告、财报、官方发布和可信行业数据 | 保留时间、地域、版本和统计口径 |

## 降级

- 企业不在 `competitive-kb`：使用公开来源，不伪造 enterprise ID。
- 只有搜索摘要：动态为 `candidate`。
- 最新指标与库内值冲突：按时间、地域和统计口径保留多条事实。
- 用户明确要求专利精确数据：记录 `patsnap-search` 不可用；没有其他授权专利源时建立 `gap`，不生成总量趋势。

## 全球化 24 家研究范围

国内：一汽、东风、上汽、广汽、比亚迪、吉利、奇瑞、长城、蔚来、小鹏、理想、零跑、华为、小米。

国际：大众、丰田、本田、日产、通用、斯蒂兰蒂斯、福特、雷诺、现代、特斯拉。

这是研究名单，不代表所有企业都在同一 MCP 内。

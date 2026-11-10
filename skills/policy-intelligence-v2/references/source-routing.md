# 政策来源路由

## Hermes MCP 配置边界

- 使用已启用的 `pci-kb`、`internal-knowledge`、`competitive-kb`、`expert-knowledge-base` 和 `tech-cards`。
- 内部政策口径只调用 `internal-knowledge`。
- 默认只调用读取类工具；知识库或报告关联写入仍需用户明确授权。

## 核心路径：pci-kb policy

1. 需要了解标签和覆盖范围时，先调用 `get_tags(dimension="policy")` 或 `get_statistics`。
2. `search_articles(dimension="policy", keyword=<短关键词>)` 发现候选。
3. 检查 title、doc_number、标签和行业字段，排除新闻、访谈和弱关联文章。
4. `get_article_detail` 获取全文、文号、发文机关、日期和已抽取字段。
5. 时效性强、效力状态重要或需要逐字摘录时，再使用发布机关/政府法定站点原文核验。

`get_statistics` 只能表达 `pci-kb` 当前数据库范围内的分布，不自动代表全部政策。

## 其他可用 MCP

| 需求 | MCP 与读取工具 | 使用边界 |
|---|---|---|
| 公司内部政策口径 | `internal-knowledge`: `search_internal_knowledge` → `get_internal_knowledge_card` | 仅标记为 `internal_direct`，不替代政策原文 |
| 竞企政策应对 | `competitive-kb`: `smart_search` 发现动态，`get_item_detail` 取详情 | 企业应对事实与政策条款分开 |
| 政策解读和产业影响 | `expert-knowledge-base`: `search_knowledge` → `get_knowledge`，必要时 `get_related` | 专家解读属于观点或推断 |
| 政策目标的技术可行性 | `tech-cards`: `search_tech_cards` → `get_card_detail`，或 `get_tech_by_function` | 技术卡支持可行性判断，不作政策效力证据 |
| 产业和资本背景 | `pci-kb`: 按需使用 `dimension="industry"` 或 `dimension="capital"` | 只补充政策作用环境，不混入政策原文事实 |

## 降级

- `pci-kb` 不可用：搜索发布机关或法定数据库。
- 只有新闻摘要：保存为候选，不输出“政策规定”。
- 找不到效力状态：列为 `gap`，不默认有效。
- 海外政策无原文：明确说明只获得二手解读。

## 可信来源优先级

1. 发布机关原文或法定数据库。
2. 数据库中的完整政策详情。
3. 专业解读。
4. 新闻报道。
5. 搜索摘要。

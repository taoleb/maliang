---
name: competitive-intelligence-v2
description: "汽车竞争情报v2独立版：分析车企战略、产品、产业布局、合资合作、技术研发、销量财务和全球化。用户提到竞争对手、竞品、对标、车型配置、合作、研发、销量、市场份额、海外建厂或全球化时使用；经营财务属于本领域，融资股权不属于本领域。"
metadata:
  maliang:
    emoji: "🏁"
    always: false
  version: 0.3.2
  hermes:
    tags: [competitive, automaker, benchmark, product, finance, globalization, standalone, v2]
    category: intelligence-v2
    standalone: true
    requires_toolsets: [terminal, files]
---

# Competitive Intelligence v2

本 Skill 独立处理 24 个 `COM-*` 功能。

## 资源路由

- 先在 `references/function-requirements.md` 定位命中的功能编号和完整功能要求。
- 战略、产品、产业布局、合作、技术、经营财务和全球化字段见 `references/workflows.md`。
- 竞争库、专利、技术、专家、政策和公开来源路径见 `references/source-routing.md`。
- 结构化证据、时效与冲突处理见 `references/bundle-contract.md` 和 `references/source-governance.md`。
- 只有用户明确要求保存或入库时，才读取 `references/local-store.md`。

## 交付形式

- 默认以 Markdown 交付分析结果；用户未指定其他形式时，不主动生成网页或 PPT。
- 用户在后续追问中可选择“交互式网页”或“PPT”。这是对当前情报结果的输出模式切换：仅要求换格式时复用既有结论与证据，不重新开展完整检索。
- 交互式网页应产出可打开的网页文件，并按内容需要提供搜索、筛选、图表或详情联动；PPT 应产出可演示的 `.pptx` 文件，而不是只给大纲。
- 转换后保留核心结论、数据口径、来源引用、证据时间、置信度、冲突与缺口。只有用户要求更新数据，或现有证据不足以支撑目标格式时，才补充检索并标明新增内容。

## 主流程

1. 规范化企业、集团、品牌、业务单元和车型名称，记录别名；明确 `COM-*` 功能编号、时间范围、地区、对标对象和统计口径。
2. 动态确认数据源的企业列表和覆盖范围，不在报告中使用硬编码条目数、档案数或截止日期。
3. 一次搜索使用单一主题关键词和结构化过滤；重要条目获取详情或原始来源。
4. 最新财务、销量、价格、合作状态和海外进展使用公司公告、财报、官方发布或可靠行业数据核验。
5. 产品发布、预售、上市和交付分开；技术发布与量产应用分开；合作宣布、签约、推进和落地分开。
6. 销量的批发、零售、交付、上险和出口口径不得混合；市场份额必须说明市场定义和分母。
7. 战略定位、影响、未来趋势和其他综合研判写入 `inferences`，不把媒体观点改写为企业事实。
8. 融资、并购、股权和发债不列入 `COM-*` 功能结果；本领域只记录其已证实的战略影响。
9. 生成 `facts / inferences / gaps / provenance / run_manifest`，再运行 `python scripts/validate_bundle.py <bundle.json>`。
10. 验证通过后，使用当前环境可用工具生成用户要求的结果，不依赖交付 Skill；仅在用户明确授权时入库。

## 范围与证据底线

- 多企业对比先统一指标、时间、地域、版本和币种再并列。
- 企业不在专用数据库时使用其他来源并明确降级，不伪造 enterprise ID。
- 只有搜索摘要时记为 `candidate`；不能未核验即写成 `verified`。
- 专利工具不支持聚合时，只列代表性专利，不生成伪精确总量趋势。

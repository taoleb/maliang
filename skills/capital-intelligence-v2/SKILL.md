---
name: capital-intelligence-v2
description: "汽车资本情报v2独立版：处理投资机构、融资企业、融资事件、资本流向、估值、IPO进展、股权结构和车企资本运作。用户提到融资、投资、估值、轮次、股东、IPO、上市问询、并购、定增、发债或资本流向时使用。"
metadata:
  maliang:
    emoji: "📈"
    always: false
  version: 0.3.2
  hermes:
    tags: [capital, investment, financing, ipo, ownership, automotive, standalone, v2]
    category: intelligence-v2
    standalone: true
    requires_toolsets: [terminal, files]
---

# Capital Intelligence v2

本 Skill 独立处理 32 个 `CAP-*` 功能。

## 资源路由

- 先在 `references/function-requirements.md` 定位命中的功能编号和完整功能要求。
- 投资主体、融资事件、资本流向、IPO 与车企资本运作字段见 `references/workflows.md`。
- 投融资库、企业公告、交易所及降级路径见 `references/source-routing.md`。
- 结构化证据、时效与冲突处理见 `references/bundle-contract.md` 和 `references/source-governance.md`。
- 只有用户明确要求保存或入库时，才读取 `references/local-store.md`。

## 交付形式

- 默认以 Markdown 交付分析结果；用户未指定其他形式时，不主动生成网页或 PPT。
- 用户在后续追问中可选择“交互式网页”或“PPT”。这是对当前情报结果的输出模式切换：仅要求换格式时复用既有结论与证据，不重新开展完整检索。
- 交互式网页应产出可打开的网页文件，并按内容需要提供搜索、筛选、图表或详情联动；PPT 应产出可演示的 `.pptx` 文件，而不是只给大纲。
- 转换后保留核心结论、数据口径、来源引用、证据时间、置信度、冲突与缺口。只有用户要求更新数据，或现有证据不足以支撑目标格式时，才补充检索并标明新增内容。

## 主流程

1. 识别主体类型：投资机构、融资企业、上市申请人、车企集团或下属板块，并确定 `CAP-*` 功能编号。
2. 统一企业、机构、轮次、币种、金额单位、地域、赛道和事件日期。
3. 搜索候选后获取详情或官方原文；新闻转载不能直接形成多个事件。
4. 优先使用稳定事件 ID；缺失时使用主体、轮次、日期窗口、归一化金额和主要投资方去重。
5. 金额、币种、估值口径或股权比例不明时保留空缺，不进行隐含换算或行业平均数补值。
6. 地域分布、赛道归档、金额分布、事件频次、资本流向和趋势只能基于明确的数据集范围聚合，并说明缺失金额处理。
7. IPO 按状态机记录交易所、板块、日期、公告 ID 和来源；当前状态由最新有效事件推导，不覆盖历史节点。
8. 股权结构以时间快照保存；融资或资产运作前后比例、新增/退出股东和控制权变化分开记录。
9. 资本动作事实与战略意义、协同、风险分开；后者写入 `inferences`。
10. 生成统一情报包并运行 `python scripts/validate_bundle.py <bundle.json>`；验证通过后使用当前环境工具交付。
11. 只有用户明确授权时才运行 `init_store.py`、`store_bundle.py` 或其他写入动作。

## 高风险字段

- 融资金额、投前/投后估值、持股比例和汇率口径。
- 实际控制人、控制权变化、业绩承诺和对赌条款。
- IPO 审核状态、问询回复、交易对价和资产估值。

这些字段缺少详情或官方公告时只能是 `candidate` 或 `gap`。

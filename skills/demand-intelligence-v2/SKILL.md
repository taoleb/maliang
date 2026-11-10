---
name: demand-intelligence-v2
description: "汽车需求情报v2独立版：构建一二级场景、未来场景推演、用户画像、需求卡片、痛点、需求强度、竞品满足度和需求机会长名单。用户提到用户需求、场景、画像、痛点、体验、机会、热度、PESTEL或未来出行时使用。"
metadata:
  maliang:
    emoji: "🧭"
    always: false
  version: 0.3.2
  hermes:
    tags: [demand, scenario, user-insight, pain-point, automotive, standalone, v2]
    category: intelligence-v2
    standalone: true
    requires_toolsets: [terminal, files]
---

# Demand Intelligence v2

本 Skill 独立处理 30 个 `DEM-*` 功能。

## 资源路由

- 先在 `references/function-requirements.md` 定位本次请求对应的功能编号，只读取命中条目的完整需求。
- 场景清单、需求卡片、机会长名单的字段和量化方法见 `references/workflows.md`。
- 选择内部调研、竞品、专家、政策或公开来源时读取 `references/source-routing.md`。
- 需要结构化结果时读取 `references/bundle-contract.md` 和 `references/source-governance.md`。
- 只有用户明确要求保存或入库时，才读取 `references/local-store.md`。

## 交付形式

- 默认以 Markdown 交付分析结果；用户未指定其他形式时，不主动生成网页或 PPT。
- 用户在后续追问中可选择“交互式网页”或“PPT”。这是对当前情报结果的输出模式切换：仅要求换格式时复用既有结论与证据，不重新开展完整检索。
- 交互式网页应产出可打开的网页文件，并按内容需要提供搜索、筛选、图表或详情联动；PPT 应产出可演示的 `.pptx` 文件，而不是只给大纲。
- 转换后保留核心结论、数据口径、来源引用、证据时间、置信度、冲突与缺口。只有用户要求更新数据，或现有证据不足以支撑目标格式时，才补充检索并标明新增内容。

## 主流程

1. 确定目标场景、用户群体、生命周期、地域、时间范围和 `DEM-*` 功能编号。
2. 判断任务是场景全景、需求卡片、机会长名单，或它们的组合。
3. 先获取原始证据、用户原话和样本说明，再生成标签、主题、评分和建议。
4. 只有样本量、统计周期、去重与归一化方法明确时，才生成频次、占比、热度或强度数字。
5. 竞品功能覆盖、用户口碑和体验评分分开记录；不用“功能存在”代替“用户满意”。
6. 未来场景、出现时间、需求优先级和机会等级写入 `inferences`，列明依据、方法和假设。
7. 用户原始表述逐字保存并指向来源；不润色后冒充原话。
8. 生成 `facts / inferences / gaps / provenance / run_manifest`，再运行 `python scripts/validate_bundle.py <bundle.json>`。
9. 验证通过后，使用当前环境可用工具生成用户要求的 JSON、Markdown、Excel、网页或汇报，不依赖交付 Skill。
10. 场景反馈、收藏或入库仅在用户明确授权时执行；可按需运行 `init_store.py`、`store_bundle.py` 和 `query_store.py`。

## 量化和证据底线

- 没有原始样本时，不生成“提及频次”。
- 不同渠道的样本量不可直接相加，除非给出归一化方法。
- 需求强度和热度属于推断，必须附 `method` 和 `basis_ids`。
- 满意度量表、时期或样本不同时分开呈现。
- 用户人群占比必须有样本定义；定性画像标签标为推断。

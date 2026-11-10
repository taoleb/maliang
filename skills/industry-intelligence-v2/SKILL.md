---
name: industry-intelligence-v2
description: "汽车产业情报v2独立版：构建产业核心卡、产业链、发展阶段、市场趋势、头部与新兴企业、研究机构以及进入壁垒。用户提到产业结构、上下游、发展阶段、规模、参与者、产业图谱、排名或壁垒时使用。"
metadata:
  maliang:
    emoji: "🏭"
    always: false
  version: 0.3.2
  hermes:
    tags: [industry, value-chain, market-stage, barriers, automotive, standalone, v2]
    category: intelligence-v2
    standalone: true
    requires_toolsets: [terminal, files]
---

# Industry Intelligence v2

本 Skill 独立处理 10 个 `IND-*` 功能。

## 资源路由

- 先在 `references/function-requirements.md` 定位命中的功能编号和完整功能要求。
- 产业核心卡、产业链、阶段、参与者和壁垒字段见 `references/workflows.md`。
- 产业档案、专家研究、专利、政策和公开来源路径见 `references/source-routing.md`。
- 结构化证据、时效与冲突处理见 `references/bundle-contract.md` 和 `references/source-governance.md`。
- 只有用户明确要求保存或入库时，才读取 `references/local-store.md`。

## 交付形式

- 默认以 Markdown 交付分析结果；用户未指定其他形式时，不主动生成网页或 PPT。
- 用户在后续追问中可选择“交互式网页”或“PPT”。这是对当前情报结果的输出模式切换：仅要求换格式时复用既有结论与证据，不重新开展完整检索。
- 交互式网页应产出可打开的网页文件，并按内容需要提供搜索、筛选、图表或详情联动；PPT 应产出可演示的 `.pptx` 文件，而不是只给大纲。
- 转换后保留核心结论、数据口径、来源引用、证据时间、置信度、冲突与缺口。只有用户要求更新数据，或现有证据不足以支撑目标格式时，才补充检索并标明新增内容。

## 主流程

1. 明确 `IND-*` 功能编号、产业定义、边界、分类口径、地域和统计周期。
2. 产业档案按企业×节点粒度使用时，先确认企业和节点，不把单家企业档案当作产业汇总。
3. 从多个档案、专家研究和公开来源组装产业链，分开事实与综合判断。
4. 产业链节点使用稳定 ID，记录上下游关系、价值活动、输入输出、代表企业和来源。
5. 发展阶段基于商业化、渗透率、增速、标准监管、供应链、成本曲线和企业进退等可观察指标；阶段结论写入 `inferences`。
6. 市场规模或长期预测记录基准年份、起始值、样本范围、假设、方法和区间；没有依据时不预测。
7. 头部和新兴企业清单声明排名/筛选规则、指标、数据周期和缺口，不只输出结果名单。
8. 研究机构记录优势方向、代表成果和公开对接渠道；个人联系方式缺失时留空。
9. 壁垒事实、形成原因、量化门槛和已跨越案例分开；量化值必须附单位、条件、时间和来源。
10. 生成统一情报包并运行 `python scripts/validate_bundle.py <bundle.json>`；验证通过后用当前环境工具交付。
11. 仅在用户明确授权时执行入库或其他写入动作。

## 证据底线

- 市场规模和机构排名口径冲突时保留地域、统计对象和预测/实际差异。
- 专利可以支持技术方向和代表性资产，不能在缺少聚合口径时代替市场份额或精确总量。
- 案例成功不等于方法对所有企业可复制。

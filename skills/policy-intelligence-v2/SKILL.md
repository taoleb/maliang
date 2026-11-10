---
name: policy-intelligence-v2
description: "汽车政策情报v2独立版：检索政策档案、保留政策原文摘录、提取支持/约束/量化条款，并形成产业引导方向。用户提到政策、法规、文号、发文机关、政策效力、补贴、准入、核心条款或政策对产业的影响时使用。"
metadata:
  maliang:
    emoji: "📜"
    always: false
  version: 0.3.2
  hermes:
    tags: [policy, regulation, clause, industry-guidance, automotive, standalone, v2]
    category: intelligence-v2
    standalone: true
    requires_toolsets: [terminal, files]
---

# Policy Intelligence v2

本 Skill 独立处理 4 个 `POL-*` 功能。

## 资源路由

- 先在 `references/function-requirements.md` 定位命中的功能编号和完整功能要求。
- 政策档案、原文摘录、产业引导和核心条款的字段见 `references/workflows.md`。
- 政策库、发布机关、专业解读和降级路径见 `references/source-routing.md`。
- 结构化证据和冲突处理见 `references/bundle-contract.md` 与 `references/source-governance.md`。
- 只有用户明确要求保存或入库时，才读取 `references/local-store.md`。

## 交付形式

- 默认以 Markdown 交付分析结果；用户未指定其他形式时，不主动生成网页或 PPT。
- 用户在后续追问中可选择“交互式网页”或“PPT”。这是对当前情报结果的输出模式切换：仅要求换格式时复用既有结论与证据，不重新开展完整检索。
- 交互式网页应产出可打开的网页文件，并按内容需要提供搜索、筛选、图表或详情联动；PPT 应产出可演示的 `.pptx` 文件，而不是只给大纲。
- 转换后保留核心结论、数据口径、来源引用、证据时间、置信度、冲突与缺口。只有用户要求更新数据，或现有证据不足以支撑目标格式时，才补充检索并标明新增内容。

## 主流程

1. 确定 `POL-*` 功能编号、政策主题、地域、机关、效力状态、产业分类和截止日期。
2. 选择最少充分来源；搜索只用于发现候选，通过详情、原文或法定数据库确认标题、文号、机关、日期和效力。
3. “全量”只指本次已声明的数据源和筛选范围；没有覆盖率证明时不声称穷尽所有政策。
4. 摘录条款时保留逐字原文、条款/页码位置和政策文号，总结与解读另存。
5. 条款按支持、约束和量化指标分类；量化值拆分为 `value / unit / condition / deadline`。
6. 产业引导方向属于 `inferences`，必须引用具体条款 ID，不只引用政策标题。
7. 政策有效、废止、修订或过渡状态都必须有截至日期和官方依据；无法核验时使用 `candidate` 并建立 `gap`。
8. 生成 `facts / inferences / gaps / provenance / run_manifest`，再运行 `python scripts/validate_bundle.py <bundle.json>`。
9. 验证通过后，使用当前环境可用工具生成用户要求的结果，不依赖交付 Skill。
10. 上传、编辑、关联报告、替换关联、附件下载或入库只在已提供对应工具且用户明确授权时执行。

## 边界

- 政策解读不是政策原文。
- 新闻转述和搜索摘要只能作为候选线索。
- 海外政策优先使用发布机关或法定数据库原文。
- 政策对企业的战略影响属于推断，与政策事实分开。

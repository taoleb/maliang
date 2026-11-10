# 资本情报工作流

## 投资主体 CAP-INVESTOR

投资机构档案：

```text
investor_id / canonical_name / organization_type / registered_capital
headquarters / shareholders / key_personnel / assets_under_management
investment_count / exit_count / data_as_of / source_ids
```

历史投资事件使用统一 `investment_event_id`。地域分布、赛道分类、金额分布和时间分布都声明样本范围及缺失金额处理。

## 融资主体与事件 CAP-INVESTEE / CAP-EVENT / CAP-FLOW

事件结构：

```text
event_id / company_id / announcement_date / closing_date
round_raw / round_normalized / amount / currency
pre_money_valuation / post_money_valuation / investors
track / geography / source_ids / review_status
```

### 去重

首选事件ID；没有时使用规范化键：

```text
company_id + round_normalized + date_window + normalized_amount + lead_investors
```

日期相近、金额相同、核心投资方相同的转载先合并为候选事件，再人工或规则确认。

### 聚合

- 不披露金额的事件计入事件数，但不计入金额合计。
- 平均单笔只用已披露金额事件，并显示分母。
- 跨币种统计需记录汇率日期和汇率来源。
- 同比/环比要求可比期间和相同样本规则。

## IPO CAP-IPO

状态机：

```text
筹备 → 辅导 → 受理 → 问询 → 回复 → 过会 → 注册 → 发行 → 上市
                                ↘ 中止 / 终止 / 撤回
```

每个状态事件记录交易所、板块、日期、公告ID和来源。当前状态由最新有效状态事件推导，不覆盖历史节点。

问询与回复分轮次保存；问题摘要和回复摘要属于总结，原文链接或文档ID必须保留。

## 车企资本运作 CAP-AUTO

融资、定增、并购、发债、换股和资产重组分开分类。记录：

- 运作主体和标的
- 对价类型、金额、股份和资产估值
- 运作前后股权快照
- 新增/退出股东和控制权变化
- 业绩承诺与对赌条款
- 资金用途和状态

运作意义、协同和风险属于 inference。


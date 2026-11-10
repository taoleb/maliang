# 竞争情报工作流

## COM-STR 战略

记录愿景、目标、规划原文、战略举措和调整事件。战略规划摘录保留原文和来源位置；战略定位和影响判断写入 inference。

调整事件结构：

```text
event_id / enterprise_id / announcement_date / effective_date
before / change / after / scope / status / source_ids
```

## COM-PROD 产品

产品和车型使用稳定ID，记录集团、品牌、细分市场、版本、上市时间、价格期间、动力、智驾、座舱、电池、续航和来源。

- 配置按版本和地区比较。
- 发布、预售、上市、交付分开记录。
- 市场反馈区分销量、专业测评和用户口碑。
- 收费模式和推广策略缺少证据时不套用互联网产品模板。

## COM-IND 产业布局

每个动作关联到产业链节点：投资、自建、采购、合作、并购、供应或生态接入。签约、开工、投产、扩产和停产使用不同状态。

## COM-JV 合作

```text
event_id / enterprise_id / partner_id / cooperation_type
field / announced_at / effective_period / equity_ratio
investment_amount / currency / status / last_verified_at / source_ids
```

合作状态：传闻、宣布、签约、推进、落地、暂停、终止。状态变化保留时间轴。

## COM-TECH 技术研发

记录技术名称、版本、时间、能力、应用场景、研发投入、机构和代表性专利。技术发布不等于量产应用，分别建立事实。

研发投入注明会计期间、币种、是否资本化及营收占比口径。

## COM-FIN 经营财务

```text
metric_id / enterprise_id / metric / value / unit / currency
period_start / period_end / geography / channel / product_scope
accounting_or_sales_basis / source_ids
```

销量口径：批发、零售、交付、上险、出口。财务口径以公告或财报为主。市场份额必须说明市场定义和分母。

禁止把AI搜索结果未经验证直接写成verified事实；自动任务先进入candidate或审核队列。

## COM-GLO 全球化

记录国家/地区、进入方式、品牌、产品、渠道、合作方、工厂、产能、状态、销量、份额和本土化动作。

需要地图或仪表盘时，使用当前环境可用的文件或可视化工具渲染；本 Skill 先生成结构化国家和地点字段，不假装已有生产页面。

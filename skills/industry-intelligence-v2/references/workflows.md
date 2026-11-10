# 产业情报工作流

## IND-STRUCT-001 产业核心信息卡

```text
industry_id / canonical_name / definition / boundary
enabling_technologies / key_resources / value_activities
user_needs / application_scenarios / classification / source_ids
```

核心逻辑句是总结性 inference，不替代字段事实。

## IND-STRUCT-002 产业链

节点：

```text
node_id / name / layer / activity / inputs / outputs
representative_entities / value_share / geography / source_ids
```

边：supplier_of、enables、integrates、distributes_to、serves。价值占比只有在口径和来源明确时填写。

## IND-STRUCT-003 发展阶段

阶段：导入、成长、爆发、成熟、衰退。判断至少考虑：

- 商业化和渗透率
- 市场增速
- 标准和监管
- 供应链成熟度
- 成本曲线
- 企业进入和退出

阶段判断属于 inference，引用观察事实。未来15年预测不是默认必填；有可靠基准和假设时才生成区间。

## IND-STRUCT-004~006 参与者

头部企业排名可按市场份额、营收、出货量或关键环节份额，但必须统一指标。新兴企业可按成立时间、融资、技术或增长选择，说明规则。

研究机构记录优势方向、代表成果和公开对接渠道。个人联系方式缺失时留空。

## IND-BARRIER 壁垒

标准类型：技术、资金、资质、渠道、品牌、规模经济、政策、人才、资源、网络效应。

量化门槛：

```text
barrier_id / type / metric / value / unit / condition
equipment / infrastructure / certification / lead_time / source_ids
```

案例记录企业、时间、方式、动作、投入、效果和可复制边界。案例成功不代表所有企业都能复制。


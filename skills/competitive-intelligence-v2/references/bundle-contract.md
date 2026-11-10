# 统一情报包协议

## 顶层结构

```json
{
  "schema_version": "2.0",
  "run_id": "20260825-competitive-byd-001",
  "domain": "competitive",
  "request": {},
  "facts": [],
  "inferences": [],
  "gaps": [],
  "provenance": [],
  "run_manifest": {}
}
```

## request

| 字段 | 含义 |
|---|---|
| `query` | 用户原始请求 |
| `subject` | 研究对象 |
| `function_ids` | 功能目录编号 |
| `requested_as_of` | 用户要求的数据截至日期 |
| `output_format` | json/markdown/excel/html/ppt |
| `write_authorized` | 是否明确允许写入 |

## provenance

每个来源必须有稳定 `source_id`。

| 字段 | 含义 |
|---|---|
| `source_id` | 本次运行内唯一ID |
| `source_type` | internal_card/mcp_detail/official_document/web_page/search_snippet |
| `title` | 来源标题 |
| `url` | 脱敏后的URL，可空 |
| `raw_ref` | 条目ID、卡片ID、文号或专利号 |
| `published_at` | 来源发布日期，可空 |
| `retrieved_at` | 获取时间 |
| `evidence_level` | primary/detail/search_snippet |
| `source_scope` | internal_direct/benchmark/external_context/public |

鉴权参数不得进入 `url`。

## facts

| 字段 | 含义 |
|---|---|
| `fact_id` | 运行内唯一ID |
| `subject` | 事实主体 |
| `predicate` | 指标或关系名称 |
| `value` | 字符串、数字、数组或对象 |
| `unit` | 单位，可空 |
| `period_start`/`period_end` | 统计期间，可空 |
| `as_of` | 事实有效或确认日期 |
| `source_ids` | 一个或多个 provenance ID |
| `confidence` | 0到1 |
| `review_status` | candidate/verified/rejected |
| `scope` | internal_direct/benchmark/external_context/public |
| `notes` | 口径和限制 |

同一指标如果存在批发、零售和交付等不同口径，建立不同 fact，不覆盖。

## inferences

| 字段 | 含义 |
|---|---|
| `inference_id` | 唯一ID |
| `subject` | 推断对象 |
| `conclusion` | 结论 |
| `basis_ids` | 支撑它的 fact_id 或 source_id |
| `method` | 评分、趋势、比较或预测方法 |
| `confidence` | 0到1 |
| `assumptions` | 关键假设 |

市场规模预测、需求热度、机会等级、下一阶段时间和战略判断都属于 inference。

## gaps

| 字段 | 含义 |
|---|---|
| `gap_id` | 唯一ID |
| `field` | 缺失字段 |
| `reason` | unavailable/not_found/conflict/insufficient_sample/not_authorized |
| `detail` | 具体说明 |
| `next_action` | 建议核验动作 |

## run_manifest

必须包含：

```json
{
  "started_at": "",
  "completed_at": "",
  "data_as_of": "",
  "used_tools": [],
  "unavailable_tools": [],
  "disabled_tools": [],
  "failed_calls": [],
  "validation_status": "pending"
}
```


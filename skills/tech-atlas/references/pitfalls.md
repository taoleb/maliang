# 踩坑清单（动手前必读）

本流水线迭代 9 轮踩过的全部坑与解法。写代码前先扫一遍，能省大量返工。

## Python / 数据

1. **保留字做字典键**：`dict(def=...)` 报 SyntaxError（def 是保留字）。→ 全部改用 `dfn`，同步改所有 `kb["def"]` 引用。
2. **嵌套游标失效**：同一 `conn.cursor()` 在遍历一个结果集时再执行查询，外层迭代会被截断（表清单只打印一行）。→ 先 `.fetchall()` 再遍历，或每查询新建 cursor。
3. **os.remove 被沙箱拦截**：重建数据库想先删旧文件会被安全策略拦截。→ 改用 `DROP TABLE IF EXISTS` + `CREATE TABLE` 原地重建。
4. **openpyxl 打开 xlsx**：本地 editor_sdk MCP 打不开该 xlsx（报 No workbook open），sheetagent 表格工具未加载。→ 降级 `openpyxl.load_workbook(path, data_only=True)` 直读。

## SQLite / 检索

5. **FTS5 不切中文**：默认 unicode61 分词器把中文当整体，"量子"匹配为 0；trigram 要求查询词 ≥3 字符。462 行规模根本不需要 FTS。→ 直接用 `LIKE '%kw%'`，毫秒级。
6. **旗舰关联键不一致**：`ref_flagship` 存了内部键名（如 "ssb"）但 flagship_atlases 注册的是显示名（"固态电池"），关联查询失败。→ 用 FLAG_MAP 把清单名映射为旗舰显示名。
7. **独立旗舰不在清单内**：太比特量子通信 / 量子通信是旗舰图谱，但不在 462 项清单里，tech_atlas 直接查报"未找到"。→ 解析链加第 3 级：flagship_atlases 精确名。
8. **模糊匹配抢占**："量子通信"被清单里"量子通信车载化"的 LIKE 先命中。→ 旗舰表精确命中必须优先于 technologies 模糊匹配。

## Windows / 编码 / 路径

9. **管道大 payload EINVAL**：文本模式管道写大 UTF-8 JSON 报 EINVAL。→ server 内 `sys.stdin.reconfigure(encoding="utf-8")` + `sys.stdout.reconfigure(encoding="utf-8")`，并设 env `PYTHONIOENCODING=utf-8`。
10. **Git Bash 路径 Python 不认**：`/tmp/xxx` 在 Python 里被解析成不存在的 `C:\tmp\xxx`。→ 传 Windows 盘符绝对路径（如 `C:/Users/.../xxx`），勿用 `/tmp`。
11. **双副本漂移**：根库 tech-atlas.db 更新了但 MCP 读的是 tech-atlas-mcp/ 下的旧副本。→ 改完 `cp -f` 覆盖 + `md5sum` 两份校验一致。

## JS / 页面

12. **eval 拿不到 const**：`eval(script)` 后访问脚本里的 `const` 绑定会 ReferenceError（块作用域不外泄）。→ 把测试 harness 拼进同一段脚本文本一起 eval。
13. **生成数据契约缺陷**（首跑必查）：
    - `g8.items` 必须 7 元素、`g8.donut` 占比合计 ≈100
    - `r3.gens` 年份必须单调不减——新近技术（origin 2023）代际边界会反转（2023→2022），需强制 `max()` 保证单调
    - TRL 柱高要 clamp 防溢出 SVG；g1 星系边索引必须 < nodes 长度，避免孤立节点
14. **CSS 类缺失**：新渲染器用了 `.sc/.sc-h` 但旧 CSS 没有该类。→ 补定义，否则样式塌。
15. **DOM id 缺失**：简况弹窗引用的 `lzName/lzEn` 等 id 没写进 HTML。→ 补全 DOM。
16. **meta 统计口径**：`flagship_linked` 按 `ref_flagship` 非空计数 = 5（清单内关联行），不是旗舰总数 6。别混淆。
17. **SVG marker 随线宽放大**：`<marker>` 默认 `markerUnits=strokeWidth`，线宽 6 的粗线箭头会放大 6 倍成巨大三角。→ 所有 marker 必须显式 `markerUnits="userSpaceOnUse"`。
18. **SVG 文字叠压**：多标签图表（地铁瓶颈、hype 定位、族谱树）标签互相叠字。→ ① 标签加白描边 `stroke="#fff" stroke-width="4" paint-order="stroke"`；② 成对标签交错行距 ≥30px；③ 族谱树每代固定独立行高（ROWY=[64,150,236,322]）；④ 右侧边缘标签用 `text-anchor="end"` 防裁切。
19. **生成脚本变量遮蔽**：gen_full.py 里有局部函数 `pick()`，新增同名变量会触发 UnboundLocalError。→ 新变量避免与既有局部函数/变量同名。
20. **融合饼撞色**：g8 小饼两色若与自身色 c 相同会变成纯色圆。→ 配色池先排除自身色再逐项去重。
22. **横向时间轴类模块遮挡通病**（R1/R2/P4/G5/G7 第 11 轮）：① 事件标签同年簇横向互叠 → 同侧（上/下）按 X 序贪心右移避让，标签右缘 clamp 到 `W-8`；② 时间轴左缘空白（y0=origin-10 过松）→ R1 `y0r=max(1976,origin-2)`、X 映射左右各留 90 内边距；③ 右缘裁切（「现在」/乐观悲观标签/末事件）→ 右界 `Math.max(2026, …gens/genLast/events)`，标签 `slice(0,22)` 且数据侧按标点截断 `cut_at_punct` 防半句话；④ 后绘元素遮字（G5 概率柱盖住「保守/激进估计」）→ 标签移到柱之后绘制并白描边；⑤ 注释文字被曲线穿过（P6「⑂ 换乘 hub」）→ 移到曲线起点左侧 + 白描边；⑥ 小节点文字穿圈（G7）→ 白描边。
23. **导出数据结构差异**（导出表格/PPT 时）：① 生成数据与旗舰手写数据的 `g8.items` 结构不同——生成版第 5 元素是比例串（"35:35"），旗舰版第 5 元素是色值（"#7c5cff"）→ 摘要提取必须双结构兼容（比例从第 2 元素百分比数组兜底）。② 旗舰 `g1.gal.macro.nodes` 描述语不含"上游/行业"关键词 → sum_g1 兜底取非当前技术节点名。③ p2.ms 等数组可能混入 None → 一切遍历前用 `items()` 过滤空项。④ `--techs` 模糊匹配连带子串条目（"量子通信"带出车载化）→ 精确优先；清单外旗舰名在 PPT 侧补虚拟条目。⑤ PPT 里 R3 代际标签若直接放在色条下方会上下叠 → 改「单行比例色条 + 双列图例」布局。

## 云端服务 / 每日流水线（6600→6622）

24. **SPA 前端探测陷阱**：6600 是 Vite SPA，任意路径都返回 index.html（200），`/openapi.json`、`/docs` 拿到的其实是 HTML。真正后端在 `/api/*`（FastAPI，403 "Not authenticated" 才说明后端活着）。探测接口结构要读前端源码 `/src/api/index.js`、`/src/pages/*.vue`（dev server 直接可下），别猜后端路径。
25. **curl 中文参数 GBK 乱码**：Git Bash 里 `curl -d '{"name":"固态电池"}'` 发出去是 GBK 字节，服务端按 UTF-8 解析报 `'utf-8' codec can't decode byte 0xb9`——这是**客户端**编码问题不是服务问题。测试一律用 Python `urllib.request` + `json.dumps(...).encode('utf-8')`。
26. **登录字段要实测**：FastAPI OAuth2 常见是 form 表单，但该系统是 JSON `{username,password}` → `{access_token}`。写登录代码前先从前端 Login 组件确认载荷格式，token 字段名做多路兼容（access_token/token/data.*）。
27. **分页结构兼容**：6600 列表页前端自己兼容 `items/results/list/数组` 四种结构，说明后端可能有版本差异。拉取端用 `normalize_items()` 多键探测，别写死单一键。
28. **ingest 去重键**：`daily_intel.intel_id` UNIQUE（格式 `6600-<源id>`），重复 push 靠 IntegrityError 计数跳过——自动化任务重跑/补跑是安全的，不会产生脏数据。
21. **R3 族谱树代际重合**（第 10 轮用户反馈）：① 数据侧——旧公式 `g2y=min(origin+8,2022)` 对新近技术（origin≥2018）把三代挤成 1 年段（"存续 0 年"条不可见）；右界 `min(2033,…)` 又把新窗口技术的第三代截断。→ 改为按技术自身生命周期比例切分：`total=max(9,win_y+2-origin)`，`g2y=origin+round(total*0.4)`、`g3y=origin+round(total*0.7)` 且 `g3y≥g2y+3`，右界 `end_y=max(2030,min(2036,max(win_y+2,g3y+3)))`；并保证每代 `b-a≥2`，R1 的 gens/genNote 与 R3 共用同一切分点。② 渲染侧——旧 `ROWY` 固定 4 行，旗舰 5 代（太比特量子通信）第 5 代与第 4 行重叠；根分支贝塞尔曲线交叉穿字；⚡ 更替标签与代际名称/年份标签互叠。→ 行 Y 按 `gens.length` 动态等分；根改左侧竖直干线 + 水平进线（不交叉）；⚡ 圆圈钉在代际条起点、标签统一收入底部事件栏并做水平避让（先画引线后画带白描边标签）；行内补「年份区间」+ 底部时间轴刻度 + 「现在」参照线。R1 长卷右界也要 `Math.max(2026, …gens/genLast/events)` 防截断。
24. **交付提示遗漏**（第 12 轮用户反馈）：生成交付后若不在最终回复里主动提示"可派生 PPT/表格"，用户会误以为不支持。→ 硬规则 8 交付提示协议：任何交付后必须追加可选导出提示段，宁可多说不可漏说。
25. **sqlite3.connect 静默建空库**：`sqlite3.connect(不存在路径)` 不报错而是创建 0 字节空库，后续查表报 `no such table`。MCP 远程模式校验函数务必先 `os.path.exists() and size>=1024` 再连库，绝不把不存在路径当有效库。
26. **远程模式缓存复用**：云端不可达时应依次回退 上次缓存 → 本地库，不能直接抛错中断 MCP 服务；`tech_stats.data_source` 标明实际来源便于排查。

## 流程

17. **未收录即生成**：用户点任何技术，库里没有就立即 WebSearch + 生成 17 模块纳入，禁止推诿话术。
18. **交付前三件套**：node --check 语法 → 全字段契约校验 → 无头冒烟全部 462 项 renderAtlas 0 异常。三件全绿才可 present_files。

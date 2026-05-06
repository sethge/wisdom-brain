# SKILL — 操作技能手册

> SKILL是四肢，负责怎么动手。所有诊断逻辑、判断标准、决策路径在BRAIN.md（大脑）。
> SKILL只管：怎么爬数据、怎么连后台、怎么出PDF、怎么对比数据。

最近更新：2026-05-06（拆分：诊断逻辑迁入BRAIN，SKILL只留纯操作技能）

---

## 1. 数据采集

**S-1** 每次采集前自检：
- 平台建议 vs 事实数据（推广页数据可能不完整）
- 子产品花费 vs 总花费
- 新客数据 vs 老客数据（第一件事必须拆）
- 营业时间：核实实际时间，不能用系统默认/特权建议当事实

**S-2** 推广数据采集完整性自检：
- 点金/推广花费要到分产品层级核实，不能只看总花费
- "没有推广"的结论前必须验证推广页数据是否完整采集

**S-3** 后台"比商圈同行均值X%"的读取规则：
- 百分比指标（进店率/下单率）：差值，高出Xpp
- 绝对值指标（月售/客单价）：均值绝对数
- 抓数据时必须看清楚，一个数字看错导致整条分析链错误

**S-4** 新老客数据采集路径（美团）：
- 路径：商家后台 → 经营分析 → 顾客管理
- 选时间：近7日（日常监测） / 近30日（月度完整）
- 拿数据：下单人数总 / 新客人数+占比 / 老客人数+占比 / 复购率% / 复购人数
- 验证：新客+老客 ≈ 下单总人数（有小差异正常）
- 补充看：下单频次分布（同页面），确认"1次买家占比"判断复购体验

**S-5** 商圈均值 vs 前10% 数据采集：
- 路径：商家后台 → 经营分析 → 各数据卡片内（进店率/下单率/客单等都有）
- 每个卡片展示三个值：本店 / 商圈均值 / 商圈前10%
- 读法区分：
  - 百分比指标（进店率/下单率/复购率）：单位是pp，差值比较。例："高出1.33pp" = 本店10.13% vs 均值8.80%
  - 绝对值指标（月售/客单价）：均值给出的是绝对数字，不是百分比
- 商圈排名格式："10/69（超越85.5%）"，分母是商圈总店数

**S-6** 新老客漏斗分别采集（进店率/下单率拆分）：
- 路径：商家后台 → 经营分析 → 访客漏斗 → 切换"新客"/"老客" tab
- 分别记录：新客（曝光→进店率→下单率），老客（曝光→进店率→下单率）
- **Playwright操作方式**（来源：crawl_xianghu.py 20260420）：
  - 连接Chrome CDP：`curl --noproxy localhost http://localhost:9222/json/version` 取 webSocketDebuggerUrl
  - 找frame：遍历 `browser.contexts → pages → frames`，匹配 `waimaieapp.meituan.com` + `flowrate` + `token=`
  - 切时间：`frame.locator("text=近30日").first.click()`
  - 切新客/老客tab：`frame.locator(f"text={tab_name}").first.click()`（tab_name = "全部顾客"/"新客"/"老客"）
  - 切前10%：点第二个 `.roo-input-group.has-icon` 下拉 → 找 `.roo-popup` 里的 "商圈同行前10%均值" 选项点击
  - 备选JS：`document.querySelector('.roo-popup')` 遍历子元素匹配文本点击
  - 读数据：`frame.evaluate("() => document.body.innerText")` 按行解析，找"流量转化"开头截取

**S-7-1** 美团后台导航路径（e.waimai.meituan.com版本）：
- 首页 → 点侧边栏"经营分析" → 点"经营数据" → waimaieapp frame加载
- frame0 = 侧边栏，**frame1 = 内容区**（用frame1读数据）
- 内容区顶部tab：总览/行业/营收/流量/推广/营销/顾客/服务/商品
- 顾客tab：全部顾客/新客/老客 切换，可看复购率拆分
- 流量tab：全部顾客/新客/老客 切换，可看漏斗数据
- 下拉可切"商圈同行均值"/"商圈收入前10%同行均值"

**S-7-2** 数据采集完毕后必须关闭后台页面。
- `await close_store_pages(ctx)` （plugin_helper.py）
- 不关页面会影响下次登录其他店铺

**S-8** 满减活动当前档位采集路径（美团）：
- 路径：活动中心 → 我的活动 → 自营销活动 tab → 现有活动
- 列表直接显示：活动类型 / 活动详情预览（满X减Y | 满X减Y...）/ 前7日销量
- 不要去"自营销活动"页点卡片（有嵌套iframe问题），直接走"我的活动"最快
- **Playwright操作方式**（来源：crawl_xianghu_manjian.py 20260420）：
  - 找美团后台page：遍历contexts→pages，匹配 `waimaieapp.meituan.com` 或 `e.waimai.meituan.com`
  - 点活动中心：JS遍历所有元素找 `textContent.trim() === '活动中心'` 且 `children.length <= 2` 且 `offsetParent` 存在
  - 找活动frame：遍历 `page.frames`，匹配 `waimaieapp.meituan.com`，取 `body.innerText` 长度 > 50 的
  - 读数据：`frame.evaluate("() => document.body.innerText")` 按行过滤含满/减/活动/折扣/优惠/券/神抢手等关键词

---

## 2. 悟空(Gouku)插件登录

**G-1** 完整流程：

```python
# 0. 环境准备：必须绕过代理
import os
for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY']:
    os.environ.pop(k, None)
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# 1. 连接Chrome CDP
from playwright.async_api import async_playwright
p = await async_playwright().start()
browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
ctx = browser.contexts[0]

# 2. 找悟空插件页面
import sys; sys.path.insert(0, os.path.expanduser("~/Downloads/store-monitor"))
from plugin_helper import get_ext, pick_brand, get_stores, click_store_platform, close_store_pages

ext = await get_ext(ctx)

# 3. 选品牌（搜索+选择）
ok, status = await pick_brand(ext, "湘湖知味")  # 品牌名

# 4. 获取店铺列表
stores = await get_stores(ext)
# stores = {"店名": [{"platform":"meituan","account":"mt501330hb","action":"一键登录"}, ...]}

# 5. 点击登录（参数是account值，不是品牌名！）
for name, accs in stores.items():
    for acc in accs:
        if acc["platform"] == "meituan":
            result = await click_store_platform(ext, acc["account"])  # 只传2个参数！
            # result: 'ok' / 'need_auth' / 'not_found'
```

**G-2** 常见错误：
- `click_store_platform(ext, brand, 'meituan')` ← **错！只有2个参数：ext和account**
- 忘记绕过代理 → CDP连接502 Bad Gateway
- 每次新Playwright连接前要 `pkill -f "playwright"`，否则端口冲突
- 采完数据要 `await close_store_pages(ctx)` 关闭后台页面

**G-3** 美团后台导航（登录后）：
- 侧边栏点"经营分析"展开 → 点"经营数据" → waimaieapp iframe加载
- frame结构：frame[0]=主页面(含侧边栏), **frame[1]=内容区**(读数据用这个)
- 内容区顶部tab：总览/行业/营收/流量/营销/顾客/服务/商品/推广/拼好饭/神抢手
- 直接导航：`await page.evaluate("window.location.hash = '#https://waimaieapp.meituan.com/igate/bizdata/product'")`
- tab内点击用JS：`biz.evaluate("() => { ... el.textContent.trim() === '商品' ... el.click() }")`
- 展开明细会弹出 `roo-drawer-portal` 抽屉，里面有SVG图表

---

## 3. 截图标注

**A-1** 两种方式混合使用（6张/份）：
- **精确框**（3张）：关键数字——评分/月售/差评数
  - 2轮验证法：裁大块确认y范围→find_text_blocks精确坐标+verify_crop验证
  - 控制在2轮内，不反复校准
  - 标签写诊断结论，不重复文字
- **总结条**（3张）：展示性内容——差评区/引流品区/展示品
  - 裁出区域+底部彩色诊断总结栏
  - 零偏移，低token消耗

**A-2** 颜色语义：
- 红(200,50,40) = 问题
- 蓝(30,120,200) = 信息
- 绿(30,150,50) = 优势
- 橙(255,150,30) = 警告

---

## 4. 数据对比

**C-1** 单品对比必须控制全量趋势：
- 不能只看单品绝对值变化（可能全店都涨/跌）
- 正确做法：算该品占全店销售额的占比变化，占比提升才说明单品表现优于全店

**C-2** 时间对比要同比不要环比（排除周期性）：
- 周一和周日不能比 → 要周一和上周一比
- 如果样本天数<7天，无法排除周周期，结论标注"待继续观察"

**C-3** 最小有效样本：
- 日均变化需要至少14天才有统计意义
- 4-5天的数据只能说"初步趋势"，不能下结论

**C-4** SVG图表数据提取方法：
- 美团后台商品详情图表是SVG渲染
- 从 `roo-drawer-portal` 读取SVG path的d属性
- Y轴刻度从text元素读（如 0/200/400/600/800 对应y坐标）
- 用线性插值反算每天数值：`value = (y_max - y) / (y_max - y_min) * scale_max`

**C-5** 区分"原有商品"和"新增商品"：
- 不能假设TOP排名里的商品是新增的，必须找"新品"标签、上架日期等证据
- 美团后台总览页"仅看新品"开关可以过滤新品

**C-6** 满减改动效果分析方法：
- 看实付单均价变化（门槛降低→单均价可能降）
- 看订单量变化（更多人触发→订单量增）
- 看营业收入变化（量x价的净效果）
- 看到手率变化（营业收入/优惠前总额）
- 综合判断：订单量增但单均价降，要算总营收是正还是负

**C-7** 美团后台API拦截法取日营收趋势数据：
- 场景：需要逐日营收数据做前后对比
- 关键API：`POST /gw/bizdata/renew/business/overview/trend` 返回日营收列表
- 返回格式：`data` = list of `{desc: "2026-04-15", index: "settleAmount", current: 1841.02, circle: 1117.53}`
  - `current` = 本店当日营业额，`circle` = 商圈均值
- 操作步骤：
  1. 先导航到经营数据商品页：`page.evaluate("window.location.hash='#.../bizdata/product'")`
  2. 再切回总览tab（dispatchEvent方式）
  3. 注册响应监听：`page.on('response', handler)` — handler过滤URL含'trend'+'overview'
  4. 点击日期tab触发请求
  5. 等待4秒收数据，移除监听
- 注意：`.selector-item`用普通click，tab用`dispatchEvent`（普通click不生效）

**C-8** 美团后台商品销售数据分页采集：
- 路径：经营数据 → 商品tab → frame[1]（biz iframe）
- 读表格：`document.querySelectorAll('tbody tr')` → 提取rank/name/sales/qty
- 翻页：`.roo-pagination li` 元素，每页20条

**C-9** 美团后台满减生效日期查询：
- 路径：活动中心 → 我的活动 → 找到满减活动 → 操作记录/活动详情

---

## 5. 批量诊断E2E流程

**E-1** 完整流程（5步）：

```
步骤1：数据采集（crawl_batch.py）
步骤2：读JSON + 按BRAIN.md逻辑树分析 → 写诊断markdown
步骤3：markdown → PDF → 桌面
步骤4：播完成音
步骤5：汇报结果
```

**E-2** 步骤1：数据采集

脚本：`~/Downloads/wisdom-brain/crawl_batch.py`
输出：`~/Downloads/wisdom-brain/diagnosis-test/crawl_raw_{店名}_{日期}.json`

```bash
cd ~/Downloads/wisdom-brain && /opt/homebrew/bin/python3 crawl_batch.py
# 从第N家开始（断点续跑）：
/opt/homebrew/bin/python3 crawl_batch.py N
```

- 每家店：悟空登录→点经营分析→经营数据→遍历所有tab
- 流量tab额外切：全部顾客/新客/老客 x 商圈均值/前10%
- 行业/服务tab加载慢，已加额外等待+重试
- 采完关闭页面再登下一家

**E-3** 步骤2：诊断分析

**诊断逻辑和输出结构按BRAIN.md逻辑树执行。** SKILL不重复诊断逻辑。

并行策略：多家店可用Agent工具并行分析，每家独立一个agent，给它crawl_raw JSON路径+BRAIN.md+SKILL.md。

**E-4** 步骤3：PDF转换

脚本：`/tmp/md2pdf3.py`（markdown→HTML→Chrome headless→PDF）

```bash
/opt/homebrew/bin/python3 /tmp/md2pdf3.py
```

- 源目录：`~/Downloads/wisdom-brain/diagnosis-test/*_运营诊断_*.md`
- 输出目录：`~/Desktop/`

**E-5** 步骤4-5：完成

```bash
afplay /System/Library/Sounds/Funk.aiff
```

汇报：X家诊断完成，PDF已放桌面。列出每家店一句话核心发现。

**E-6** 参考范例：
- `~/Downloads/wisdom-brain/diagnosis-test/峨眉郑记豆腐脑_宽窄店_运营诊断_20260422.md`

---

## 6. 模糊操作方式

**SF-1** 新客立减前端展示的具体条件
- 待确认：怎样设置才能让新客立减有标签展示？

**SF-2** 分时段定价的操作方法
- 待确认：美团/饿了么后台具体怎么设置分时段折扣？

**SF-3** 满减后续档位设计
- 第一档已确认（实付x1.15/0.9，1.3倍校验）
- 待确认：第二档、第三档的递进逻辑

**SF-4** 推广数据完整采集的方法
- 待确认：完整采集推广数据的标准流程是什么？

**SF-5** 订单关联数据分析方法
- 操作：美团商家后台 → 订单管理 → 导出近7日订单明细 → 按订单ID分组 → 统计高频搭配TOP10
- 应用：套餐重设计、发现潜在组合需求

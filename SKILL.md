# SKILL — 操作技能手册

> SKILL是四肢，负责怎么动手。所有诊断逻辑、判断标准、决策路径在BRAIN.md（大脑）。
> SKILL只管：怎么爬数据、怎么连后台、怎么出PDF、怎么对比数据。

最近更新：2026-05-08（新增S-5-1/S-5-2/S-5-3数据验证规则，来自20260424 Review教训）

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
- **新店推广时间段校验**：新店可能中途才开始投推广，"近30天"数据不满月→日均花费要按实际天数算，不能除以30（牛卷凉皮案例：4月才开始投，"近30天"数据虚高）

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
- ⚠️ **必须交叉验证（S-5-1，20260424 Review教训）：**
  - 采完商圈均值后，立刻和本店数据做逻辑校验：均值不可能远高于本店排名靠前的数据
  - 曝光量：如果本店曝光4万且排名靠前，均值不可能是8万（牛卷凉皮案例：均值抓成8万，实际比本店还低）
  - 排名：采完后和"超越X%"交叉验证，"超越85%"不可能排154名（牛卷凉皮案例）
  - 转化率：下结论"低于均值"前必须先查均值实际数值，不能只看"感觉低"（牛卷凉皮案例：新客转化21%实际高于均值19.7%）
  - 读数据时确认当前选的是"商圈同行均值"还是"商圈收入前10%同行均值"，两个值差很多，不能混淆
  - 均值超过90%的指标要警惕：老客下单转化率均值97.25%不可能（饺子仙案例），说明读错了数据
  - 推广花费等累计指标要确认时间段是否满30天，新店可能4月才开始投放，"近30天"数据不满月（牛卷凉皮案例）
  - 下结论前必须有数据对比：不能说"力度很大"不给折扣率，不能说"拉低整体"不给均值数字

**S-5-2** 价格与SKU数据采集必须展开规格（20260424 Review教训）：
- 美团后台菜品管理中，同一商品可能有多规格（大/小份、鸡肉/牛肉等），价格不同
- 前端列表只显示"起步价"（最低规格价），不代表所有规格的价格
- 采集价格时必须点进商品详情看每个规格的价格，不能只看列表价
- 计算价格差时用各规格实际价格，不是起步价差（宝狮案例：鸡肉22牛肉26差4元，报告写"差2元"因为只看了起步价）
- 多渠道（主站/神枪手/掉饭粒）同一商品不算"重复SKU"（饺子仙案例：不同渠道的渠道品不是真重复）
- 运营主动拆分的SKU（如双拼拆成单品）不算"重复SKU"（牛卷凉皮案例：运营说"SKU太少所以我拆开来的"，报告反而说"重复SKU多"）
- 满减折扣率必须逐档计算：不能只说"力度大/小"，要给出具体折扣率（牛卷凉皮案例：报告说"力度很大"，运营说"九点几折，只便宜一块钱"）

**S-5-3** 客单价必须从后台取（20260424 Review教训）：
- 客单价只能从后台"经营分析→营收"tab取"商家实收客单价"，不能从前端商品价格推算
- 前端推算的客单价 ≠ 实际客单价（有活动折扣、满减、配送费等差异）
- 原始鲜语案例：前端推算客单价偏高，实际商家收入三十几块钱
- 采完客单价后和商家实收数据交叉验证

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
- ⚠️ **S-6数据解析防错规则（20260424 Review教训）：**
  - **页面结构**：流量tab的innerText中，数据分两段——第一段(行24-37)=本店，第二段(行38-44)=商圈对比。两段之间以"曝光/入店/下单"三个标签行分隔
  - 本店数据行顺序：入店转化率数值→下单转化率数值→曝光人数→曝光次数→入店人数→入店次数→下单人数→下单次数
  - 商圈数据行顺序：曝光人数→入店人数→下单人数→入店转化率→下单转化率
  - **解析后必须校验**：均值不能比本店高出2倍以上（如本店4万均值8万=读错了），转化率均值不能>95%（饺子仙案例97.25%=读错了）
  - **切tab后等够时间**：click新客/老客tab后必须sleep(5)再读数据，否则可能读到上一个tab的残留数据
  - **确认下拉选择**：读均值数据前，检查当前下拉是"商圈同行均值"还是"前10%"，两个值差几倍

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

## 2. 悟空(Gouku)插件 — 从零进入一家店的完整流程

### G-0 Chrome启动（最容易出错的一步！）

**Chrome 147+ 要求：CDP必须用非默认user-data-dir，否则报错"DevTools remote debugging requires a non-default data directory"**

```bash
# 正确的启动方式（browser.py里的配置）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug" \
  --load-extension="$HOME/Downloads/store-monitor/goku" \
  --no-first-run \
  --no-default-browser-check \
  --proxy-server="direct://" \
  2>/dev/null &
```

**关键参数：**
- `--user-data-dir=~/chrome-debug` — 不是`~/Library/.../Google/Chrome`，不是`/tmp/xxx`，就是`~/chrome-debug`
- `--load-extension=.../goku` — 必须加载悟空扩展，否则找不到插件
- `--proxy-server="direct://"` — 不走代理，直连
- 等8秒再连：`sleep 8 && nc -z 127.0.0.1 9222`

**常见错误：**
- ❌ 用默认Chrome profile → CDP启动失败
- ❌ 不加`--load-extension` → 找不到悟空插件
- ❌ 不加`--proxy-server=direct://` → 网页加载超时
- ❌ 用`open -a "Google Chrome"` → 参数不一定传递

### G-1 悟空插件登录 + 进入店铺

**前置条件：** Chrome已按G-0启动，CDP端口9222可用

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

# ⚠️ 如果插件显示"登录后使用"（自动修复，不需要人工登录）：
#   Goku插件从cookie读取"user-token"来认证
#   外卖通bi页面的localStorage有"sh-user-token"（JWT），但cookie里没有
#   解法：从localStorage复制到cookie，然后reload插件
for page in ctx.pages:
    if 'bi.shihengtech' in page.url:
        token = await page.evaluate('() => localStorage.getItem("sh-user-token")')
        if token:
            await ctx.add_cookies([
                {'name': 'user-token', 'value': token, 'domain': '.shihengtech.com', 'path': '/'},
                {'name': 'user-token', 'value': token, 'domain': 'bi-open.shihengtech.com', 'path': '/'},
            ])
            break
# 如果没有bi页面打开，先在ext上点"前往登录"打开它：
# ext_page = [p for p in ctx.pages if 'chrome-extension://' in p.url][0]
# await ext_page.locator('text=前往登录').click()
# await asyncio.sleep(5)  # 等bi页面加载
# 然后再执行上面的token复制流程

# 最后reload插件
for page in ctx.pages:
    if 'chrome-extension://' in page.url:
        await page.reload()
        await asyncio.sleep(5)
ext = await get_ext(ctx)  # 重新获取

# 3. 选品牌（用PA的subscriber_name搜索）
ok, status = await pick_brand(ext, "酸菜猪脚饭（鼓楼店）")

# 4. 获取店铺列表
stores = await get_stores(ext)
# stores = {"店名": [{"platform":"meituan","account":"mt312263uz","action":"一键登录"}, ...]}

# 5. 点击登录（参数是account值，不是品牌名！）
for name, accs in stores.items():
    for acc in accs:
        if acc["platform"] == "meituan":
            result = await click_store_platform(ext, acc["account"])  # 只传2个参数！
            # result: 'ok' / 'need_auth' / 'not_found'
            # 登录成功后等8秒让美团后台加载
```

### G-2 常见错误清单

- `click_store_platform(ext, brand, 'meituan')` ← **错！只有2个参数：ext和account**
- 忘记绕过代理 → CDP连接502 Bad Gateway
- 每次新Playwright连接前要 `pkill -f "playwright"`，否则端口冲突
- 采完数据要 `await close_store_pages(ctx)` 关闭后台页面
- **不要在Goku网页(bi.shihengtech.com)搜店铺** — 那是数据看板，门店选择器经常加载不出来。搜店铺一律用悟空插件(pick_brand)
- 插件显示"登录后使用" → 自动修复：从bi.shihengtech.com的localStorage取sh-user-token写入cookie（见G-1代码），不需要人工登录

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

**C-10** 美团后台评分/评价数据采集：
- 导航URL：`e.waimai.meituan.com/#https://waimaieapp.meituan.com/frontweb/ffw/userComment_gw`
- 页面结构：主frame→hashframe(Flutter canvas)→inner iframe(ScoreDetailPagePc)
- **评分明细**直接从inner iframe的innerText解析（非Flutter canvas部分）
- **评分API**（scores）：
  ```
  GET /gw/customer/comment/scores?ignoreSetRouterProxy=true&acctId={}&wmPoiId={}&token={}&appType=3
  ```
  返回：poiScore/foodScore/merchantScore(含各星级评价条数)/prisePercent(好评率)
- **评分详情API**（scores/detail）：
  ```
  GET /gw/customer/comment/scores/detail?acctId={}&wmPoiId={}&token={}&appType=3
  ```
- **tabs问题**：6个tab(综合评分明细/外卖评价列表/外卖评价统计/拦截与申诉/规则帮助/评价神器)是Flutter canvas渲染，Playwright点击/CDP PointerEvent/dispatchEvent均无法点击。需手动操作或找到评价列表的独立API
- **差评判断**：近30日1-2星评价数从scores API的merchantScore字段解析即可，无需进评价列表

**C-11** PA数据库评分历史+流量对比：
- 表：`takeaway_shop_ratings` — 每日评分(rating/taste_rating/packaging_rating/delivery_rating)
- 表：`daily_shop_operation_statuses` — 每日曝光/进店/订单/GMV/新老客拆分
- 查店：`SELECT id FROM takeaway_shops WHERE name LIKE '%店名%' AND platform='meituan'`
- 流程：①找评分变化节点 ②按节点分两期 ③排除节假日 ④算日均+转化率变化
- 注意：expose_uv有些天为0（数据缺失），只用expose_uv>0的天
- 前置：需VPN连通PA数据库（见reference_shiheng_database.md）

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

**E-3** 步骤2：诊断分析（运营诊断报告生成 Skill）

**诊断逻辑按BRAIN.md逻辑树执行，输出格式严格按以下模板。** 每次出诊断报告必须走这个skill，不能手写。

并行策略：多家店可用Agent工具并行分析，每家独立一个agent，给它完整的数据包+BRAIN.md+本skill模板。

### E-3-1 输入要求

每个品牌必须准备以下数据包（缺失项标注"数据缺失"）：
- crawl_results.json中对应品牌的美团后台数据（流量/营收/顾客/商品/活动）
- CRM中的合同信息（合同类型/运营/服务天数/月营收/利润）
- BRAIN.md全文

### E-3-2 输出模板（严格遵守，不能增减章节）

```markdown
# {品牌名}运营诊断

---

## 诊断元信息

| 项目 | 内容 |
|------|------|
| 品牌 | {品牌名} |
| 诊断时间 | {YYYY-MM-DD} |
| 数据周期 | 近30日（{起止日期}） |
| 认知版本 | brain-test（BRAIN.md {版本日期}） |
| 平台 | {美团/饿了么/双平台} |

---

## 一、这家店在卖什么？（产品端）

### 1.1 品类识别
- 品类定性+消费场景还原（P-1）
- TOP10产品角色表（产品/销量/单均价/标签/角色判断）
- 角色缺口诊断（引流/招牌/利润/加购各项是否充足）

### 1.2 价格结构分析
- 价格带分布表（区间/订单量/占比/评估）
- 核心问题标注

### 1.3 套餐设计
- 有无套餐、逻辑是否数据驱动
- 缺失项

### 1.4 菜单结构
- SKU数/分类合理性/长尾品/重复品

---

## 二、把东西卖对了吗？（运营端）

### 2.1 漏斗拆解
#### 综合数据
表格：指标/本店/商圈均值/差距

#### 新客链路（L-2）
表格：指标/本店/商圈均值/评估

#### 老客链路（L-2）
表格：指标/本店/商圈均值/评估

#### 关键信号
1次购买率/未收藏率等留存数据

### 2.2 活动与满减（D-9/D-12分析）
- 到手率表格
- 满减逐档分析（有数据时）
- 与D-12对照

### 2.3 评价管理
- 有数据时按类型分析；无数据时标注+间接信号

### 2.4 竞对分析
- 竞对流向数据（C-4）
- 竞争性质判断

### 2.5 利润判断
- 系统后净利估算

---

## 三、诊断输出

### 3.1 核心判断
一段话：最大的问题是什么，用数据说话

### 3.2 核心问题排序
P1-P5格式：
**P1（最严重）：{问题名}**
- 数据支撑
- 根因引用BRAIN节点
- 影响

### 3.3 做对了的
1-5条，每条有数据支撑

### 3.4 菜单重构方案（如有菜单问题）
- 角色重新标定表
- 新增套餐建议表
- 折扣/下架策略

### 3.5 TODO
每条格式：
**TODO-N：{标题}**
- 改什么：具体到SKU
- 解决漏斗哪个环节
- 原因逻辑（引用BRAIN节点）
- 预估影响

Tips单独列，标注不计入采纳率

### 3.6 还需确认
运营/老板需补充的信息

---

*诊断时间：{日期} | BRAIN版本：{版本} | 数据完整性：{说明}*
```

### E-3-3 执行规则

1. **每个判断必须有数据支撑** — 不能空说"偏低"，必须给数字和对比基准
2. **引用BRAIN节点** — 如"（D-12）""（P-17）""（L-3-1）"，让诊断可溯源
3. **到手率必算** — 到手率=营业收入/优惠前总额，低于50%必须P1标注
4. **漏斗必拆新老客** — 综合指标是假象（L-1），必须分别分析
5. **价格带必须从营收数据中提取** — 不能跳过
6. **TOP10必须标角色** — 每个品标引流/招牌/利润/加购
7. **竞对流向必看** — 顾客常买商家数据推导竞争关系（C-4）
8. **不了解的不下判断（J-1）** — 缺数据就标"需补充数据确认"
9. **文件命名** — `{品牌简称}_{分店}_{运营诊断}_{YYYYMMDD}.md`
10. **保存路径** — `~/Downloads/wisdom-brain/diagnosis-test/`
11. **更新CRM** — 写完报告后更新review_batches的diagnosis_report(文件路径)、diagnosis_summary、diagnosed_at

### E-3-4 Agent调用prompt模板

给Agent的prompt必须包含：
```
你是一个资深外卖运营诊断专家。请严格按照BRAIN.md诊断逻辑树+SKILL E-3-2输出模板，对以下店铺数据进行完整运营诊断。

[BRAIN.md全文]

[E-3-2输出模板]

[品牌数据包]

注意：
- 每个判断必须有具体数据支撑
- 评级用P1-P5排序（不用A/B/C/D）
- 引用BRAIN节点编号
- 缺数据的维度标注"数据缺失"而非跳过
```

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

**E-6** 参考范例（20260513标准）：
- `~/Downloads/wisdom-brain/diagnosis-test/燊味盐帮菜_武侯_运营诊断_20260512.md` — 最完整的标准参考
- `~/Downloads/wisdom-brain/diagnosis-test/食宜鲜炖_双店_河西店_运营诊断_20260513.md` — 养生品类参考

---

## 6. 模糊操作方式

**SF-1** 新客立减前端展示的具体条件
- 待确认：怎样设置才能让新客立减有标签展示？

**SF-2** 分时段定价的操作方法
- 待确认：美团/饿了么后台具体怎么设置分时段折扣？

---

## 7. TODO反馈格式规范

**F-1** CRM TODO反馈必须分三块：

```
**结论：{有效/无效/待讨论/待确认}**
{一句话结论} + {关键数据表格}

**原因：** {为什么有效/无效}

**后续TODO：** {有→写具体下一步 / 无→写"已闭环"}
```

- 数据对比必须用markdown表格，不要纯文本罗列
- 结论先行，数据支撑放后面
- 后续TODO要具体可执行（谁做什么，多久后看数据）

**SF-3** 满减后续档位设计
- 第一档已确认（实付x1.15/0.9，1.3倍校验）
- 待确认：第二档、第三档的递进逻辑

**SF-4** 推广数据完整采集的方法
- 待确认：完整采集推广数据的标准流程是什么？

**SF-5** 订单关联数据分析方法
- 操作：美团商家后台 → 订单管理 → 导出近7日订单明细 → 按订单ID分组 → 统计高频搭配TOP10
- 应用：套餐重设计、发现潜在组合需求

**SF-6** 前后对比数据分析规则
- **必须用相对数/单均**：绝对数会随订单量波动，不能直接对比。例：补贴¥9176→¥8820不能说"减少"，要算单均¥25.35→¥25.42才知道"持平"
- **常用标准化方式**：单均（÷订单数）、占比（÷总额）、转化率（÷曝光/进店）、日均（÷天数）
- **结论必须基于相对数**：不能用"营业收入持平"得出"没增长"，也不能用"ROI提升"得出"改动有效"——要看转化率（进店率/下单率）才能判断活动对增长的作用。效率提升≠增长
- **归因要排除混杂因素**：多个变量同时变化（满减+套餐+流量质量）时，用对照组（如饿了么）隔离变量。如果对照组没变→不是共同因素的锅；如果对照组也变了→是共同因素
- **对比时间段要等长**：8天比8天，不能8天比4天（除非用日均）
- **必须验证数据完整性**：PA数据可能有缺失天（字段=0），汇总前先看逐日，发现缺失要用有效天日均
- **多平台做对照组**：饿了么和美团同时改，如果一边变了另一边没变→不是改动的锅
- **PA数据不可靠时走后台**：PA订单表可能缺失整天数据，关键分析要到美团/饿了么商家后台拉

**SF-7** 满减效果分析方法
- **数据源**：美团商家后台 → 活动中心 → 我的活动 → 满减那行"详情" → "操作记录"tab 看历史修改
- **关键指标**（全部用相对数）：
  - 活动客单价（支付单均价）：门槛改高→客单价涨→说明凑单有效
  - 活动力度（%）：商家补贴占GMV比例，越低越好
  - ROI（投入产出比）：越高越好
  - 单均满减成本（满减活动成本÷订单数）：触发力度
  - 新客/老客占比：不看绝对数看占比变化
- **成本分布**：营销tab → 活动成本分布，拆出满减活动、天天神券、折扣商品等各项占比
- **对比方法**：自定义日期拉改前/改后同等天数，不看绝对值看单均和占比

**SF-8** 美团后台数据采集路径汇总
- **商品销量**：经营分析 → 经营数据 → 商品tab → 自定义日期 → 逐页提取（每页20条）
- **营收概览**：经营分析 → 经营数据 → 营收tab → 自定义日期 → 营业收入/优惠前总额/补贴支出/订单量/支付单均价
- **活动/营销**：经营分析 → 经营数据 → 营销tab → 自定义日期 → 活动订单/成本/力度/ROI/客单价/新老客
- **活动成本分布**：营销tab下滚 → 各类型活动商家成本（天天神券/满减/折扣商品等）
- **满减历史**：活动中心 → 我的活动 → 满减活动"详情" → 操作记录tab
- **iframe注意**：美团后台内容在waimaieapp.meituan.com的iframe里，需要找到正确的frame操作

---

## 8. TODO效果验证框架

> 本质是A/B test逻辑：每个改动影响的是谁、在哪个动作上、怎么看数据、数据够不够。

### V-1 核心思考链（每个TODO必须走一遍）

改动前问自己：

```
1. 这个改动出现在谁面前？
   → 新客？老客？所有人？

2. 出现在用户旅程的哪个瞬间？
   → 列表页扫一眼？菜单页选品？下单结算？收餐体验？

3. 影响的是哪个动作？
   → 点不点进去（进店）？买不买（下单）？买多少（客单）？下次来不来（复购）？

4. 预期是什么？
   → 明确写出：预期哪个指标往哪个方向变

5. 怎么看数据验证？
   → 看哪个人群的哪个指标，是否需要按流量来源拆开
```

### V-2 新客 vs 老客的旅程差异

**新客旅程**：
```
列表页（店名/logo/评分/价格标签/月售）→ 进店决策
菜单页（首屏品/图片/价格/满减提示）→ 下单决策
收餐体验 → 第一印象（决定有没有下次）
```

**老客旅程**：
```
搜索/收藏/推送 → 想起这家店 → 进店（路径不同于新客）
找常点品 → 快速下单（决策路径短）
常点品变了/价格变了/下架了 → 困惑 → 可能流失
```

**关键区别**：同一个改动对新客和老客的影响机制不同。
- 改店名：新客在列表页看店名决定进不进，老客认logo和位置，店名对他们几乎无感
- 退折扣：新客看到的是"这家贵不贵"，老客看到的是"我常点的涨价了"
- 加套餐：新客看到的是"有个简单选择降低决策门槛"，老客看到的是"可以试试新组合"

### V-3 常见改动的验证方式

| 改动 | 影响谁 | 影响哪个动作 | 看什么 | 怎么拆 |
|------|--------|------------|--------|--------|
| 改店名/品类名 | 主要新客 | 列表页→进店 | 新客进店率 | — |
| 改头图/主图 | 主要新客 | 列表页→进店 | 新客进店率 | — |
| 改菜单首屏排序 | 新客为主 | 进店→下单 | 新客下单率 | — |
| 加套餐 | 所有人 | 下单+客单 | 下单率、客单价、件均 | 新客/老客分别看 |
| 退折扣/调价 | 所有人 | 下单+利润 | 下单率、到手率 | 免费流量/付费流量分开看 |
| 调满减档位 | 所有人 | 客单+利润 | 客单价、满减触发率、到手率 | 各档触发订单占比 |
| 下架长尾品 | 老客为主 | 下单（风险） | 老客下单率、老客复购率 | 看是否有老客常点品被误删 |
| 招牌品包装 | 所有人 | 进店+复购 | 该品销量占比、复购率 | 新客/老客分别看 |
| 加购区设计 | 所有人 | 客单 | 件均、加购品销量 | — |
| 收藏/留存机制 | 新转老 | 复购 | 收藏率、首单→二单转化率 | — |
| 加付费投放 | 新客为主 | 曝光→进店 | 进店率（会降）、下单率（会降） | 必须拆免费/付费流量分别看 |

### V-4 验证规则

**预期先行**：每个TODO执行前写明预期（"预期新客下单率+2pp"），review时对照预期判断。

**拆解排除干扰**：数据不符合预期时，不是直接说"没效果"，而是拆开看有没有干扰因素。
- 典型场景：改了价格同时加了付费投放 → 整体下单率降了 → 拆开看：免费流量下单率其实升了，是付费流量质量差拉低了整体 → 结论：价格改动达到预期，整体降是付费流量的问题
- 另一种：改了满减同时改了菜单 → 客单升了但不知道归谁 → 用饿了么做对照组（只改了满减没改菜单），隔离变量

**数据稳定性判断**：
- 一般3天数据够看
- 日均单量小的店（<20单）看7天
- 判断标准不是样本量，是数据稳不稳——连续几天在一个水平不大幅波动，就够下结论
- 如果3天数据还在上下跳，再等几天直到稳定

**必须用相对数**（SF-6重申）：看单均、占比、转化率，不看绝对数。绝对数随订单量波动，不能直接对比。

**老客敏感度看数据不猜**：不预设"老客会怎样"，改了之后直接看老客进店率/下单率/复购率的实际变化。

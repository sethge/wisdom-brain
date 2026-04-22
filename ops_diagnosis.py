"""
运营诊断 skill — 标准化数据采集 + brain-test诊断框架

用法:
    /opt/homebrew/bin/python3 ops_diagnosis.py "店铺名1" "店铺名2" ...
    /opt/homebrew/bin/python3 ops_diagnosis.py --all  # 跑预设列表

依赖:
    - store-monitor/browser.py (CDP连接)
    - store-monitor/plugin_helper.py (悟空插件操作)
    - playwright

数据采集清单（每家店固定）:
    1. 经营总览 (总览tab)
    2. 流量漏斗 (全部顾客/新客/老客 × 近30日)
    3. 推广数据
    4. 顾客数据 (复购/频次/画像/竞对流向)
    5. 商品销量 TOP20
    6. 活动详情 (满减/折扣/配送费)
    7. 菜单结构 (分组+SKU)

输出:
    ~/Downloads/wisdom-brain/diagnosis-test/{店名}_原始数据_{日期}.md
"""

import asyncio
import sys
import os
import time

# 加入store-monitor路径
sys.path.insert(0, os.path.expanduser("~/Downloads/store-monitor"))
from browser import launch as launch_browser
from plugin_helper import get_ext, pick_brand, get_stores, click_store_platform, check_verification, close_store_pages

OUTDIR = os.path.expanduser("~/Downloads/wisdom-brain/diagnosis-test")
DATE = time.strftime("%Y%m%d")

# 预设店铺列表
DEFAULT_STORES = [
    "峨眉郑记豆腐脑（宽窄店）",
    "冰拾叁（北城天街店）",
    "重庆碗杂面（益州大道南段店）",
    "川香风味（玉溪店）",
    "冰拾叁（三河店）",
    "擀面皮肉夹馍（丽泽店）",
    "煎豆师咖啡（东园文化创意广场店）",
    "西北羊肉馆（虹井路店）",
    "都市潮粉梦（广州店）",
    "牛牛卷凉皮.米线（雨山路）",
    "千羽鹤（崇文门店）",
    "优米师傅（锦江店）",
    "饱鲜新疆炒米粉（青羊店）",
    "干饭人干拌冒菜（郭店店）",
    "饺子鲜（双菱路店）",
    "华兴煎蛋面（致民路店）",
    "原始鲜屿（西直门店）",
]


def js_click(text):
    """生成点击指定文字元素的JS"""
    return f"""() => {{
        const all = document.querySelectorAll('*');
        for (const el of all) {{
            if (el.childNodes.length <= 2 && el.textContent.trim() === '{text}' && el.offsetParent) {{
                el.click();
                return true;
            }}
        }}
        return false;
    }}"""


async def wait_mt_page(ctx, timeout=15):
    """等待美团后台页面出现并加载"""
    for _ in range(timeout):
        for p in ctx.pages:
            if 'e.waimai.meituan.com' in p.url and 'chrome-extension' not in p.url:
                try:
                    await p.wait_for_load_state("domcontentloaded", timeout=3000)
                except:
                    pass
                return p
        await asyncio.sleep(1)
    return None


async def get_biz_frame(mt_page):
    """找经营分析frame"""
    for f in mt_page.frames:
        if 'bizdata' in f.url or 'waimaieapp' in f.url:
            try:
                t = await f.evaluate("() => document.body ? document.body.innerText.length : 0")
                if t > 100:
                    return f
            except:
                pass
    return None


async def read_frame_content(mt_page, max_len=5000):
    """读取最大内容frame的文本"""
    best, best_len = None, 0
    for f in mt_page.frames:
        if f.url == mt_page.url:
            continue
        try:
            t = await f.evaluate("() => document.body ? document.body.innerText.length : 0")
            if t > best_len:
                best_len = t
                best = f
        except:
            pass
    if best and best_len > 50:
        return (await best.evaluate("() => document.body.innerText"))[:max_len]
    return ""


async def crawl_one_store(ctx, ext, brand_name):
    """采集一家店的全部美团数据，返回 (data_dict, status)"""
    data = {"store_name": brand_name, "crawl_time": time.strftime("%Y-%m-%d %H:%M")}

    # === 1. 悟空切换品牌 ===
    ok, status = await pick_brand(ext, brand_name)
    if not ok:
        return data, f"品牌切换失败: {status}"

    if "未授权" in status:
        return data, "未授权"

    # === 2. 获取店铺列表，找美团账号 ===
    stores = await get_stores(ext)
    mt_account = None
    for store_key, accounts in stores.items():
        for acct in accounts:
            if acct['platform'] == 'meituan' and acct['action'] == '一键登录':
                mt_account = acct['account']
                break
        if mt_account:
            break

    if not mt_account:
        # 检查是否需要授权
        for store_key, accounts in stores.items():
            for acct in accounts:
                if acct['platform'] == 'meituan' and acct['action'] == '立刻授权':
                    return data, "美团需要授权"
        return data, "无美团账号"

    data["mt_account"] = mt_account

    # === 3. 关闭旧页面 + 一键登录 ===
    await close_store_pages(ctx)
    result = await click_store_platform(ext, mt_account)
    if result != 'ok':
        return data, f"登录失败: {result}"

    await asyncio.sleep(5)

    # === 4. 等美团页面 ===
    mt_page = await wait_mt_page(ctx)
    if not mt_page:
        return data, "美团页面未打开"

    # 验证检测
    blocked, reason = await check_verification(mt_page)
    if blocked:
        return data, f"验证拦截: {reason}"

    # 确认已登录
    await mt_page.goto("https://e.waimai.meituan.com/", wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    homepage = await mt_page.evaluate("() => document.body.innerText.substring(0, 500)")
    if "商家首页" not in homepage:
        return data, "未成功登录"

    mt_store_name = homepage.split("\n")[0].strip()
    data["mt_store_name"] = mt_store_name
    data["homepage"] = homepage

    # === 5. 经营分析 ===
    await mt_page.evaluate(js_click('经营分析'))
    await asyncio.sleep(2)
    try:
        await mt_page.evaluate(js_click('经营数据'))
    except:
        pass
    await asyncio.sleep(5)

    biz = await get_biz_frame(mt_page)
    if biz:
        # 总览tab
        data["overview"] = (await biz.evaluate("() => document.body.innerText"))[:5000]

        # 流量tab
        await biz.evaluate(js_click('流量'))
        await asyncio.sleep(3)
        await biz.evaluate(js_click('近30日'))
        await asyncio.sleep(3)
        data["flow_all"] = (await biz.evaluate("() => document.body.innerText"))[:3000]

        await biz.evaluate(js_click('新客'))
        await asyncio.sleep(3)
        data["flow_new"] = (await biz.evaluate("() => document.body.innerText"))[:3000]

        await biz.evaluate(js_click('老客'))
        await asyncio.sleep(3)
        data["flow_old"] = (await biz.evaluate("() => document.body.innerText"))[:3000]

        # 推广tab
        await biz.evaluate(js_click('推广'))
        await asyncio.sleep(3)
        data["promo"] = (await biz.evaluate("() => document.body.innerText"))[:3000]

        # 顾客tab
        await biz.evaluate(js_click('顾客'))
        await asyncio.sleep(3)
        await biz.evaluate(js_click('近30日'))
        await asyncio.sleep(2)
        data["customer"] = (await biz.evaluate("() => document.body.innerText"))[:5000]

        # 商品tab
        await biz.evaluate(js_click('商品'))
        await asyncio.sleep(3)
        await biz.evaluate(js_click('近30日'))
        await asyncio.sleep(2)
        data["products"] = (await biz.evaluate("() => document.body.innerText"))[:5000]
    else:
        data["error_biz"] = "经营分析frame未找到"

    # === 6. 活动中心 ===
    await mt_page.goto("https://e.waimai.meituan.com/", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(3)
    await mt_page.evaluate(js_click('活动中心'))
    await asyncio.sleep(2)
    await mt_page.evaluate(js_click('我的活动'))
    await asyncio.sleep(5)
    act_text = await read_frame_content(mt_page, 3000)
    if act_text:
        data["activities"] = act_text

    # === 7. 商品管理 ===
    await mt_page.goto("https://e.waimai.meituan.com/", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(3)
    await mt_page.evaluate(js_click('商品管理'))
    await asyncio.sleep(2)
    await mt_page.evaluate(js_click('商品列表'))
    await asyncio.sleep(5)
    menu_text = await read_frame_content(mt_page, 5000)
    if menu_text:
        data["menu"] = menu_text

    # === 8. 关闭页面 ===
    await close_store_pages(ctx)

    return data, "ok"


def save_raw_data(brand_name, data):
    """保存原始数据为标准md"""
    safe = brand_name.replace("（", "_").replace("）", "").replace("·", "_").replace(".", "_").replace(" ", "")
    path = os.path.join(OUTDIR, f"{safe}_原始数据_{DATE}.md")

    section_names = {
        'homepage': '首页概况',
        'overview': '经营总览',
        'flow_all': '流量-全部顾客(近30日)',
        'flow_new': '流量-新客(近30日)',
        'flow_old': '流量-老客(近30日)',
        'promo': '推广数据',
        'customer': '顾客数据(近30日)',
        'products': '商品销量(近30日)',
        'activities': '活动详情',
        'menu': '菜单结构',
    }

    with open(path, "w") as f:
        f.write(f"# {brand_name} 原始数据\n\n")
        f.write(f"> 采集时间: {data.get('crawl_time', '')}\n")
        f.write(f"> 美团店名: {data.get('mt_store_name', '')}\n")
        f.write(f"> 美团账号: {data.get('mt_account', '')}\n\n---\n\n")

        for key, name in section_names.items():
            if key in data and data[key]:
                f.write(f"## {name}\n\n```\n{data[key]}\n```\n\n")

        if 'error_biz' in data:
            f.write(f"## 采集异常\n\n{data['error_biz']}\n")

    return path


async def main():
    from playwright.async_api import async_playwright

    # 解析参数
    args = sys.argv[1:]
    if not args or args[0] == '--all':
        stores = DEFAULT_STORES
    else:
        stores = args

    print(f"运营诊断采集: {len(stores)}家店")
    print("=" * 60)

    # 连接浏览器
    pw = await async_playwright().start()
    browser, ctx = await launch_browser(pw)
    ext = await get_ext(ctx)
    print("悟空插件已连接")

    results = {}

    for i, store in enumerate(stores):
        print(f"\n[{i+1}/{len(stores)}] {store}")
        print("-" * 40)

        try:
            data, status = await crawl_one_store(ctx, ext, store)
        except Exception as e:
            status = f"异常: {str(e)[:100]}"
            data = {"store_name": store, "error": status}

        if status == "ok":
            path = save_raw_data(store, data)
            print(f"  ✅ 保存: {os.path.basename(path)}")
            results[store] = "ok"
        else:
            print(f"  ❌ {status}")
            results[store] = status

    # 汇总
    print(f"\n{'=' * 60}")
    print("采集结果:")
    ok_count = sum(1 for v in results.values() if v == "ok")
    print(f"成功 {ok_count}/{len(stores)}")
    for store, status in results.items():
        icon = "✅" if status == "ok" else "❌"
        print(f"  {icon} {store}: {status}")

    await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())

"""通用店铺数据采集脚本 — 悟空插件登录 + 美团后台全量采集"""
import asyncio
import json
import subprocess
import sys
import os

sys.path.insert(0, os.path.expanduser("~/Downloads/store-monitor"))
from plugin_helper import get_ext, pick_brand, get_stores, click_store_platform, close_store_pages, check_verification

PORT = 9222

async def cdp_ws():
    r = subprocess.run(["curl", "--noproxy", "localhost", "-s", f"http://localhost:{PORT}/json/version"],
                       capture_output=True, text=True, timeout=3)
    return json.loads(r.stdout).get("webSocketDebuggerUrl")


async def wait_mt_ready(browser, timeout=30):
    """等美团后台加载完成，返回(page, frame)"""
    for _ in range(timeout):
        for c in browser.contexts:
            for p in c.pages:
                if 'chrome-extension' in p.url:
                    continue
                if 'e.waimai.meituan.com' in p.url or 'waimaieapp.meituan.com' in p.url:
                    # 检查验证拦截
                    blocked, desc = await check_verification(p)
                    if blocked:
                        print(f"⚠️ 被拦截: {desc}")
                        return None, None
                    # 找内容frame（两种URL模式）
                    for f in p.frames:
                        u = f.url
                        if ('waimaieapp.meituan.com' in u or 'new_fe/business_gw' in u) and f != p.main_frame:
                            try:
                                text = await f.evaluate("() => document.body.innerText.substring(0, 200)")
                                if len(text) > 30:
                                    return p, f
                            except:
                                pass
                    # fallback: 主页面本身有内容
                    try:
                        text = await p.evaluate("() => document.body.innerText.substring(0, 200)")
                        if len(text) > 50 and ('商家首页' in text or '经营分析' in text):
                            return p, None
                    except:
                        pass
        await asyncio.sleep(1)
    return None, None


async def nav_to_section(page, section_name):
    """点侧边栏导航到指定区域"""
    await page.evaluate(f"""() => {{
        const els = document.querySelectorAll('*');
        for (const el of els) {{
            if (el.textContent.trim() === '{section_name}' && el.children.length <= 2 && el.offsetParent) {{
                el.click(); return true;
            }}
        }}
        return false;
    }}""")
    await asyncio.sleep(3)


async def get_content_frame(page, min_len=50):
    """获取当前内容frame"""
    for f in page.frames:
        u = f.url
        if ('waimaieapp.meituan.com' in u or 'new_fe/' in u) and f != page.main_frame:
            try:
                text = await f.evaluate("() => document.body.innerText")
                if len(text.strip()) > min_len:
                    return f
            except:
                pass
    return None


async def click_tab_in_frame(frame, tab_name):
    """在frame内点击tab"""
    await frame.evaluate(f"""() => {{
        const els = document.querySelectorAll('*');
        for (const el of els) {{
            const t = el.textContent.trim();
            if (t === '{tab_name}' && el.children.length <= 1 && el.offsetParent) {{
                el.click(); return true;
            }}
        }}
        return false;
    }}""")
    await asyncio.sleep(2)


async def read_frame_text(frame):
    """读取frame全文"""
    try:
        return await frame.evaluate("() => document.body.innerText")
    except:
        return ""


async def crawl_overview(page, frame):
    """采集经营分析-总览"""
    print("📊 采集总览...")
    # 点经营分析
    await nav_to_section(page, "经营分析")
    await asyncio.sleep(2)
    # 再点经营数据
    await nav_to_section(page, "经营数据")
    await asyncio.sleep(3)

    frame = await get_content_frame(page)
    if not frame:
        print("  ❌ 找不到经营分析frame")
        return "", frame

    # 切近30日
    try:
        await frame.locator("text=近30日").first.click(timeout=5000)
        await asyncio.sleep(2)
    except:
        print("  ⚠️ 切近30日失败")

    text = await read_frame_text(frame)
    print(f"  ✅ 总览 {len(text)} chars")
    return text, frame


async def crawl_flow_funnel(page, frame):
    """采集流量漏斗（全部/新客/老客 × 均值/前10%）"""
    print("📊 采集流量漏斗...")

    # 点流量tab
    await click_tab_in_frame(frame, "流量")
    await asyncio.sleep(3)

    # 重新获取frame（tab切换后可能变）
    frame = await get_content_frame(page)
    if not frame:
        print("  ❌ 找不到流量frame")
        return {}

    results = {}
    for tab_name in ["全部顾客", "新客", "老客"]:
        try:
            await frame.locator(f"text={tab_name}").first.click(timeout=3000)
            await asyncio.sleep(2)
        except:
            print(f"  ⚠️ 切{tab_name}失败")
            continue

        text = await read_frame_text(frame)
        results[f"{tab_name}_均值"] = text

        # 尝试切前10%
        try:
            dropdown = frame.locator(".roo-input-group.has-icon").nth(1)
            await dropdown.click(timeout=3000)
            await asyncio.sleep(0.5)
            opt = frame.locator(".roo-popup .roo-dropdown-item, .roo-popup li, .roo-popup div").filter(has_text="前10%")
            await opt.first.click(timeout=3000)
            await asyncio.sleep(2)
            text10 = await read_frame_text(frame)
            results[f"{tab_name}_前10%"] = text10
            print(f"  ✅ {tab_name} 均值+前10%")

            # 切回均值
            dropdown = frame.locator(".roo-input-group.has-icon").nth(1)
            await dropdown.click(timeout=3000)
            await asyncio.sleep(0.5)
            opt2 = frame.locator(".roo-popup .roo-dropdown-item, .roo-popup li, .roo-popup div").filter(has_text="商圈同行均值")
            await opt2.first.click(timeout=3000)
            await asyncio.sleep(1)
        except:
            print(f"  ⚠️ {tab_name} 前10%切换失败")

    return results


async def crawl_customer(page, frame):
    """采集顾客数据"""
    print("📊 采集顾客数据...")
    await click_tab_in_frame(frame, "顾客")
    await asyncio.sleep(3)
    frame = await get_content_frame(page)
    if not frame:
        return ""
    text = await read_frame_text(frame)
    print(f"  ✅ 顾客 {len(text)} chars")
    return text


async def crawl_product(page, frame):
    """采集商品数据"""
    print("📊 采集商品数据...")
    await click_tab_in_frame(frame, "商品")
    await asyncio.sleep(3)
    frame = await get_content_frame(page)
    if not frame:
        return ""
    text = await read_frame_text(frame)
    print(f"  ✅ 商品 {len(text)} chars")
    return text


async def crawl_promotion(page, frame):
    """采集推广数据"""
    print("📊 采集推广数据...")
    await click_tab_in_frame(frame, "推广")
    await asyncio.sleep(3)
    frame = await get_content_frame(page)
    if not frame:
        return ""
    text = await read_frame_text(frame)
    print(f"  ✅ 推广 {len(text)} chars")
    return text


async def crawl_marketing(page, frame):
    """采集营销数据"""
    print("📊 采集营销数据...")
    await click_tab_in_frame(frame, "营销")
    await asyncio.sleep(3)
    frame = await get_content_frame(page)
    if not frame:
        return ""
    text = await read_frame_text(frame)
    print(f"  ✅ 营销 {len(text)} chars")
    return text


async def crawl_service(page, frame):
    """采集服务数据"""
    print("📊 采集服务数据...")
    await click_tab_in_frame(frame, "服务")
    await asyncio.sleep(3)
    frame = await get_content_frame(page)
    if not frame:
        return ""
    text = await read_frame_text(frame)
    print(f"  ✅ 服务 {len(text)} chars")
    return text


async def crawl_activities(page):
    """采集活动中心数据"""
    print("📊 采集活动中心...")
    await nav_to_section(page, "活动中心")
    await asyncio.sleep(4)

    frame = await get_content_frame(page)
    if not frame:
        # fallback: 直接读page
        text = await page.evaluate("() => document.body.innerText")
    else:
        text = await read_frame_text(frame)

    print(f"  ✅ 活动中心 {len(text)} chars")
    return text


async def crawl_reviews(page):
    """采集评价数据"""
    print("📊 采集评价数据...")
    await nav_to_section(page, "顾客管理")
    await asyncio.sleep(2)
    await nav_to_section(page, "顾客评价")
    await asyncio.sleep(4)

    frame = await get_content_frame(page)
    if not frame:
        text = await page.evaluate("() => document.body.innerText")
    else:
        text = await read_frame_text(frame)

    print(f"  ✅ 评价 {len(text)} chars")
    return text


async def crawl_flow_source(page, frame):
    """采集流量来源"""
    print("📊 采集流量来源...")
    # 应该已经在流量tab了
    text = await read_frame_text(frame)
    # 找流量来源部分
    lines = text.split('\n')
    source_lines = []
    capture = False
    for l in lines:
        if '流量来源' in l or '曝光渠道' in l:
            capture = True
        if capture:
            source_lines.append(l)
        if capture and len(source_lines) > 20:
            break
    return '\n'.join(source_lines)


async def main():
    if len(sys.argv) < 2:
        print("用法: python3 crawl_store.py '品牌名（店铺名）'")
        print("例如: python3 crawl_store.py '峨眉郑记豆腐脑（宽窄店）'")
        sys.exit(1)

    store_name = sys.argv[1]
    # 从品牌名提取搜索关键词
    brand_kw = store_name.split("（")[0] if "（" in store_name else store_name

    print(f"🏪 开始采集: {store_name}")
    print(f"   搜索关键词: {brand_kw}")

    ws = await cdp_ws()

    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0]

        # 1. 先关闭已有的美团页面
        await close_store_pages(ctx)
        await asyncio.sleep(1)

        # 2. 找到悟空插件
        print("🔌 连接悟空插件...")
        ext = await get_ext(ctx)

        # 3. 搜索品牌并选择
        print(f"🔍 搜索品牌: {brand_kw}...")
        ok, status = await pick_brand(ext, store_name)
        if not ok:
            print(f"❌ 品牌搜索失败: {status}")
            return
        print(f"  品牌状态: {status}")

        # 4. 获取店铺列表
        stores = await get_stores(ext)
        print(f"  找到 {len(stores)} 个店铺")
        for name, accts in stores.items():
            for a in accts:
                print(f"    {name}: {a['platform']} - {a['account']} [{a['action']}]")

        # 5. 找到美团账号并登录
        mt_account = None
        for name, accts in stores.items():
            for a in accts:
                if a['platform'] == 'meituan' and a['action'] == '一键登录':
                    mt_account = a['account']
                    break
            if mt_account:
                break

        if not mt_account:
            print("❌ 没找到可登录的美团账号")
            # 列出所有账号信息
            for name, accts in stores.items():
                for a in accts:
                    print(f"  {a['platform']} {a['account']} {a['action']}")
            return

        print(f"🔑 登录美团: {mt_account}")
        r = await click_store_platform(ext, mt_account)
        if r != 'ok':
            print(f"❌ 登录失败: {r}")
            return

        # 6. 等美团后台加载
        print("⏳ 等待美团后台加载...")
        page, frame = await wait_mt_ready(browser, timeout=30)
        if not page:
            print("❌ 美团后台加载超时或被拦截")
            return
        print("✅ 美团后台已加载")

        # 7. 采集所有数据
        all_data = {"store": store_name, "account": mt_account}

        # 总览
        overview_text, frame = await crawl_overview(page, frame)
        all_data["overview"] = overview_text

        # 流量漏斗
        funnel_data = await crawl_flow_funnel(page, frame)
        all_data["funnel"] = funnel_data

        # 刷新frame引用
        frame = await get_content_frame(page)

        # 顾客
        customer_text = await crawl_customer(page, frame)
        all_data["customer"] = customer_text

        # 商品
        product_text = await crawl_product(page, frame)
        all_data["product"] = product_text

        # 推广
        promo_text = await crawl_promotion(page, frame)
        all_data["promotion"] = promo_text

        # 营销
        marketing_text = await crawl_marketing(page, frame)
        all_data["marketing"] = marketing_text

        # 服务
        service_text = await crawl_service(page, frame)
        all_data["service"] = service_text

        # 活动中心
        activity_text = await crawl_activities(page)
        all_data["activities"] = activity_text

        # 评价
        review_text = await crawl_reviews(page)
        all_data["reviews"] = review_text

        # 8. 保存原始数据
        safe_name = store_name.replace("（", "_").replace("）", "").replace(" ", "")
        out_path = os.path.expanduser(f"~/Downloads/wisdom-brain/diagnosis-test/crawl_raw_{safe_name}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 原始数据已保存: {out_path}")

        # 9. 关闭美团页面
        await close_store_pages(ctx)
        print("🔒 已关闭美团页面")

        # 10. 输出关键信息摘要
        print(f"\n{'='*60}")
        print(f"采集完成: {store_name}")
        print(f"{'='*60}")
        print(f"总览: {len(overview_text)} chars")
        print(f"漏斗: {len(funnel_data)} tabs")
        print(f"顾客: {len(customer_text)} chars")
        print(f"商品: {len(product_text)} chars")
        print(f"推广: {len(promo_text)} chars")
        print(f"营销: {len(marketing_text)} chars")
        print(f"服务: {len(service_text)} chars")
        print(f"活动: {len(activity_text)} chars")
        print(f"评价: {len(review_text)} chars")


asyncio.run(main())

"""批量店铺数据采集 — 悟空登录 + 美团后台全量采集"""
import asyncio
import json
import subprocess
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.expanduser("~/Downloads/store-monitor"))
from plugin_helper import get_ext, pick_brand, get_stores, click_store_platform, close_store_pages, check_verification
from playwright.async_api import async_playwright

PORT = 9222
OUT_DIR = os.path.expanduser("~/Downloads/wisdom-brain/diagnosis-test")
TODAY = datetime.now().strftime("%Y%m%d")


async def cdp_ws():
    r = subprocess.run(["curl", "--noproxy", "localhost", "-s", f"http://localhost:{PORT}/json/version"],
                       capture_output=True, text=True, timeout=3)
    return json.loads(r.stdout).get("webSocketDebuggerUrl")


async def find_best_frame(page, exclude_main=True, min_len=50):
    """扫描所有frame，返回内容最长的那个frame的文本"""
    best = ""
    for f in page.frames:
        if exclude_main and f == page.main_frame:
            continue
        try:
            t = await f.evaluate("() => document.body.innerText")
            if len(t) > len(best):
                best = t
        except:
            pass
    return best


async def get_bizdata_frame(page):
    """找到经营数据的主frame"""
    for f in page.frames:
        if f == page.main_frame:
            continue
        if 'waimaieapp.meituan.com' in f.url and 'bizdata' in f.url:
            return f
    return None


async def click_tab_by_index(frame, idx):
    """用navtabs class按序号点击tab"""
    await frame.evaluate(f"""() => {{
        const items = document.querySelectorAll('.navtabs-wrapper__item');
        if (items[{idx}]) items[{idx}].click();
    }}""")
    await asyncio.sleep(4)


async def switch_30d(frame):
    """切近30日"""
    try:
        await frame.evaluate("""() => {
            const all = document.querySelectorAll('*');
            for (const el of all) {
                if (el.textContent.trim() === '近30日' && el.offsetParent && el.children.length <= 1
                    && el.getBoundingClientRect().y < 200) {
                    el.click(); return true;
                }
            }
            return false;
        }""")
        await asyncio.sleep(3)
    except:
        pass


async def crawl_store_data(page):
    """在已登录的美团后台采集全量数据，返回dict"""
    all_data = {}

    # 1. 导航到经营数据（先展开经营分析菜单）
    try:
        await page.locator('text=经营分析').first.click(timeout=5000)
        await asyncio.sleep(2)
    except:
        pass
    try:
        await page.locator('text=经营数据').first.click(timeout=8000)
    except:
        # fallback: JS点击
        await page.evaluate("""() => {
            const els = document.querySelectorAll('*');
            for (const el of els) {
                if (el.textContent.trim() === '经营数据' && el.offsetParent && el.children.length <= 2) {
                    el.click(); return;
                }
            }
        }""")
    await asyncio.sleep(5)

    df = await get_bizdata_frame(page)
    if not df:
        print("  ❌ 找不到经营数据frame")
        return all_data

    # 2. 获取tab列表
    tabs = await df.evaluate("""() => {
        const items = document.querySelectorAll('.navtabs-wrapper__item');
        return Array.from(items).map((el, i) => ({idx: i, text: el.textContent.trim()}));
    }""")
    print(f"  tabs: {[t['text'] for t in tabs]}")

    # 3. 采集每个tab
    # tab map: {name: idx}
    tab_map = {t['text']: t['idx'] for t in tabs}

    for name, idx in tab_map.items():
        print(f"  📊 [{idx}] {name}...", end=" ", flush=True)
        await click_tab_by_index(df, idx)

        # 行业/服务等tab加载较慢，多等一会
        if name in ('行业', '服务'):
            await asyncio.sleep(3)

        # 切近30日（在任何可用frame里尝试）
        # 先在df里试
        await switch_30d(df)
        # 也在新frame里试
        for f in page.frames:
            if f == page.main_frame or f == df:
                continue
            try:
                await switch_30d(f)
            except:
                pass

        # 读内容：扫描所有frame取最长
        text = await find_best_frame(page, exclude_main=True, min_len=30)

        # 如果内容太短（可能只拿到导航栏），再等一轮重试
        if len(text) < 80:
            await asyncio.sleep(5)
            text2 = await find_best_frame(page, exclude_main=True, min_len=30)
            if len(text2) > len(text):
                text = text2

        all_data[name] = text
        print(f"{len(text)} chars")

        # 流量tab: 切新客/老客
        if name == '流量':
            for sub in ["全部顾客", "新客", "老客"]:
                try:
                    await df.locator(f"text={sub}").first.click(timeout=3000)
                    await asyncio.sleep(2)
                    t = await find_best_frame(page)
                    all_data[f"流量_{sub}"] = t
                    print(f"    {sub}: {len(t)} chars")

                    # 前10%
                    try:
                        dropdown = df.locator(".roo-input-group.has-icon").nth(1)
                        await dropdown.click(timeout=2000)
                        await asyncio.sleep(0.5)
                        opt = df.locator("text=前10%均值")
                        if await opt.count() > 0:
                            await opt.first.click(timeout=2000)
                            await asyncio.sleep(2)
                            t10 = await find_best_frame(page)
                            all_data[f"流量_{sub}_前10%"] = t10
                            print(f"    {sub}_前10%: {len(t10)} chars")
                            dropdown = df.locator(".roo-input-group.has-icon").nth(1)
                            await dropdown.click(timeout=2000)
                            await asyncio.sleep(0.5)
                            await df.locator("text=商圈同行均值").first.click(timeout=2000)
                            await asyncio.sleep(1)
                    except:
                        pass
                except:
                    print(f"    {sub} 失败")

    # 4. 活动中心
    print("  📊 活动中心...", end=" ", flush=True)
    try:
        await page.locator('text=活动中心').first.click(timeout=5000)
        await asyncio.sleep(2)
        await page.locator('text=我的活动').first.click(timeout=5000)
        await asyncio.sleep(4)
        act = await find_best_frame(page)
        all_data["活动中心"] = act
        print(f"{len(act)} chars")
    except:
        print("失败")

    # 5. 顾客评价
    print("  📊 顾客评价...", end=" ", flush=True)
    try:
        await page.locator('text=顾客管理').first.click(timeout=5000)
        await asyncio.sleep(2)
        await page.locator('text=顾客评价').first.click(timeout=5000)
        await asyncio.sleep(4)
        rev = await find_best_frame(page)
        all_data["评价"] = rev
        print(f"{len(rev)} chars")
    except:
        print("失败")

    return all_data


async def login_store(ctx, ext, store_name):
    """用悟空插件登录指定店铺的美团账号，返回成功/失败"""
    # 关闭已有美团页面
    await close_store_pages(ctx)
    await asyncio.sleep(1)

    # 搜索品牌
    ok, status = await pick_brand(ext, store_name)
    if not ok:
        print(f"  ❌ 品牌搜索失败: {status}")
        return False

    # 获取店铺列表
    stores = await get_stores(ext)

    # 找美团账号
    mt_account = None
    for name, accts in stores.items():
        for a in accts:
            if a['platform'] == 'meituan' and a['action'] == '一键登录':
                mt_account = a['account']
                break
        if mt_account:
            break

    if not mt_account:
        print(f"  ❌ 没找到可登录的美团账号")
        for name, accts in stores.items():
            for a in accts:
                print(f"    {a['platform']} {a['account']} {a['action']}")
        return False

    # 登录
    r = await click_store_platform(ext, mt_account)
    if r != 'ok':
        print(f"  ❌ 登录失败: {r}")
        return False

    # 等页面加载
    print(f"  ⏳ 等美团后台加载（账号: {mt_account}）...")
    for _ in range(30):
        for p in ctx.pages:
            if 'e.waimai.meituan.com' in p.url:
                blocked, desc = await check_verification(p)
                if blocked:
                    print(f"  ⚠️ 被拦截: {desc}")
                    return False
                # 检查是否有内容
                try:
                    text = await p.evaluate("() => document.body.innerText.substring(0, 200)")
                    if '商家首页' in text or '经营分析' in text:
                        # 关弹窗
                        await p.evaluate("""() => {
                            document.querySelectorAll('button, div').forEach(b => {
                                if (b.textContent.trim() === '我知道了' && b.offsetParent) b.click();
                            });
                        }""")
                        await asyncio.sleep(1)
                        print(f"  ✅ 登录成功")
                        return True
                except:
                    pass
        await asyncio.sleep(1)

    print(f"  ❌ 加载超时")
    return False


async def main():
    stores = [
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

    # 支持从指定序号开始
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    ws = await cdp_ws()
    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0]

        # 获取悟空插件
        ext = await get_ext(ctx)

        results = {}
        for i, store in enumerate(stores):
            if i < start:
                continue

            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(stores)}] {store}")
            print(f"{'='*60}")

            # 登录
            ok = await login_store(ctx, ext, store)
            if not ok:
                results[store] = "❌ 登录失败"
                continue

            # 找美团页面
            mt_page = None
            for p in ctx.pages:
                if 'e.waimai.meituan.com' in p.url and 'chrome-extension' not in p.url:
                    mt_page = p
                    break

            if not mt_page:
                results[store] = "❌ 找不到页面"
                continue

            # 采集
            data = await crawl_store_data(mt_page)

            # 保存
            safe = store.replace("（", "_").replace("）", "").replace("·", "_").replace(" ", "").replace(".", "_")
            out = os.path.join(OUT_DIR, f"crawl_raw_{safe}_{TODAY}.json")
            with open(out, 'w', encoding='utf-8') as f:
                json.dump({"store": store, "data": data}, f, ensure_ascii=False, indent=2)

            total_chars = sum(len(v) for v in data.values())
            results[store] = f"✅ {len(data)} tabs, {total_chars} chars → {out}"
            print(f"  💾 {out}")

            # 关闭页面
            await close_store_pages(ctx)
            await asyncio.sleep(2)

        # 汇总
        print(f"\n{'='*60}")
        print(f"采集汇总")
        print(f"{'='*60}")
        for store, result in results.items():
            print(f"  {store}: {result}")

asyncio.run(main())

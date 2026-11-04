"""Offline proof for the MoneyBall PWA kit (Dispatch #2 annex §1).

Run against a locally served copy of the site:
  MB_SITE_URL=http://localhost:8931 python3 test_pwa_offline.py

Asserts, in order: the service worker CONTROLS the first load
(the SOFA caveat), feeds render online, then — fully offline —
the index renders from cache, an unvisited page renders its
precached shell + feed, and the large pools feed renders from
the SWR runtime cache after one online visit.
"""
import asyncio
import os
import sys

from playwright.async_api import async_playwright

BASE = os.environ.get("MB_SITE_URL", "http://localhost:8931")


async def main() -> int:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{BASE}/index.html")
        await page.wait_for_function(
            "() => navigator.serviceWorker && "
            "navigator.serviceWorker.controller !== null",
            timeout=15000,
        )
        print("PASS sw controls the first load")
        await page.wait_for_function(
            "() => { const el = document.getElementById('subjects');"
            " return el && el.textContent.trim().length > 40 &&"
            " !el.textContent.includes('failed to load'); }",
            timeout=15000,
        )
        print("PASS index feed renders online")
        await page.goto(f"{BASE}/pools.html")
        await page.wait_for_function(
            "() => { const el = document.getElementById('pools');"
            " return el && el.textContent.trim().length > 40 &&"
            " !el.textContent.includes('failed to load'); }",
            timeout=15000,
        )
        print("PASS pools feed renders online (now SWR-cached)")
        await ctx.set_offline(True)
        await page.goto(f"{BASE}/index.html")
        await page.wait_for_function(
            "() => { const el = document.getElementById('subjects');"
            " return el && el.textContent.trim().length > 40 &&"
            " !el.textContent.includes('failed to load'); }",
            timeout=15000,
        )
        print("PASS index renders OFFLINE from cache")
        await page.goto(f"{BASE}/settlement.html")
        await page.wait_for_function(
            "() => document.body.textContent.trim().length > 200",
            timeout=15000,
        )
        print("PASS unvisited settlement page renders OFFLINE "
              "(precached shell)")
        await page.goto(f"{BASE}/pools.html")
        await page.wait_for_function(
            "() => { const el = document.getElementById('pools');"
            " return el && el.textContent.trim().length > 40 &&"
            " !el.textContent.includes('failed to load'); }",
            timeout=15000,
        )
        print("PASS pools renders OFFLINE from SWR cache")
        manifest = await page.evaluate(
            "async () => { const r = await fetch('manifest.webmanifest');"
            " const j = await r.json(); return j.short_name + '|' +"
            " j.display + '|' + j.icons.length; }"
        )
        assert manifest == "MoneyBall|standalone|3", manifest
        print("PASS manifest served + parseable:", manifest)
        await browser.close()
    print("PWA OFFLINE PROOF: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

"""Wallets page acceptance (Dispatch POPULATE, Web3 seat): rendered counts ==
wallets-feed stamp, genesis balances fold-proven, no numeric-% anywhere
(§11 / Amendment 6 discipline), offline re-render from the SW cache.

Run: python3 tests/test_wallets_page.py [base_url]  (default: serve repo root)
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = sys.argv[1] if len(sys.argv) > 1 else None


def main() -> int:
    feed = json.loads((ROOT / "data" / "wallets-feed.json").read_text())
    rc = feed["reconciliation"]
    server = None
    base = BASE
    if base is None:
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8934", "--bind", "127.0.0.1"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        base = "http://127.0.0.1:8934"
        for _ in range(50):
            try:
                urllib.request.urlopen(base + "/wallets.html", timeout=1)
                break
            except Exception:
                time.sleep(0.2)
    fails = []

    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
        if not ok:
            fails.append(name)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(base + "/wallets.html", wait_until="networkidle")
            page.wait_for_selector("#genesis .row", timeout=20000)
            n_feed = page.inner_text("#n-feed").replace(",", "")
            n_paper = page.inner_text("#n-paper").replace(",", "")
            n_pool = page.inner_text("#n-pool").replace(",", "")
            check("counts == feed stamp",
                  (int(n_feed), int(n_paper), int(n_pool))
                  == (rc["feed_wallets"], rc["paper_wallets"], rc["pool_wallets"]),
                  f"rendered {n_feed}/{n_paper}/{n_pool} vs stamp "
                  f"{rc['feed_wallets']}/{rc['paper_wallets']}/{rc['pool_wallets']}")
            grows = page.query_selector_all("#genesis .row")
            check("genesis rows == paper_wallets", len(grows) == rc["paper_wallets"],
                  f"{len(grows)} rows")
            bals = [r.inner_text() for r in grows]
            check("genesis balances all 1,000 (fold-proven)",
                  all("1,000" in b for b in bals))
            check("genesis rows carry ledger receipts",
                  all("wallet-ledger.jsonl seq" in b for b in bals))
            prows = page.query_selector_all("#pools .row")
            check("pool rows == pool_wallets", len(prows) == rc["pool_wallets"],
                  f"{len(prows)} rows")
            body = page.inner_text("body")
            check("no numeric-% figure anywhere (Amendment 6)",
                  not re.search(r"\d\s?%", body))
            check("substrate summary names all 5 basis points",
                  all(s in body for s in [
                      "required to wager on QUE tasks", "per agent contract",
                      "granted pooled funding", "Discounted agent-team custom requests",
                      "allocation algorithms"]))
            # offline: SW controls + feed is SWR-cached after first load
            page.wait_for_function(
                "() => navigator.serviceWorker && navigator.serviceWorker.controller",
                timeout=20000)
            ctx.set_offline(True)
            page.reload(wait_until="domcontentloaded")
            page.wait_for_selector("#genesis .row", timeout=20000)
            check("offline re-render: genesis rows from cache",
                  len(page.query_selector_all("#genesis .row")) == rc["paper_wallets"])
            ctx.set_offline(False)
            browser.close()
    finally:
        if server:
            server.terminate()
    print("VERDICT:", "PASS" if not fails else f"FAIL {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

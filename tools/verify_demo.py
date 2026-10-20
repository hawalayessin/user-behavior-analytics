"""Exercise the public demo without an API server or database."""

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5174"
OUTPUT = Path("C:/tmp/insighthub-demo-check")
OUTPUT.mkdir(exist_ok=True)
ROUTES = ["/dashboard", "/analytics/behaviors", "/analytics/trial", "/analytics/campaigns", "/analytics/retention", "/analytics/churn", "/analytics/cross-service", "/analytics/churn-prediction", "/analytics/segmentation", "/analytics/anomalies", "/management/subscribers", "/notes", "/admin/reports", "/admin/users", "/admin/import", "/admin/management", "/admin/settings", "/admin/run-ai-models", "/account/profile"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    console_errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda e: console_errors.append(e.text) if e.type == "error" else None)
    results = []
    for route in ROUTES:
        before = len(errors)
        page.goto(BASE + route)
        page.wait_for_timeout(1300)
        body = page.locator("body").inner_text()
        issues = [line for line in body.splitlines() if "not available in the portfolio demo" in line or "Unknown demo" in line]
        results.append({"route": route, "text": body, "errors": errors[before:], "issues": issues})
        print(route, "chars=", len(body), "errors=", len(errors) - before, "issues=", issues, flush=True)
        if route in ["/dashboard", "/analytics/segmentation", "/analytics/churn-prediction"]:
            page.screenshot(path=str(OUTPUT / (route.split('/')[-1] + '.png')))
    (OUTPUT / "results.json").write_text(json.dumps({"routes": results, "errors": errors, "console": console_errors}, indent=2), encoding="utf-8")
    browser.close()
    if errors or any(r["issues"] for r in results):
        sys.exit(1)

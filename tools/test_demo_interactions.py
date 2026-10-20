"""Check demo filtering, pagination, isolated writes, and PDF downloads."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    page.goto("http://127.0.0.1:5174/dashboard")
    page.get_by_role("button", name="All services", exact=True).wait_for()
    result = page.evaluate("""async () => {
      const { resolveDemoRequest: request } = await import('/src/demo/adapter.js');
      const o = await request('/analytics/overview');
      if (o.users.total !== 160) throw Error('Subscriber count');
      if (o.top_services.reduce((n, s) => n + s.total, 0) !== 160) throw Error('Service totals');
      const filtered = await request('/analytics/overview', 'get', null, {service_id: 'demo-tawer'});
      if (filtered.users.total !== 40 || filtered.top_services.length !== 1) throw Error('Service filter');
      const empty = await request('/analytics/overview?start_date=2026-01-01');
      if (empty.users.total !== 0 || empty.engagement.trend.length !== 0) throw Error('Empty range');
      const first = await request('/users?page_size=10');
      const second = await request('/users', 'get', null, {page_size: 10, cursor_id: first.next_cursor.id});
      if (first.data.some(a => second.data.some(b => a.id === b.id))) throw Error('Cursor overlap');
      const found = await request('/users?search=DEMO-0001');
      if (found.data.length !== 1) throw Error('Search');
      const risk = await request('/ml/churn/scores?threshold=0.4&page_size=10');
      const riskNext = await request('/ml/churn/scores?threshold=0.4&page_size=10&page=2');
      const high = await request('/ml/churn/scores?threshold=0.6');
      if (high.total > risk.total || risk.top_users.some(u => u.churn_risk < 0.4)) throw Error('Risk threshold');
      if (risk.top_users.some(a => riskNext.top_users.some(b => a.user_id === b.user_id))) throw Error('Risk pagination');
      const note = await request('/notes', 'post', {content: 'Portfolio interaction test', metric: 'DAU'});
      if (!(await request('/notes')).some(n => n.id === note.id)) throw Error('Create note');
      await request('/notes/' + note.id, 'delete');
      if ((await request('/notes')).some(n => n.id === note.id)) throw Error('Delete note');
      try { await request('/admin/import/csv', 'post'); throw Error('Import was accepted'); }
      catch(e) { if (e.status !== 403) throw e; }
      const report = await request('/reports/generate', 'post', {period_start:'2025-09-01', period_end:'2025-10-31'});
      const pdf = await request('/reports/download/' + report.report_id);
      if (!(await pdf.text()).startsWith('%PDF-')) throw Error('Invalid PDF');
      return {subscribers: o.users.total, filtered: filtered.users.total, risky: risk.total, pdf_bytes: pdf.size};
    }""")
    print("Data and API checks:", result, flush=True)
    page.get_by_role("button", name="All services", exact=True).click()
    page.get_by_role("button", name="Tawer", exact=True).click()
    page.get_by_role("button", name="Apply filters", exact=True).click()
    page.wait_for_timeout(1500)
    assert "160" not in page.locator("main").inner_text().split("Total Users")[1].split("Active Subscriptions")[0]
    print("Service filter UI: passed", flush=True)
    page.goto("http://127.0.0.1:5174/admin/reports")
    page.get_by_role("button", name=re.compile("Generate Report")).click()
    page.get_by_text("Report Generated", exact=False).wait_for(timeout=15000)
    print("Report UI: generated", flush=True)
    buttons = page.get_by_role("button").all_inner_texts()
    print("Report actions:", [b for b in buttons if "Download" in b], flush=True)
    with page.expect_download() as download_event:
        page.get_by_role("button", name=re.compile("Download")).last.click()
    download = download_event.value
    target = Path("C:/tmp/insighthub-demo-check/report.pdf")
    download.save_as(target)
    assert target.read_bytes().startswith(b"%PDF-")
    print("PDF download UI: passed", flush=True)
    mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
    mobile.goto("http://127.0.0.1:5174/dashboard")
    mobile.wait_for_timeout(1500)
    mobile.screenshot(path="C:/tmp/insighthub-demo-check/mobile.png")
    print("Mobile overflow:", mobile.evaluate("document.documentElement.scrollWidth > innerWidth"), flush=True)
    browser.close()

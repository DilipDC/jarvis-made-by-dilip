from __future__ import annotations
import importlib.util
class BrowserManager:
    def __init__(self): self.available=bool(importlib.util.find_spec('playwright'))
    def health(self): return {'available':self.available}
    def fetch_title(self,url):
        if not self.available: raise RuntimeError('Playwright not installed')
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True); page=browser.new_page(); page.goto(url,wait_until='domcontentloaded',timeout=15000); data={'url':page.url,'title':page.title()}; browser.close(); return data

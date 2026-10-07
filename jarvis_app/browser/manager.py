from __future__ import annotations
import importlib.util, platform, shutil, subprocess, urllib.parse, webbrowser

class BrowserManager:
    def __init__(self): self.available=bool(importlib.util.find_spec("playwright")); self.system=platform.system()
    def health(self):
        return {"available":self.available or bool(shutil.which("xdg-open") or shutil.which("start") or shutil.which("open")),
                "playwright":self.available,"system_browser":True,"platform":self.system}
    def fetch_title(self,url):
        if not self.available: raise RuntimeError("Playwright is not installed; system browser search still works.")
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True); page=browser.new_page()
            page.goto(url,wait_until="domcontentloaded",timeout=15000)
            data={"url":page.url,"title":page.title()};browser.close();return data
    def search(self,query):
        url="https://www.google.com/search?"+urllib.parse.urlencode({"q":query})
        ok=webbrowser.open(url,new=2)
        return {"opened":bool(ok),"url":url,"query":query,"browser":"system default"}

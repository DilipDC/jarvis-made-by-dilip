from __future__ import annotations
import html, re, time
import httpx
class WebSearch:
    def __init__(self,timeout=12): self.timeout=timeout
    def search(self,query):
        r=httpx.get('https://html.duckduckgo.com/html/',params={'q':query},headers={'User-Agent':'JARVIS/0.2'},timeout=self.timeout,follow_redirects=True); r.raise_for_status(); items=[]
        pattern=re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',re.S|re.I)
        for m in pattern.finditer(r.text):
            title=re.sub(r'<.*?>','',m.group(2)); title=html.unescape(re.sub(r'\s+',' ',title)).strip(); items.append({'title':title,'url':html.unescape(m.group(1))})
            if len(items)>=8: break
        return {'query':query,'results':items,'retrieved_at':time.time()}

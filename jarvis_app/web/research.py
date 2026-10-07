from __future__ import annotations
import html,re,time
from html.parser import HTMLParser
from urllib.parse import urlparse
import httpx

class _TextExtractor(HTMLParser):
    SKIP={"script","style","noscript","svg","nav","footer","header","form"}
    def __init__(self): super().__init__(); self.depth=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in self.SKIP:self.depth+=1
    def handle_endtag(self,tag):
        if tag.lower() in self.SKIP and self.depth:self.depth-=1
    def handle_data(self,data):
        if not self.depth:
            text=re.sub(r"\s+", " ", html.unescape(data)).strip()
            if text:self.parts.append(text)
    def text(self): return " ".join(self.parts)

class WebResearchAgent:
    """Low-RAM search -> fetch -> extract -> synthesize -> cite pipeline."""
    def __init__(self,searcher,timeout=10,max_results=4,max_chars_per_page=5000):
        self.searcher=searcher; self.timeout=timeout; self.max_results=max_results; self.max_chars_per_page=max_chars_per_page
    def _fetch(self,url):
        p=urlparse(url)
        if p.scheme not in {"http","https"}: return ""
        try:
            r=httpx.get(url,headers={"User-Agent":"JARVIS/1.0 local-research"},timeout=self.timeout,follow_redirects=True)
            r.raise_for_status()
            if "text/html" not in r.headers.get("content-type","").lower(): return ""
            parser=_TextExtractor(); parser.feed(r.text)
            return parser.text()[:self.max_chars_per_page]
        except Exception: return ""
    def research(self,query,ollama=None,model=None,cache=None):
        started=time.perf_counter()
        key=cache.key("web-research",query.lower()) if cache else None
        if cache and key:
            hit=cache.get(key)
            if hit:return {**hit,"cache":"hit"}
        search=self.searcher.search(query); sources=[]; context=[]
        for idx,item in enumerate(search.get("results",[])[:self.max_results],1):
            body=self._fetch(item["url"])
            sources.append({"id":idx,"title":item["title"],"url":item["url"],"content_available":bool(body)})
            if body:context.append(f"[SOURCE {idx}] {item['title']}\nURL: {item['url']}\nCONTENT:\n{body}")
        if not context:
            answer="I could not retrieve readable source content. The search results are listed below."
        elif ollama and model:
            prompt=("Answer the user's question using ONLY the supplied web sources. Prefer agreement across sources, "
                    "identify uncertainty, do not invent facts, and cite claims inline as [1], [2], etc.\n\n"
                    f"QUESTION: {query}\n\n" + "\n\n".join(context))
            try:
                r=ollama.chat(model,[{"role":"system","content":"You are JARVIS WebResearchAgent, a careful research synthesizer."},{"role":"user","content":prompt}],False)
                answer=r.get("message",{}).get("content","").strip() or "No synthesis was returned."
            except Exception as exc: answer=f"Web sources were retrieved, but local synthesis failed: {exc}"
        else: answer="\n\n".join(x.split("\nCONTENT:\n",1)[0] for x in context)
        result={"text":answer,"query":query,"intent":"web_research","sources":sources,"retrieved_at":time.time(),"latency_ms":round((time.perf_counter()-started)*1000,2),"cache":"miss"}
        if cache and key:cache.set(key,result,ttl=180,source="web-research")
        return result

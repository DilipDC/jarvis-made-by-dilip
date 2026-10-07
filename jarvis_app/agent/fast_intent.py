from __future__ import annotations
import re

RULES=[
 ('reminder', re.compile(r'\b(remind me|reminder|remind)\b',re.I)),
 ('ram', re.compile(r'\b(ram|memory usage|memory percentage)\b',re.I)),
 ('cpu', re.compile(r'\b(cpu|processor usage|cpu usage)\b',re.I)),
 ('time', re.compile(r'\b(what time|current time|time now)\b',re.I)),
 ('remember', re.compile(r'^\s*remember\b',re.I)),
 ('forget', re.compile(r'^\s*forget\b',re.I)),
 ('python', re.compile(r'\b(execute|run|start)\s+[\w./\\-]+\.py\b',re.I)),
 ('computer', re.compile(r'\b(click|double click|type|press|hotkey|move mouse|screenshot|control (my|the) (computer|desktop)|control windows|control linux)\b',re.I)),
 ('browser_search', re.compile(r'\b(open|launch)\s+(the\s+)?(browser|chrome|firefox|edge)\s+(and\s+)?(search|look up)\b',re.I)),
 ('list_tasks', re.compile(r'\b(task status|running tasks|python tasks|list tasks)\b',re.I)),
 ('terminal', re.compile(r'^\s*(run|execute)\s+(command|terminal)\b',re.I)),
 ('status', re.compile(r'\b(system status|jarvis status|health|diagnostics|doctor)\b',re.I)),
]

def classify(text:str)->str:
    for n,p in RULES:
        if p.search(text): return n
    if re.search(r'\b(latest|current|today|price|weather|news|documentation|search the web|search online|search for|look up|stock|share price)\b',text,re.I):
        return 'web'
    if re.search(r'\b(delete|shutdown|reboot|kill process|stop process|firewall|send message|run command)\b',text,re.I): return 'sensitive'
    if re.search(r'\b(explain|fix|debug|code|coding|python|javascript|typescript|program)\b', text, re.I): return 'coding'
    if re.search(r'\b(plan|build|implement|steps|multiple tasks|do all of this)\b',text,re.I): return 'planning'
    return 'chat'

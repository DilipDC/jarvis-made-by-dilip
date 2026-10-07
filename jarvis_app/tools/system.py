from __future__ import annotations
import platform, shutil, subprocess, urllib.parse, webbrowser
def open_application(name):
    n=name.strip()
    aliases={"browser":"__browser__","chrome":"google-chrome","google chrome":"google-chrome",
             "firefox":"firefox","edge":"msedge","editor":"__editor__","vscode":"code","vs code":"code",
             "notepad":"notepad.exe","gedit":"gedit"}
    target=aliases.get(n.lower(),n)
    if target=="__browser__":
        return browser_search("")
    if target=="__editor__":
        target="notepad.exe" if platform.system()=="Windows" else "gedit"
    try:
        if platform.system()=="Windows":
            p=subprocess.Popen(["cmd","/c","start","",target])
        elif platform.system()=="Darwin":
            p=subprocess.Popen(["open",target])
        else:
            exe=shutil.which(target)
            if not exe: return {"started":False,"error":f"Application not found: {target}"}
            p=subprocess.Popen([exe])
        return {"started":True,"pid":p.pid,"application":target}
    except Exception as exc:return {"started":False,"error":str(exc)}

def browser_search(query):
    q=query.strip()
    if not q:return {"started":False,"error":"No search query supplied"}
    url="https://www.google.com/search?"+urllib.parse.urlencode({"q":q})
    try:
        ok=webbrowser.open(url,new=2)
        return {"started":bool(ok),"url":url,"query":q}
    except Exception as exc:return {"started":False,"error":str(exc)}
def system_info():
    import datetime, psutil
    vm=psutil.virtual_memory()
    return {"platform":platform.platform(),"cpu_percent":psutil.cpu_percent(interval=.1),
            "cpu_count":psutil.cpu_count(),"ram_percent":vm.percent,"ram_available":vm.available,
            "disk_free":shutil.disk_usage("/").free,"time":datetime.datetime.now().isoformat(timespec="seconds")}

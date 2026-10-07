from __future__ import annotations
import gc
try:import psutil
except ImportError:psutil=None
def snapshot(soft_limit_gb=3.5,critical_limit_gb=3.85):
    if psutil is None:return {"available":False,"mode":"UNKNOWN"}
    p=psutil.Process(); vm=psutil.virtual_memory(); rss=p.memory_info().rss; rss_gb=rss/(1024**3)
    mode="CRITICAL" if vm.percent>=92 or rss_gb>=critical_limit_gb else ("LOW" if vm.percent>=78 or rss_gb>=soft_limit_gb else "NORMAL")
    return {"available":True,"mode":mode,"system_ram_percent":vm.percent,"system_available_gb":round(vm.available/(1024**3),2),"process_rss_mb":round(rss/(1024**2),1),"system_total_gb":round(vm.total/(1024**3),2),"process_pid":p.pid}
def low_ram_cleanup():
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():torch.cuda.empty_cache()
    except Exception:pass

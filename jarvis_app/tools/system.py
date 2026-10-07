from __future__ import annotations
import os, platform, shutil, subprocess, time
try: import psutil
except Exception: psutil=None

def system_info():
    info={'os':platform.system(),'release':platform.release(),'machine':platform.machine(),'python':platform.python_version(),'time':time.strftime('%Y-%m-%d %H:%M:%S')}
    if psutil:
        vm=psutil.virtual_memory(); disk=psutil.disk_usage(os.path.abspath(os.sep)); info.update({'cpu_percent':psutil.cpu_percent(interval=0.02),'cpu_count':psutil.cpu_count(),'ram_percent':vm.percent,'ram_total':vm.total,'ram_available':vm.available,'disk_percent':disk.percent})
    return info

def open_application(name:str):
    system=platform.system()
    aliases={'chrome':'google-chrome','google chrome':'google-chrome','firefox':'firefox','edge':'microsoft-edge'}
    target=aliases.get(name.lower(),name)
    if system=='Windows':
        p=subprocess.Popen(['cmd','/c','start','',target])
    elif system=='Darwin':
        p=subprocess.Popen(['open',target])
    else:
        exe=shutil.which(target)
        p=subprocess.Popen([exe or 'xdg-open',target] if exe else ['xdg-open',target])
    time.sleep(0.05)
    return {'started':True,'pid':p.pid,'target':target,'launcher_alive':p.poll() is None}

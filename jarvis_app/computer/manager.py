from __future__ import annotations
import importlib.util, platform, subprocess
class ComputerControlManager:
    def __init__(self): self.pyautogui=bool(importlib.util.find_spec('pyautogui'))
    def health(self): return {'platform':platform.system(),'pyautogui_available':self.pyautogui}
    def open_app(self,name):
        if platform.system()=='Windows': p=subprocess.Popen(['cmd','/c','start','',name])
        else: p=subprocess.Popen(['xdg-open',name])
        return {'pid':p.pid,'started':True}

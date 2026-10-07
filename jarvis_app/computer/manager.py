from __future__ import annotations
import importlib.util, platform, subprocess, time

class ComputerControlManager:
    def __init__(self):
        self.pyautogui=bool(importlib.util.find_spec("pyautogui"))

    def health(self):
        return {"platform":platform.system(),"pyautogui_available":self.pyautogui,"approved_actions":True}

    def open_app(self,name):
        if platform.system()=="Windows":
            p=subprocess.Popen(["cmd","/c","start","",name])
        else:
            p=subprocess.Popen(["xdg-open",name])
        return {"pid":p.pid,"started":True}

    def act(self,action,**kwargs):
        if not self.pyautogui:
            raise RuntimeError("Desktop control requires the optional computer extra: pip install -e '.[computer]'")
        import pyautogui
        if action=="click":
            pyautogui.click(int(kwargs["x"]),int(kwargs["y"]))
        elif action=="double_click":
            pyautogui.doubleClick(int(kwargs["x"]),int(kwargs["y"]))
        elif action=="type":
            pyautogui.write(str(kwargs["text"]),interval=0.01)
        elif action=="press":
            pyautogui.press(str(kwargs["key"]))
        elif action=="hotkey":
            pyautogui.hotkey(*[x.strip() for x in str(kwargs["keys"]).split("+")])
        elif action=="screenshot":
            path=str(kwargs.get("path","jarvis_screenshot.png"))
            pyautogui.screenshot(path)
            return {"action":action,"path":path}
        elif action=="move":
            pyautogui.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=0.15)
        else:
            raise ValueError(f"Unsupported desktop action: {action}")
        time.sleep(0.08)
        return {"action":action,"ok":True}

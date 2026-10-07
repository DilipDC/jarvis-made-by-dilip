from __future__ import annotations
import importlib.util, os, platform, shutil, subprocess, time
from pathlib import Path

class ComputerControlManager:
    """Cross-platform, visible desktop automation with explicit action boundaries."""
    def __init__(self, events=None):
        self.pyautogui=bool(importlib.util.find_spec("pyautogui"))
        self.events=events

    def _emit(self,event,**data):
        if self.events:
            try:self.events.emit(event,**data)
            except Exception:pass

    def health(self):
        return {"platform":platform.system(),"pyautogui_available":self.pyautogui,
                "approved_actions":True,"visible_control":self.pyautogui,
                "cursor_animation":self.pyautogui}

    def open_app(self,name):
        system=platform.system()
        n=name.strip()
        if system=="Windows":
            p=subprocess.Popen(["cmd","/c","start","",n],shell=False)
        elif system=="Darwin":
            p=subprocess.Popen(["open",n])
        else:
            # Try desktop launcher first, then common editors.
            aliases={"editor":"gedit","text editor":"gedit","vscode":"code","vs code":"code",
                     "code editor":"code","terminal":"x-terminal-emulator"}
            target=aliases.get(n.lower(),n)
            exe=shutil.which(target)
            if not exe and target in {"gedit","code","x-terminal-emulator"}:
                raise RuntimeError(f"Application '{n}' is not installed on this Linux desktop.")
            p=subprocess.Popen([exe or target])
        self._emit("computer.action",action="open_app",target=n,state="DONE")
        return {"pid":p.pid,"started":True,"application":n}

    def act(self,action,**kwargs):
        if action=="open_app":
            return self.open_app(str(kwargs.get("name","")))
        if not self.pyautogui:
            raise RuntimeError("Desktop control unavailable. Install: python -m pip install -e '.[computer]'")
        import pyautogui
        self._emit("computer.action",action=action,state="START",x=kwargs.get("x"),y=kwargs.get("y"))
        try:
            if action=="move":
                pyautogui.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.25)
            elif action=="click":
                pyautogui.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.18); pyautogui.click()
            elif action=="double_click":
                pyautogui.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.18); pyautogui.doubleClick()
            elif action=="type":
                text=str(kwargs.get("text",""))
                # write() is fast but poor for Unicode; clipboard paste handles both when available.
                try:
                    import pyperclip
                    pyperclip.copy(text); pyautogui.hotkey("ctrl","v")
                except Exception:
                    pyautogui.write(text,interval=.008)
            elif action=="press": pyautogui.press(str(kwargs["key"]))
            elif action=="hotkey": pyautogui.hotkey(*[x.strip() for x in str(kwargs["keys"]).split("+") if x.strip()])
            elif action=="screenshot":
                path=str(kwargs.get("path") or Path.cwd()/"jarvis_screenshot.png")
                pyautogui.screenshot(path); self._emit("computer.screenshot",path=path)
                return {"action":action,"path":path,"ok":True}
            else: raise ValueError(f"Unsupported desktop action: {action}")
            time.sleep(.08)
            self._emit("computer.action",action=action,state="DONE",x=kwargs.get("x"),y=kwargs.get("y"))
            return {"action":action,"ok":True}
        except Exception as exc:
            self._emit("computer.action",action=action,state="ERROR",error=str(exc))
            raise

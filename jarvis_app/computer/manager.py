from __future__ import annotations
import importlib.util, os, platform, shutil, subprocess, time
from pathlib import Path

class ComputerControlManager:
    """Cross-platform visible desktop automation with Linux fallbacks."""
    def __init__(self, events=None):
        self.events=events
        self.pyautogui_available=bool(importlib.util.find_spec("pyautogui"))
        self.mss_available=bool(importlib.util.find_spec("mss"))
        self.xdotool=shutil.which("xdotool")
        self._pyautogui=None
        if self.pyautogui_available:
            try:
                import pyautogui
                self._pyautogui=pyautogui
            except Exception:
                self._pyautogui=None

    def _emit(self,event,**data):
        if self.events:
            try:self.events.emit(event,**data)
            except Exception:pass

    def health(self):
        return {
            "platform":platform.system(),
            "pyautogui_available":self._pyautogui is not None,
            "pyautogui_installed":self.pyautogui_available,
            "xdotool_available":bool(self.xdotool),
            "mss_available":self.mss_available,
            "approved_actions":True,
            "visible_control":bool(self._pyautogui or self.xdotool),
            "cursor_animation":bool(self._pyautogui or self.xdotool),
        }

    def open_app(self,name):
        system=platform.system()
        n=name.strip()
        if system=="Windows":
            p=subprocess.Popen(["cmd","/c","start","",n],shell=False)
        elif system=="Darwin":
            p=subprocess.Popen(["open",n])
        else:
            aliases={"editor":"gedit","text editor":"gedit","vscode":"code","vs code":"code","code editor":"code","terminal":"x-terminal-emulator","browser":"firefox","google chrome":"google-chrome","chrome":"google-chrome"}
            target=aliases.get(n.lower(),n)
            exe=shutil.which(target)
            if not exe:return {"started":False,"application":n,"error":f"Application not found: {target}"}
            p=subprocess.Popen([exe])
        self._emit("computer.action",action="open_app",target=n,state="DONE",pid=p.pid)
        return {"pid":p.pid,"started":True,"application":n}

    def _fallback_input(self,action,**kwargs):
        if platform.system()!="Linux" or not self.xdotool:
            raise RuntimeError("Desktop input unavailable. Install xdotool or repair PyAutoGUI dependencies.")
        if action=="move":
            subprocess.run([self.xdotool,"mousemove",str(int(kwargs["x"])),str(int(kwargs["y"]))],check=True)
        elif action=="click":
            subprocess.run([self.xdotool,"mousemove",str(int(kwargs["x"])),str(int(kwargs["y"]))],check=True)
            subprocess.run([self.xdotool,"click","1"],check=True)
        elif action=="double_click":
            subprocess.run([self.xdotool,"mousemove",str(int(kwargs["x"])),str(int(kwargs["y"]))],check=True)
            subprocess.run([self.xdotool,"click","--repeat","2","--delay","100","1"],check=True)
        elif action=="type":
            subprocess.run([self.xdotool,"type","--delay","8",str(kwargs.get("text",""))],check=True)
        elif action=="press":
            subprocess.run([self.xdotool,"key",str(kwargs["key"])],check=True)
        elif action=="hotkey":
            keys="+".join(x.strip() for x in str(kwargs["keys"]).split("+") if x.strip())
            subprocess.run([self.xdotool,"key",keys],check=True)
        else:raise ValueError(f"Unsupported desktop action: {action}")

    def _screenshot(self,path):
        if self.mss_available:
            import mss
            with mss.mss() as sct:
                monitor=sct.monitors[1] if len(sct.monitors)>1 else sct.monitors[0]
                shot=sct.grab(monitor)
                mss.tools.to_png(shot.rgb,shot.size,output=path)
                return {"action":"screenshot","path":path,"ok":True,"backend":"mss"}
        if self._pyautogui is not None:
            self._pyautogui.screenshot(path)
            return {"action":"screenshot","path":path,"ok":True,"backend":"pyautogui"}
        raise RuntimeError("Screenshot unavailable. Install mss with: python -m pip install mss")

    def act(self,action,**kwargs):
        if action=="open_app":return self.open_app(str(kwargs.get("name","")))
        if action=="screenshot":
            path=str(kwargs.get("path") or Path.cwd()/"jarvis_screenshot.png")
            result=self._screenshot(path)
            self._emit("computer.screenshot",path=path,backend=result.get("backend"))
            return result
        self._emit("computer.action",action=action,state="START",x=kwargs.get("x"),y=kwargs.get("y"))
        try:
            if self._pyautogui is not None:
                p=self._pyautogui
                if action=="move":p.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.25)
                elif action=="click":p.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.18);p.click()
                elif action=="double_click":p.moveTo(int(kwargs["x"]),int(kwargs["y"]),duration=.18);p.doubleClick()
                elif action=="type":
                    text=str(kwargs.get("text",""))
                    try:
                        import pyperclip
                        pyperclip.copy(text);p.hotkey("ctrl","v")
                    except Exception:p.write(text,interval=.008)
                elif action=="press":p.press(str(kwargs["key"]))
                elif action=="hotkey":p.hotkey(*[x.strip() for x in str(kwargs["keys"]).split("+") if x.strip()])
                else:raise ValueError(f"Unsupported desktop action: {action}")
            else:self._fallback_input(action,**kwargs)
            time.sleep(.08)
            self._emit("computer.action",action=action,state="DONE",x=kwargs.get("x"),y=kwargs.get("y"))
            return {"action":action,"ok":True,"backend":"pyautogui" if self._pyautogui is not None else "xdotool"}
        except Exception as exc:
            self._emit("computer.action",action=action,state="ERROR",error=str(exc));raise
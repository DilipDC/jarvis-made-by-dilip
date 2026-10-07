from __future__ import annotations
import os, platform, subprocess, shlex
from dataclasses import dataclass

@dataclass
class CommandResult:
    returncode:int; stdout:str; stderr:str

class TerminalManager:
    def __init__(self, timeout=30): self.timeout=timeout
    def run(self, argv:list[str], cwd=None):
        p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=self.timeout,shell=False)
        return CommandResult(p.returncode,p.stdout[-12000:],p.stderr[-12000:])
    def run_line(self, line:str, cwd=None):
        if platform.system()=='Windows': return self.run(['powershell','-NoProfile','-Command',line],cwd)
        return self.run(['/bin/bash','-lc',line],cwd)

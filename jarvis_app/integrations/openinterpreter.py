from __future__ import annotations
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

class OpenInterpreterAdapter:
    """Optional Linux execution/agent bridge using the official Open Interpreter CLI.

    JARVIS does not embed Open Interpreter source. It delegates through its
    public CLI with an explicit sandbox and approval policy.
    """

    def __init__(self,enabled=True,timeout=180,model="qwen3:0.6b",local_provider="ollama"):
        self.enabled=bool(enabled)
        self.timeout=max(10,int(timeout))
        self.model=model
        self.local_provider=local_provider
        self.binary=shutil.which(os.getenv("JARVIS_INTERPRETER_BIN","interpreter"))

    @property
    def available(self):
        return self.enabled and platform.system()=="Linux" and bool(self.binary)

    def health(self):
        return {
            "available":self.available,
            "enabled":self.enabled,
            "platform":platform.system(),
            "binary":self.binary,
            "model":self.model,
            "provider":self.local_provider,
        }

    def run(self,prompt,cwd=None,write=False):
        if not self.available:
            raise RuntimeError(
                "Open Interpreter is unavailable. Install it with scripts/install_openinterpreter_linux.sh"
            )
        workdir=str(Path(cwd or Path.cwd()).expanduser().resolve())
        sandbox="workspace-write" if write else "read-only"

        cmd=[
            self.binary,"exec",
            "--oss",
            "--local-provider",self.local_provider,
            "--model",self.model,
            "--sandbox",sandbox,
            "--ask-for-approval","on-request",
            "--cd",workdir,
            str(prompt).strip(),
        ]

        start=time.perf_counter()
        proc=subprocess.run(
            cmd,
            cwd=workdir,
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        return {
            "ok":proc.returncode==0,
            "returncode":proc.returncode,
            "stdout":proc.stdout[-12000:],
            "stderr":proc.stderr[-6000:],
            "latency_ms":round((time.perf_counter()-start)*1000,2),
            "sandbox":sandbox,
            "cwd":workdir,
            "command":["interpreter","exec","..."],
        }

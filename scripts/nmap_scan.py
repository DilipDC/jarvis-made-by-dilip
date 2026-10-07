"""Bounded Nmap wrapper for authorized network diagnostics.

Usage:
  python scripts/nmap_scan.py 192.168.1.0/24
  python scripts/nmap_scan.py 192.168.1.1

Only service/version discovery on the top 100 ports is performed.
Use only on networks and systems you own or are authorized to test.
"""
from __future__ import annotations
import shutil
import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/nmap_scan.py <authorized-target>")
        raise SystemExit(2)
    if not shutil.which("nmap"):
        print("nmap is not installed. Install it with your OS package manager.")
        raise SystemExit(1)
    target=sys.argv[1].strip()
    if not target or target.startswith("-"):
        print("Invalid target.")
        raise SystemExit(2)
    cmd=["nmap","-sV","--top-ports","100",target]
    print("Running:", " ".join(cmd))
    raise SystemExit(subprocess.call(cmd))

if __name__=="__main__":
    main()

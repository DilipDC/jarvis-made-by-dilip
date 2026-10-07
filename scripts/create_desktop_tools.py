"""Create JARVIS helper scripts on the user's Desktop."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DESKTOP=Path.home()/"Desktop"
if not DESKTOP.exists():
    DESKTOP=Path.home()/"desktop"
DESKTOP.mkdir(parents=True,exist_ok=True)

for name in ("happy.py","nmap_scan.py"):
    source=ROOT/"scripts"/name
    destination=DESKTOP/name
    destination.write_text(source.read_text(encoding="utf-8"),encoding="utf-8")
    print(destination)

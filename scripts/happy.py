"""JARVIS local smoke-test script."""
from datetime import datetime
import platform

def main():
    print("Happy from JARVIS!")
    print("Python:", platform.python_version())
    print("OS:", platform.system(), platform.release())
    print("Time:", datetime.now().isoformat(timespec="seconds"))

if __name__ == "__main__":
    main()

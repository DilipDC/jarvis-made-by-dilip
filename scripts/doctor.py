from __future__ import annotations
import importlib.util, os, platform, shutil, sys
def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'WARN'}] {name}: {detail}")
def main():
    print("JARVIS DOCTOR")
    print("="*60)
    check("Python", sys.version_info >= (3,10), platform.python_version())
    check("OS", platform.system() in {"Windows","Linux"}, platform.platform())
    check("FastAPI", importlib.util.find_spec("fastapi") is not None)
    check("PyAutoGUI", importlib.util.find_spec("pyautogui") is not None, "desktop control")
    check("mss", importlib.util.find_spec("mss") is not None, "screen capture fallback")
    check("xdotool", shutil.which("xdotool") is not None, "Linux input fallback")
    check("Playwright", importlib.util.find_spec("playwright") is not None, "headless browser")
    check("MCP", importlib.util.find_spec("mcp") is not None, "MCP SDK")
    check("AirLLM", importlib.util.find_spec("airllm") is not None, "local inference")
    check("PyTorch", importlib.util.find_spec("torch") is not None, "AirLLM dependency")
    check("npx", shutil.which("npx") is not None, "MCP stdio servers")
    check("Ollama", shutil.which("ollama") is not None or bool(os.getenv("OLLAMA_URL")), "fallback backend")
    check("Open Interpreter", shutil.which("interpreter") is not None, "Linux computer/coding agent bridge")
    try:
        import torch
        print(f"[INFO] torch={torch.__version__} cuda={torch.cuda.is_available()}")
    except Exception as exc: print(f"[WARN] torch import failed: {exc}")
    print("="*60)
    print("A WARN means an optional capability is unavailable; core JARVIS can still start.")
if __name__=="__main__": main()

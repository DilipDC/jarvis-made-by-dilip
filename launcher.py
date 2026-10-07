from __future__ import annotations
import os,threading,time,webbrowser

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from jarvis_app.core.app import app
    import uvicorn
    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:8000")),
        daemon=True,
    ).start()
    uvicorn.run(app,host="127.0.0.1",port=8000,log_level="info")

if __name__=="__main__":
    main()

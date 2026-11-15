"""
Convenience Launcher for AutoPrice AI (MyDash Analytics Platform).
Runs the modern FastAPI application with interactive MyDash frontend,
or optionally the Streamlit dashboard via '--streamlit'.
"""

import sys
import os
import time
import webbrowser
import uvicorn

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # Check for optional Streamlit flag
    if "--streamlit" in sys.argv:
        import subprocess
        app_path = os.path.join(root_dir, 'app', 'main.py')
        print(f"Launching Streamlit version from: {app_path}")
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port=8501", "--server.headless=false", "--browser.gatherUsageStats=false"
        ]
        subprocess.run(cmd)
        return

    port = 8501
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print("=" * 64)
    print("   🚗 AutoPrice AI | MyDash Intelligence Platform")
    print("=" * 64)
    print(f"   ► Dashboard URL : {url}")
    print(f"   ► Interactive UI: Top Navigation, Real-time Valuation, Q1 BI")
    print(f"   ► API Docs      : {url}/docs")
    print(f"   ► Theme Style   : MyDash Charcoal Dark (#151B1D)")
    print("=" * 64)
    print("   Press Ctrl+C to stop the server.\n")

    # Open browser automatically in a background timer
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch Uvicorn
    uvicorn.run("app.server:app", host=host, port=port, log_level="info", reload=False)

if __name__ == '__main__':
    main()

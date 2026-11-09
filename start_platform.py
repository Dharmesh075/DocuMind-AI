"""
DocuMind AI - Local Platform Launcher
Launches FastAPI backend (port 8000) and Next.js frontend (port 3000) concurrently.
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

def main():
    print("=" * 65)
    print("  DocuMind AI: Intelligent Document Processing Platform")
    print("  Apple Liquid Glass UI + FastAPI + Scikit-Learn + Layout Engine")
    print("=" * 65)

    # 1. Start FastAPI Backend
    print("\n[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = str(BACKEND_DIR)
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=str(BACKEND_DIR),
        env=backend_env
    )

    time.sleep(2)

    # 2. Start Next.js Frontend
    print("[2/2] Launching Next.js Liquid Glass Frontend on http://localhost:3000 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR)
    )

    print("\n" + "=" * 65)
    print("  Platform running!")
    print("  -> Frontend UI:      http://localhost:3000")
    print("  -> Backend API:      http://127.0.0.1:8000")
    print("  -> API Docs (OpenAPI): http://127.0.0.1:8000/docs")
    print("  Press Ctrl+C to terminate both servers.")
    print("=" * 65 + "\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping DocuMind AI platform servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Servers stopped cleanly.")

if __name__ == "__main__":
    main()

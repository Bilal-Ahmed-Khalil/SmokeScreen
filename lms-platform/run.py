import subprocess
import time
import os
import sys
import webbrowser

BASE_DIR = "/home/kali/Desktop/FYP/lms-platform"
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
VENV_PYTHON = os.path.join(BACKEND_DIR, "venv/bin/python")

def main():
    print("--- LMS PLATFORM MASTER STARTUP ---")
    
    # 1. Start MongoDB
    subprocess.run(["sudo", "systemctl", "start", "mongodb"], check=True)
    print("✅ MongoDB Started.")

    # 2. Start Backend
    backend_proc = subprocess.Popen([VENV_PYTHON, "run.py"], cwd=BACKEND_DIR)
    
    # 3. Start Frontend
    frontend_proc = subprocess.Popen(["python3", "-m", "http.server", "8000"], cwd=FRONTEND_DIR)
    
    time.sleep(2)
    print("🚀 ALL SYSTEMS ONLINE")
    print("Opening browser to http://localhost:8000/index.html")
    
    # Automatically open the correct page
    webbrowser.open("http://localhost:8000/index.html")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend_proc.terminate()
        frontend_proc.terminate()
        print("\n👋 Systems Offline.")

if __name__ == "__main__":
    main()

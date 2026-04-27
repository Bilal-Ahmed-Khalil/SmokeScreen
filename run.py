import subprocess
import os
import time
import sys

# --- CONFIGURATION ---
BASE_DIR = "/root/lms-platform"
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# --- PATHS (System Global) ---
VENV_PYTHON = "/usr/bin/python3"
OTEL_INSTRUMENT = "/usr/local/bin/opentelemetry-instrument"
OTLP_ENDPOINT = "http://localhost:4317"

def start_services():
    print("🛡️  LMS HONEYPOT ACTIVATION SEQUENCE  🛡️")
    print("-" * 40)

    # 1. Prepare Environment Variables
    env = os.environ.copy()
    env["OTEL_EXPORTER_OTLP_ENDPOINT"] = OTLP_ENDPOINT
    env["OTEL_SERVICE_NAME"] = "lms-honeypot-decoy"
    
    # 2. Start Backend
    print(f"📡 Starting Honey-Backend on Port 8001...")
    backend_cmd = [
        OTEL_INSTRUMENT,
        "--traces_exporter", "otlp",
        "--metrics_exporter", "none",
        VENV_PYTHON, "run.py"
    ]
    
    backend_proc = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR, env=env)

    # 3. Start Frontend
    print(f"💻 Starting LMS Decoy UI on Port 8000...")
    frontend_proc = subprocess.Popen(
        ["python3", "-m", "http.server", "8000"], 
        cwd=FRONTEND_DIR
    )

    print("-" * 40)
    print("🚀 ALL SYSTEMS ONLINE")
    print(f"Logs: {BASE_DIR}/logs/honeypot_interactions.json")
    print("Telemetry: Streaming to SigNoz on port 4317")
    print("Press CTRL+C to shutdown.")

    return backend_proc, frontend_proc

if __name__ == "__main__":
    if not os.path.exists(OTEL_INSTRUMENT):
        print(f"❌ ERROR: {OTEL_INSTRUMENT} not found.")
        sys.exit(1)

    b_proc, f_proc = start_services()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 SHUTTING DOWN HONEYPOT...")
        b_proc.terminate()
        f_proc.terminate()
        sys.exit(0)

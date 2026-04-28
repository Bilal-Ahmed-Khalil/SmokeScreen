import os
import subprocess
import sys
import time

# Import the instrumented app from the app package
try:
    from app import app
except ImportError as e:
    print(f"❌ Critical Error: Could not import 'app'. Ensure you are in the project root. {e}")
    sys.exit(1)

def start_decoy_ui():
    """Starts the static frontend on Port 8000 relative to the project root."""
    # Dynamically find the project root regardless of where run.py is called from
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    frontend_path = os.path.join(project_root, "frontend")
    
    if not os.path.exists(frontend_path):
        print(f"⚠️ Error: Frontend folder not found at {frontend_path}")
        return

    print(f"💻 Starting LMS Decoy UI on Port 8000...")
    # sys.executable ensures it uses the same Python (venv) as the backend
    subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=frontend_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    print("\n🛡️  LMS HONEYPOT ACTIVATION SEQUENCE  🛡️")
    print("----------------------------------------")
    
    # 1. Start the Static Decoy
    start_decoy_ui()
    time.sleep(1) # Small delay to let the port initialize

    # 2. Start the Instrumented Honey-Backend
    print("📡 Starting Honey-Backend on Port 8001...")
    print("🚀 ALL SYSTEMS ONLINE")
    print("Telemetry: Streaming to SigNoz at 192.168.23.140:4318")
    print("----------------------------------------\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8001, debug=False)

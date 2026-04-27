from flask import Flask, render_template, request, jsonify
import datetime
import json
import os

app = Flask(__name__, static_folder='static')

# --- CONFIGURATION ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
LOG_FILE = "logs.json"

# --- LOGGING UTILITIES ---

def write_logs_to_file(logs):
    """Saves the log list to a JSON file with pretty formatting."""
    with open(LOG_FILE, "w") as log_file:
        json.dump(logs, log_file, indent=4)

def read_logs_from_file():
    """Reads existing logs. Returns an empty list if file is missing or corrupt."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as log_file:
            try:
                return json.load(log_file)
            except json.JSONDecodeError:
                return [] 
    return []

def log_action(action, ip_address, port):
    """Core logging function: captures timestamp, event, and attacker source."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "ip_address": ip_address,
        "port": port
    }
    
    # Load, append, and save
    current_logs = read_logs_from_file()
    current_logs.append(log_entry)
    write_logs_to_file(current_logs)

# --- EVENT-SPECIFIC LOGGERS ---

def log_login_attempt(username, password, ip_address, port, status):
    """Wraps log_action specifically for authentication events."""
    action = f"Login attempt: {status} (User: {username})"
    log_action(action, ip_address, port)

def log_camera_action(action, ip_address, port):
    """Wraps log_action for UI interactions (e.g., toggling power)."""
    log_action(action, ip_address, port)

def log_directory_traversal(ip_address, port, url):
    """Wraps log_action for unauthorized URL path discovery attempts."""
    action = f"Directory traversal attempt to {url}"
    log_action(action, ip_address, port)

# --- ROUTES ---

@app.route("/", methods=["GET", "POST"])
def login():
    """Handles the fake Hikvision login portal and credential logging."""
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip_address = request.remote_addr
        port = request.environ.get("REMOTE_PORT")
        
        # Check credentials against hardcoded admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            status = "login successful"
            log_login_attempt(username, password, ip_address, port, status)
            
            # Show the camera feed upon successful "breach"
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('camera.html', current_time=current_time)
        else:
            status = "login failed"
            log_login_attempt(username, password, ip_address, port, status)
            message = "Incorrect credentials. Please try again."
            
    return render_template("login_hikvision.html", message=message)

@app.route("/camera-action", methods=["POST"])
def camera_action():
    """API endpoint for UI buttons (On/Off) - logs malicious interaction."""
    action = request.form.get("action")
    ip_address = request.remote_addr
    port = request.environ.get("REMOTE_PORT")
    
    log_camera_action(action, ip_address, port)
    return jsonify({"status": "success"})

@app.route("/<path:dummy>")
def handle_directory_traversal(dummy):
    """Catch-all route to log 'fuzzing' or directory scanning attempts."""
    ip_address = request.remote_addr
    port = request.environ.get("REMOTE_PORT")
    url = request.url
    
    log_directory_traversal(ip_address, port, url)
    return "Attempt logged! You are not allowed to visit here..", 403

# --- MAIN ---

if __name__ == "__main__":
    # debug=True allows for auto-reloading during development
    app.run(host='0.0.0.0', port=5000, debug=True)

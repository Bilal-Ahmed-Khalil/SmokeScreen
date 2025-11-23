from flask import Flask, render_template, request, jsonify
import datetime
import json
import os

app = Flask(__name__, static_folder='static')

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

LOG_FILE = "logs.json"

# Function to write logs in the proper format
def write_logs_to_file(logs):
    with open(LOG_FILE, "w") as log_file:
        json.dump(logs, log_file, indent=4)

# Function to read logs from the file
def read_logs_from_file():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as log_file:
            try:
                return json.load(log_file)
            except json.JSONDecodeError:
                return []  # If JSON is corrupted, return an empty list
    else:
        return []

# Function to log general actions (e.g., login success, camera action)
def log_action(action, ip_address, port):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "ip_address": ip_address,
        "port": port
    }
    logs = read_logs_from_file()
    logs.append(log_entry)
    write_logs_to_file(logs)

# Function to log login attempts
def log_login_attempt(username, password, ip_address, port, status):
    action = f"Login attempt: {status}"
    log_action(action, ip_address, port)

# Function to log camera actions
def log_camera_action(action, ip_address, port):
    log_action(action, ip_address, port)

# Function to log directory traversal attempts
def log_directory_traversal(ip_address, port, url):
    action = f"Directory traversal attempt to {url}"
    log_action(action, ip_address, port)

# Route for login page
@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip_address = request.remote_addr
        port = request.environ.get("REMOTE_PORT")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            status = "login successful"
            log_login_attempt(username, password, ip_address, port, status)
            return render_template('camera.html', current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            status = "login failed"
            log_login_attempt(username, password, ip_address, port, status)
            message = "Incorrect credentials. Please try again."
    return render_template("login_hikvision.html", message=message)

# Route for camera action (example: turning on or off)
@app.route("/camera-action", methods=["POST"])
def camera_action():
    action = request.form.get("action")
    ip_address = request.remote_addr
    port = request.environ.get("REMOTE_PORT")
    log_camera_action(action, ip_address, port)
    # Perform action here (e.g., turn the camera on or off)
    return jsonify({"status": "success"})

# Route to handle directory traversal attempts
@app.route("/<path:dummy>")
def handle_directory_traversal(dummy):
    ip_address = request.remote_addr
    port = request.environ.get("REMOTE_PORT")
    url = request.url
    log_directory_traversal(ip_address, port, url)
    return "Attempt logged! You are not allowed to visit here.."

if __name__ == "__main__":
    app.run(debug=True)

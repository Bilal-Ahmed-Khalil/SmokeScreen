from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this to a high-entropy string in production

# --- CONFIGURATION & DATA ---
# Simulated user credentials (replace with a database/hashed passwords in production)
USER_CREDENTIALS = {
    "admin": "password123"
}

# Data structure defining decoys categorized by interaction level
# Each decoy maps to a Proxmox VMID for container management
decoys = {
    "low": [
        {
            "id": "Camera", 
            "status": "deactivated", 
            "vmid": 1002, 
            "ip": "http://192.168.23.131:5000", 
            "details": "Camera mimic IoT camera behavior"
        },
    ],
    "medium": [
        {
            "id": "FireAlarm", 
            "status": "deactivated", 
            "vmid": 1012, 
            "ip": "http://192.168.23.132:5000", 
            "details": "FireAlarm mimic real fire alarm system"
        },
    ],
    "high": [
        {
            "id": "LMS", 
            "status": "deactivated", 
            "vmid": 3001, 
            "ip": "http://192.168.23.133:8000", 
            "details": "LMS System of High Interaction. Mimic Normal LMS behavior"
        },
    ],
}

# --- AUTHENTICATION ROUTES ---

@app.route("/", methods=["GET", "POST"])
def login():
    """Handles admin authentication for SmokeScreen."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
            
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Clears the session and redirects to login."""
    session.pop("user", None)
    return redirect(url_for("login"))

# --- CORE DASHBOARD ROUTES ---

@app.route("/dashboard")
def dashboard():
    """Main landing page after login."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/view_logs")
def view_logs():
    """Aggregated log view for all decoys."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("view_logs.html")

@app.route("/<level>")
def honeypot_page(level):
    """Dynamically routes to Low, Medium, or High interaction pages."""
    if "user" not in session:
        return redirect(url_for("login"))
    
    if level in decoys:
        return render_template(f"{level}.html", decoys=decoys[level])
    return "Page not found", 404

# --- API ENDPOINTS (JSON) ---

@app.route("/toggle_decoy", methods=["POST"])
def toggle_decoy():
    """
    Triggers a subprocess call to virtual_machine.py to start/stop
    the Proxmox container associated with the decoy ID.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    level = data.get("level")
    id = data.get("id")
    action = data.get("action") # Expected "on" or "off"
    
    # Locate the decoy in our data dictionary
    for decoy in decoys.get(level, []):
        if decoy["id"] == id:
            # Update internal state status
            decoy["status"] = "Activated" if action == "on" else "Deactivated"
            vmid = decoy["vmid"]
            
            # Execute external script to interface with the hypervisor
            subprocess.run(["python", "virtual_machine.py", action, str(vmid)])
            
            return jsonify({"message": f"Decoy {id} is now {decoy['status']}."})
    
    return jsonify({"error": "Invalid decoy information"}), 400

@app.route("/get_decoy_details/<level>/<id>", methods=["GET"])
def get_decoy_details(level, id):
    """Returns metadata and mock logs for a specific decoy."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized access."}), 401
    
    for decoy in decoys.get(level, []):
        if decoy["id"] == id:
            details = {
                "id": decoy["id"],
                "status": decoy["status"],
                "vmid": decoy["vmid"],
                "ip": decoy["ip"],
                "details": decoy["details"],
                "logs": [
                    f"Log entry 1 for VMID {decoy['vmid']}",
                    f"Log entry 2 for VMID {decoy['vmid']}",
                ],
            }
            return jsonify(details)

    return jsonify({"error": "Decoy not found"}), 404

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    # Running on 0.0.0.0 to make the SmokeScreen UI accessible over the network
    app.run(host='0.0.0.0', port=5000)

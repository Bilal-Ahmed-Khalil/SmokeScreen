from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Simulated user credentials (replace with a database in production)
USER_CREDENTIALS = {
    "admin": "password123"
}
# Simulated decoy statuses with hardcoded VMIDs for each decoy
decoys = {
    "low": [
        {"id": "Camera", "status": "deactivated", "vmid": 1002, "ip": "http://192.168.23.131:5000", "details": "details"},
      #  {"id": "Printer", "status": "deactivated", "vmid": 104, "ip": "http://192.168.95.141:5000", "details": "details"},
       # {"id": "Email-SMTP (Telnet)", "status": "deactivated", "vmid": 105, "ip": "http://192.168.95.144:5000", "details": "The Email Honeypot is a deception tool that simulates an SMTP server to attract and log malicious email activity, such as spam or phishing attempts. It listens for incoming email connections, records details like the sender, recipient, and email content, and stores them in a JSON log file. To interact, attackers can connect using a command like:telnet <honeypot_ip> 2525 \n HELO attacker.com \n MAIL FROM:<attacker@example.com> \n RCPT TO:<victim@example.com> \n DATA Subject: Test Message This is a test message. \n  . \n QUIT"},
	#{"id": "SSHield", "status": "deactivated", "vmid": 106, "ip": "http://192.168.95.146:5000", "details": "details"},
	#{"id": "Router", "status": "deactivated", "vmid": 107, "ip": "http://192.168.95.147:5000", "details": "details"},    
],
    "medium": [
        {"id": "FireAlarm -192.168.23.132", "status": "deactivated", "vmid": 1012},
     #  {"id": "Defense - CT#102-192.168.95.138", "status": "deactivated", "vmid": 102},
	#{"id": "PARKING", "status": "deactivated", "vmid": 108},
	#{"id": "Student LMS", "status": "deactivated", "vmid": 109},
	#{"id": "Fake Endpoints", "status": "deactivated", "vmid": 110},
    ],
    "high": [
      #  {"id": "StudentPortal", "status": "deactivated", "vmid": 301},
    ],
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/view_logs")
def view_logs():
    return render_template("view_logs.html")

@app.route("/<level>")
def honeypot_page(level):
    if "user" not in session:
        return redirect(url_for("login"))
    if level in decoys:
        return render_template(f"{level}.html", decoys=decoys[level])
    return "Page not found", 404

@app.route("/toggle_decoy", methods=["POST"])
def toggle_decoy():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    level, id, action = data.get("level"), data.get("id"), data.get("action")
    
    # Find the VMID based on the decoy's level and id
    for decoy in decoys.get(level, []):
        if decoy["id"] == id:
            decoy["status"] = "Activated" if action == "on" else "Deactivated"
            vmid = decoy["vmid"]  # Use the VMID here for the Proxmox container
            # Call virtual_machine.py with the VMID to start/stop the container
            subprocess.run(["python", "virtual_machine.py", action, str(vmid)])
            return jsonify({"message": f"Decoy {id} is now {decoy['status']}."})
    
    return jsonify({"error": "Invalid decoy information"}), 400

@app.route("/get_decoy_details/<level>/<id>", methods=["GET"])
def get_decoy_details(level, id):
    if "user" not in session:
        return jsonify({"error": "Unauthorized access. Please log in first."}), 401
    
    # Locate the decoy
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

    # If decoy not found
    return jsonify({"error": "Decoy not found"}), 404


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



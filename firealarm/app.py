from flask import Flask, render_template, request, jsonify
import sqlite3
import smtplib
from email.mime.text import MIMEText
import json
import os
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    try:
        conn = sqlite3.connect('logs/interactions.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           action TEXT NOT NULL,
                           ip_address TEXT NOT NULL,
                           port INTEGER NOT NULL,
                           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

init_db()

# JSON Log setup
def log_interaction(action):
    # Collect log details
    log_entry = {
        'action': action,
        'ip_address': request.remote_addr,
        'port': request.environ.get('REMOTE_PORT'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Log to database
    try:
        conn = sqlite3.connect('logs/interactions.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (action, ip_address, port) VALUES (?, ?, ?)",
                       (log_entry['action'], log_entry['ip_address'], log_entry['port']))
        conn.commit()
        conn.close()
        print(f"Logged to database: {log_entry}")
    except Exception as e:
        print(f"Error logging to database: {e}")

    # Log to JSON file
    log_file_path = 'logs/activity_log.json'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    try:
        # Read existing logs if file exists
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as log_file:
                logs = json.load(log_file)
        else:
            logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write updated logs back to the file
        with open(log_file_path, 'w') as log_file:
            json.dump(logs, log_file, indent=4)

        print(f"Logged to JSON file: {log_entry}")
    except Exception as e:
        print(f"Error logging to JSON file: {e}")

def send_email(action):
    try:
        # Configure email settings
        sender = 'your_email@example.com'
        recipient = 'recipient@example.com'
        subject = 'Fire Alarm Notification'
        body = f'Action performed: {action}'

        msg = MIMEText(body)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        # Send the email
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender, 'your_password')
            server.sendmail(sender, recipient, msg.as_string())
        print(f"Email sent for action: {action}")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate_alarm():
    log_interaction('Alarm Activated')
    send_email('Alarm Activated')
    return jsonify(status="Alarm Activated")

@app.route('/reset', methods=['POST'])
def reset_alarm():
    log_interaction('Alarm Reset')
    send_email('Alarm Reset')
    return jsonify(status="Alarm Reset")

@app.route('/temperature', methods=['GET'])
def get_temperature():
    # Simulate getting temperature from a sensor
    temperature = "72°F"  # Replace with actual temperature reading logic
    return jsonify(temperature=temperature)

@app.route('/smoke', methods=['GET'])
def get_smoke_level():
    # Simulate getting smoke level from a sensor
    smoke_level = "Normal"  # Replace with actual smoke level reading logic
    return jsonify(smokeLevel=smoke_level)

@app.route('/countermeasures', methods=['POST'])
def initiate_countermeasures():
    log_interaction('Countermeasures Initiated')
    send_email('Countermeasures Initiated')
    return jsonify(status="Countermeasures Initiated")

@app.route('/call_fire_brigade', methods=['POST'])
def call_fire_brigade():
    log_interaction('Called Fire Brigade')
    send_email('Called Fire Brigade')
    return jsonify(status="Fire Brigade Called")

@app.route('/call_emergency', methods=['POST'])
def call_emergency_services():
    log_interaction('Called Emergency Services')
    send_email('Called Emergency Services')
    return jsonify(status="Emergency Services Called")

if __name__ == '__main__':
    app.run(debug=True)

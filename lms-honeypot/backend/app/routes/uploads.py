from flask import Blueprint, request, jsonify, send_from_directory
from app.utils import token_required
import os
import datetime
from opentelemetry import trace
import json

tracer = trace.get_tracer(__name__)
uploads_bp = Blueprint('uploads', __name__)

UPLOAD_FOLDER = "/root/lms-platform/uploads"
LOG_FILE = "/root/lms-platform/logs/honeypot_interactions.json"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_log(event_type, payload):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event": event_type,
        "src_ip": request.remote_addr,
        "payload": payload
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

@uploads_bp.route('/', methods=['POST'])
@token_required
def upload_file(current_user):
    with tracer.start_as_current_span("honeypot_file_upload") as span:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        # Honeypot: Rename file to include uploader email to track who sent malware
        filename = f"{current_user['email']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(filepath)

        # Log the upload event
        save_log("file_upload", {"user": current_user['email'], "filename": filename, "original_name": file.filename})
        span.set_attribute("file.name", filename)
        
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 201

@uploads_bp.route('/<filename>', methods=['GET'])
def download_file(filename):
    # Log who is downloading what
    save_log("file_download", {"filename": filename})
    return send_from_directory(UPLOAD_FOLDER, filename)

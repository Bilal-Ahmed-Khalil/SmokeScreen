import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.utils import token_required
from extensions import mongo
import datetime

uploads_bp = Blueprint('uploads', __name__)

# 1. Upload logic (Works for Teacher Materials OR Student Assignments)
@uploads_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    course_id = request.form.get('course_id')
    week_num = request.form.get('week_number')
    upload_type = request.form.get('type') # 'material' or 'submission'
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(f"{upload_type}_{course_id}_wk{week_num}_{file.filename}")
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    if upload_type == 'submission':
        mongo.db.submissions.insert_one({
            "course_id": course_id,
            "week_number": week_num,
            "student_email": current_user['email'],
            "filename": filename,
            "timestamp": datetime.datetime.utcnow()
        })
    
    return jsonify({"message": "File uploaded successfully", "filename": filename}), 201

# 2. Download logic
@uploads_bp.route('/download/<filename>', methods=['GET'])
@token_required
def download_file(current_user, filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# 3. Teacher view: List of student submissions
@uploads_bp.route('/submissions/<course_id>', methods=['GET'])
@token_required
def get_submissions(current_user, course_id):
    if current_user['role'] != 'teacher':
        return jsonify({"message": "Unauthorized"}), 403
    subs = list(mongo.db.submissions.find({"course_id": course_id}))
    for s in subs: s['_id'] = str(s['_id'])
    return jsonify(subs), 200

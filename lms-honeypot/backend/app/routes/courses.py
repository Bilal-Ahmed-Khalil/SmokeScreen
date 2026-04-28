from flask import Blueprint, request, jsonify
from app import mongo
from bson import ObjectId
from datetime import datetime
from opentelemetry import trace # For SigNoz Traces

courses_bp = Blueprint('courses', __name__)
tracer = trace.get_tracer(__name__) # Initialize OTEL Tracer

# --- 1. GET ALL COURSES ---
@courses_bp.route('/', methods=['GET'])
def get_courses():
    """Fetches all courses for the dashboard."""
    courses = list(mongo.db.courses.find())
    for course in courses:
        course['_id'] = str(course['_id'])
    return jsonify(courses), 200

# --- 2. CREATE NEW COURSE (Honeypot Interaction) ---
@courses_bp.route('/', methods=['POST'])
def create_course():
    """Logs course creation as a trace event for SigNoz."""
    with tracer.start_as_current_span("course_creation") as span:
        data = request.json
        title = data.get('title')
        description = data.get('description', '')

        # Set SigNoz attributes
        span.set_attribute("honeypot.event", "create_course")
        span.set_attribute("course.title", title)
        span.set_attribute("attacker.ip", request.remote_addr)

        new_course = {
            "title": title,
            "description": description,
            "teacher": "Admin",
            "modules": [],
            "created_at": datetime.utcnow()
        }

        result = mongo.db.courses.insert_one(new_course)
        return jsonify({
            "message": "Course created successfully",
            "course_id": str(result.inserted_id)
        }), 201

# --- 3. GET SINGLE COURSE DETAILS ---
@courses_bp.route('/<course_id>', methods=['GET'])
def get_single_course(course_id):
    """Fetches details and modules for a specific course."""
    try:
        course = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
        if course:
            course['_id'] = str(course['_id'])
            return jsonify(course), 200
        return jsonify({"message": "Course not found"}), 404
    except Exception:
        return jsonify({"message": "Invalid Course ID"}), 400

# --- 4. ADD MODULE (High-Interaction Trap) ---
@courses_bp.route('/modules/<course_id>', methods=['POST'])
def add_module(course_id):
    """Tracks module content additions in SigNoz."""
    with tracer.start_as_current_span("module_addition") as span:
        data = request.json
        title = data.get('title')
        content = data.get('content')

        span.set_attribute("honeypot.event", "add_module")
        span.set_attribute("module.title", title)
        span.set_attribute("course.id", course_id)

        mongo.db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$push": {"modules": {
                "title": title,
                "content": content,
                "timestamp": datetime.utcnow()
            }}}
        )
        return jsonify({"message": "Module added"}), 201

# --- 5. FILE UPLOAD TRAP (Critical Honeypot Feature) ---
@courses_bp.route('/upload/<course_id>', methods=['POST'])
def upload_file(course_id):
    """Captures malicious file metadata and alerts SigNoz."""
    with tracer.start_as_current_span("file_upload_attempt") as span:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        
        file = request.files['file']
        
        # Log metadata to SigNoz for analysis
        span.set_attribute("honeypot.event", "file_upload")
        span.set_attribute("file.name", file.filename)
        span.set_attribute("file.content_type", file.content_type)
        span.set_attribute("attacker.ip", request.remote_addr)

        # In a real honeypot, you might save the file to a secure 'quarantine' folder
        print(f"⚠️ HONEYPOT ALERT: File {file.filename} uploaded by {request.remote_addr}")
        
        return jsonify({"message": "File uploaded successfully (Pending Review)"}), 200

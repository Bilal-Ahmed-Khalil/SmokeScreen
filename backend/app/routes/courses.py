from flask import Blueprint, request, jsonify
from app import mongo  # FIX: Import directly from app package
from app.routes.auth import token_required # FIX: Import from auth.py where it is defined
from bson.objectid import ObjectId

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
@token_required
def get_courses(current_user):
    courses = list(mongo.db.courses.find())
    for c in courses: 
        c['_id'] = str(c['_id'])
    return jsonify(courses), 200

@courses_bp.route('/<id>', methods=['GET'])
@token_required
def get_course(current_user, id):
    try:
        course = mongo.db.courses.find_one({"_id": ObjectId(id)})
        if not course:
            return jsonify({"msg": "Course not found"}), 404
        course['_id'] = str(course['_id'])
        return jsonify(course), 200
    except:
        return jsonify({"msg": "Invalid Course ID"}), 400

@courses_bp.route('/', methods=['POST'])
@token_required
def create_course(current_user):
    # Allowed both 'teacher' and 'admin' to create courses for easier testing
    if current_user['role'] not in ['teacher', 'admin']: 
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    new_id = mongo.db.courses.insert_one({
        "title": data.get('title'),
        "description": data.get('description'),
        "instructor": current_user['email'],
        "weeks": [] 
    }).inserted_id
    
    return jsonify({"id": str(new_id)}), 201

@courses_bp.route('/<id>/week', methods=['POST'])
@token_required
def add_week(current_user, id):
    if current_user['role'] not in ['teacher', 'admin']:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    mongo.db.courses.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"weeks": data}}
    )
    return jsonify({"msg": "Week added"}), 200

import jwt
import datetime
import logging  # Added for Fail2Ban
from flask import Blueprint, request, jsonify, current_app
from app import mongo, bcrypt
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# --- CONFIG LOGGING ---
# This creates the file Fail2Ban will read
logging.basicConfig(
    filename='/home/kali/Desktop/FYP/lms-platform/backend/access.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# --- HELPER: Token Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"email": data['sub']})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- ROUTES ---

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    mongo.db.users.insert_one({
        "email": email,
        "password": hashed_pw,
        "role": role,
        "created_at": datetime.datetime.utcnow()
    })
    return jsonify({"message": "User registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    # Capture the IP address of the person trying to log in
    client_ip = request.remote_addr 

    user = mongo.db.users.find_one({"email": email})

    if user and bcrypt.check_password_hash(user['password'], password):
        token = jwt.encode({
            'sub': user['email'],
            'role': user.get('role', 'student'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "token": token,
            "role": user.get('role'),
            "message": "Login successful"
        }), 200

    # LOG THE FAILURE: This is what Fail2Ban uses to detect an attack
    logging.info(f"LOGIN_FAILED from IP: {client_ip} for user: {email}")
    
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "email": current_user['email'], 
        "role": current_user['role']
    }), 200

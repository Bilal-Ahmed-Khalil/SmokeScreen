import os
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from app import mongo, bcrypt

# --- FIXED OPENTELEMETRY SETUP ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Initialize Tracer with explicit Service Name
resource = Resource(attributes={
    "service.name": "lms-honeypot"
})
provider = TracerProvider(resource=resource)

# Direct OTLP/HTTP Export to your Kali machine
otlp_exporter = OTLPSpanExporter(endpoint="http://192.168.23.140:4318/v1/traces")
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

auth_bp = Blueprint('auth', __name__)

# --- UTILS: HONEYPOT LOCAL LOGGING ---
def log_interaction(event_type, data):
    """Local JSON backup for attacker activity."""
    log_path = "/root/lms-platform/logs/honeypot_interactions.json"
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "ip": request.remote_addr,
        "details": data
    }
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# --- JWT DECORATOR ---
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
            # SECRET_KEY is loaded from app/__init__.py
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"email": data['sub']})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# --- ROUTES ---

@auth_bp.route('/register', methods=['POST'])
def register():
    """Honeypot registration: Records intent of new users."""
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
        "created_at": datetime.utcnow()
    })
    return jsonify({"message": "User registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Primary Trap: Captures credentials and streams to SigNoz."""
    with tracer.start_as_current_span("login_attempt") as span:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Telemetry Attributes for SigNoz Dashboard
        span.set_attribute("attacker.ip", request.remote_addr)
        span.set_attribute("attacker.email", email)

        user = mongo.db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user['password'], password):
            # Generate JWT on Success
            token = jwt.encode({
                'sub': user['email'],
                'role': user.get('role', 'student'),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            span.set_attribute("login.status", "success")
            log_interaction("login_success", {"user": email})

            return jsonify({
                "token": token,
                "role": user.get('role'),
                "message": "Login successful"
            }), 200

        # FAILURE TRAP: Catch and export the password to SigNoz
        span.set_attribute("login.status", "failed")
        span.set_attribute("attacker.password", password)
        
        log_interaction("login_failed", {
            "email": email, 
            "password_tried": password
        })
        
        return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({"email": current_user['email'], "role": current_user['role']}), 200

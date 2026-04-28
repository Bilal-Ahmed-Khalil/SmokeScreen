import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# OpenTelemetry Global Instrumentors
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # --- 1. CONFIGURATION ---
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/lms_honeypot"
    app.config["SECRET_KEY"] = "LMS_HONEYPOT_SUPER_SECRET_KEY_2026_STAY_SAFE"
    
    # --- 2. SECURITY & EXTENSIONS ---
    # Allow Port 8000 (Frontend) to talk to Port 8001 (Backend)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    mongo.init_app(app)
    bcrypt.init_app(app)

    # --- 3. GLOBAL LOGGING (SIGNOZ) ---
    # This instruments EVERY Flask request (even 404s and 500s)
    FlaskInstrumentor().instrument_app(app)
    
    # This instruments EVERY MongoDB query (find, insert, update)
    PymongoInstrumentor().instrument()

    # --- 4. BLUEPRINT REGISTRATION ---
    # Importing inside the function prevents circular import errors
    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')

    return app

# Create the app instance for run.py
app = create_app()

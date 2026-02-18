import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize Extensions
mongo = PyMongo()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURATION ---
    # Connect to local MongoDB
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/lms_honeypot"
    app.config["SECRET_KEY"] = "LMS_SECRET_KEY_STANDARD"
    
    # --- SECURITY ---
    # Allow CORS so Frontend (8000) can talk to Backend (8001)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    mongo.init_app(app)
    bcrypt.init_app(app)

    # --- BLUEPRINTS ---
    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')

    return app

app = create_app()

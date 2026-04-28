import os

class Config:
    # Key must be at least 32 characters for HS256 security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lms_production_secure_key_32_chars_long_minimum')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/lms_db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit

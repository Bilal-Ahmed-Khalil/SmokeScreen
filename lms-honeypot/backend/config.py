import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/lms_db')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    JWT_ALGORITHM = 'HS256'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Upload Limit1~

from flask import Flask
from config import Config
from extensions import mongo, bcrypt, cors
from app.routes.auth import auth_bp
from app.routes.courses import courses_bp
from app.routes.uploads import uploads_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)  # <--- This prevents the 'Blocked by CORS' error

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(uploads_bp, url_prefix='/uploads')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8001, debug=False)

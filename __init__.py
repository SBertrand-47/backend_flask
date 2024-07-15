from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)

    with app.app_context():
        from .routes import app as routes_blueprint
        app.register_blueprint(routes_blueprint)

        db.create_all()  # Create database tables for our data models

    return app

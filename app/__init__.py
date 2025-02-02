from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(database_url=None):
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

    # Configure the Flask application
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Ensure PostgreSQL compatibility
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

    # General SQLAlchemy settings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models
        from app.models.models import Platform, Category
        
        # Create all database tables
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
            raise
        
        # Initialize default data
        try:
            Platform.insert_default_platforms()
            Category.insert_default_categories()
            app.logger.info("Default platforms and categories initialized successfully")
        except Exception as e:
            app.logger.error(f"Error initializing default data: {str(e)}")

    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
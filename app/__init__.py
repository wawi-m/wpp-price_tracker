from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

class Config:
    """Configuration class to handle environment variables."""
    
    # Fetch DATABASE_URL from environment variable
    DATABASE_URL = os.getenv('DATABASE_URL')

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required.")
   
    # Build the SQLAlchemy URI dynamically from environment variables
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Disable track modifications to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'

def create_app():
    app = Flask(__name__)
    
    # Configure the Flask application
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
            raise

    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api')
    def api_docs():
        return {
            "message": "Welcome to Price Tracker API",
            "version": "1.0",
            "endpoints": {
                "products": "/api/v1/products",
                "product_detail": "/api/v1/products/<id>",
                "search": "/api/v1/products/search",
                "price_history": "/api/v1/products/<id>/prices",
                "price_visualization": "/api/v1/products/<id>/visualization",
                "price_visualization_data": "/api/v1/products/<id>/visualization/data",
                "categories": "/api/v1/categories",
                "platforms": "/api/v1/platforms",
                "stats": "/api/v1/stats"
            }
        }

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
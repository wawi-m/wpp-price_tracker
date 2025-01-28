from flask import Flask, render_template
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

    # Configure the SQLAlchemy database URI
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Ensure PostgreSQL compatibility
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

    # General SQLAlchemy settings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

    # Initialize database and migration extension
    db.init_app(app)
    migrate.init_app(app, db)

    # Create database tables if not already created (used during app initialization)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
            raise

    # Register the API Blueprint (routes for the API are in app/api/routes.py)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Define the homepage route
    @app.route('/')
    def index():
        return render_template('index.html')

    # API documentation route
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

# Ensures that app runs only when executed directly
if __name__ == '__main__':
    app = create_app()  # Create the app with the database URL
    app.run(debug=True)  # Start the app in debug mode

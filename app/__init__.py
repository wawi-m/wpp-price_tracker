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

def create_app():
    app = Flask(__name__)
    
    # Configure the Flask application
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    
    # Build database URL from environment variables
    db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

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

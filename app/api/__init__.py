from flask import Blueprint

# Initialize the API Blueprint
bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import routes to associate them with the 'api' Blueprint
from app.api import routes

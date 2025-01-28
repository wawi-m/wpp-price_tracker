from flask import Blueprint

# Initialize the API Blueprint
bp = Blueprint('api', __name__)

# Import routes to associate them with the 'api' Blueprint
from app.api import routes

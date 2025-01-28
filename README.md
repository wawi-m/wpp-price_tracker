# wpp-price_tracker

# Setup and Installation

## Prerequisites
- Python 3.12
- Docker (for PostgreSQL only)
- Conda (recommended for environment management)

## Development Setup

1. Create and activate conda environment:
```bash
conda create --name e-analytics python=3.12
conda init bash
conda activate e-analytics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Database Setup:
```bash
# Start PostgreSQL container
docker-compose up -d

# The database will be available at:
# - Host: localhost
# - Port: 5432
# - Database: price_tracker
# - Username: postgres
# - Password: password
```

4. Run the application:
```bash
python run.py
```

5. Access the application:
- Web Interface: http://localhost:5000
- API Documentation: http://localhost:5000/api

## Project Structure

wpp-price_tracker/ ├── .env ├── Connecting ├── Procfile ├── README.md ├── pycache/ ├── app/ │ ├── init.py │ ├── pycache/ │ ├── api/ │ ├── models/ │ ├── routes.py │ ├── scrapers/ │ ├── static/ │ └── templates/ ├── buildpack.toml ├── migrations/ │ ├── README │ ├── pycache/ │ ├── alembic.ini │ ├── env.py │ ├── script.py.mako │ └── versions/ ├── requirements.txt └── run.py


## API Endpoints

### Products
- GET `/api/v1/products` - List all products
- GET `/api/v1/products/<id>` - Get product details
- GET `/api/v1/products/search` - Search products

### Price History
- GET `/api/v1/products/<id>/prices` - Get price history
- GET `/api/v1/products/<id>/visualization` - Price history visualization
- GET `/api/v1/products/<id>/visualization/data` - Raw visualization data

### Categories and Platforms
- GET `/api/v1/categories` - List all categories
- GET `/api/v1/platforms` - List all platforms
- GET `/api/v1/stats` - Get platform statistics

## Development Notes

### Database Connection
- Development: Uses localhost connection through `.env` configuration
- Docker: Uses internal Docker network with `db` service name
- Production: Will use Heroku PostgreSQL (to be configured)

### Scraping Schedule
- Scrapers run daily to update prices
- Manual update available through API endpoint
- Rate limiting implemented to respect website policies

### Frontend Features
- Real-time price comparison
- Historical price trends visualization
- Product search and filtering
- Mobile-responsive design
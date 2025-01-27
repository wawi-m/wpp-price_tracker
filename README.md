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

wpp-price_tracker/
├── .dockerignore
├── .env
├── .git/
├── .gitignore
├── docker-compose.yaml
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── models/
│   │   └── models.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── jumia_phones.py
│   │   ├── jumia_tvs.py
│   │   ├── kilimall_phones.py
│   │   ├── kilimall_tvs.py
│   │   └── run_scrapers.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── templates/
├── media/
├── migrations/
│   ├── versions/
│   └── alembic.ini
    ├── env.py
    ├── README
    └── script.py.mako
├── run.py
├── README.md

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
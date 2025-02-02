import logging
from flask import Blueprint, render_template, jsonify, request, abort
from app import db
from app.models.models import Product, Platform, Category
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__, 
              template_folder='templates',
              static_folder='static',
              static_url_path='/static')

# Frontend Routes
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/compare')
def compare():
    return render_template('compare.html')

@bp.route('/price-history')
def price_history():
    return render_template('price_history.html')

# API Routes
@bp.route('/api/v1/products')
def get_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12
        query = Product.query.order_by(Product.updated_at.desc())
        
        # Apply filters
        search = request.args.get('search')
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
            
        category_id = request.args.get('category_id')
        if category_id and category_id != 'all':
            query = query.filter_by(category_id=category_id)
            
        platform_id = request.args.get('platform_id')
        if platform_id and platform_id != 'all':
            query = query.filter_by(platform_id=platform_id)
        
        # Log query information
        logger.info(f"Fetching products with filters - Search: {search}, Category: {category_id}, Platform: {platform_id}")
        
        # Execute query with pagination
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        if not products.items:
            logger.warning("No products found for the given filters")
        
        return jsonify({
            'items': [{
                'id': p.id,
                'name': p.name,
                'url': p.url,
                'image_url': p.image_url,
                'platform': p.platform.name,
                'current_price': p.current_price,
                'currency': p.currency,
                'last_update': p.last_price_update.isoformat() if p.last_price_update else None
            } for p in products.items],
            'page': products.page,
            'total_pages': products.pages,
            'has_next': products.has_next
        })
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/v1/products/<int:id>')
def get_product(id):
    try:
        product = Product.query.options(joinedload(Product.platform)).get(id)
        
        if not product:
            abort(404, description="Product not found")

        return jsonify({
            'id': product.id,
            'name': product.name,
            'url': product.url,
            'image_url': product.image_url,
            'platform': product.platform.name,
            'current_price': product.current_price,
            'currency': product.currency,
            'price_history': product.price_history or [],
            'last_update': product.last_price_update.isoformat() if product.last_price_update else None
        })
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/v1/categories')
def get_categories():
    try:
        categories = Category.query.all()
        logger.info(f"Fetched {len(categories)} categories")
        return jsonify([{
            'id': c.id,
            'name': c.name
        } for c in categories])
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/v1/platforms')
def get_platforms():
    try:
        platforms = Platform.query.all()
        logger.info(f"Fetched {len(platforms)} platforms")
        return jsonify([{
            'id': p.id,
            'name': p.name
        } for p in platforms])
    except Exception as e:
        logger.error(f"Error fetching platforms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/v1/stats')
def get_stats():
    try:
        # Get platform-specific stats
        platform_stats = db.session.query(
            Platform.name,
            func.count(Product.id).label('total_products'),
            func.count(Product.price_history).label('total_prices')
        ).join(Product, isouter=True).group_by(Platform.name).all()
        
        # Calculate price changes in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        price_changes = db.session.query(
            func.sum(case((Product.current_price < Product.price_history[-1]['price'], 1), else_=0)).label('drops'),
            func.sum(case((Product.current_price > Product.price_history[-1]['price'], 1), else_=0)).label('increases')
        ).filter(Product.last_price_update >= yesterday).first()

        # Initialize stats with default values
        stats = {
            'total_products': Product.query.count(),
            'price_drops': price_changes.drops if price_changes and price_changes.drops else 0,
            'price_increases': price_changes.increases if price_changes and price_changes.increases else 0,
            'jumia_products': 0,
            'jumia_prices': 0,
            'kilimall_products': 0,
            'kilimall_prices': 0
        }

        # Add platform-specific stats
        for platform in platform_stats:
            stats[f'{platform.name.lower()}_products'] = platform.total_products or 0
            stats[f'{platform.name.lower()}_prices'] = platform.total_prices or 0

        logger.info(f"Stats generated successfully: {stats}")
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/v1/test-stats')
def test_stats():
    """Test endpoint to verify stats calculation"""
    try:
        # Get raw counts
        product_count = Product.query.count()
        platform_counts = {p.name: p.products.count() for p in Platform.query.all()}
        
        return jsonify({
            'total_products': product_count,
            'platform_counts': platform_counts,
            'message': 'This is a test endpoint to verify stats calculation'
        })
    except Exception as e:
        logger.error(f"Error in test-stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

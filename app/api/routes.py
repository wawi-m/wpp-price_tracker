from flask import jsonify, request, abort
from app.api import bp
from app.models.models import Product, Platform, Category
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload

@bp.route('/products')
def get_products():
    """Get paginated list of products"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    query = Product.query.order_by(Product.updated_at.desc())
    
    # Apply filters
    search = request.args.get('search')
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
        
    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    platform_id = request.args.get('platform_id')
    if platform_id:
        query = query.filter_by(platform_id=platform_id)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
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
        } for p in pagination.items],
        'page': pagination.page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next
    })

@bp.route('/products/<int:id>')
def get_product(id):
    """Get product details by ID"""
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

@bp.route('/categories')
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name
    } for c in categories])

@bp.route('/platforms')
def get_platforms():
    """Get all platforms"""
    platforms = Platform.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name
    } for p in platforms])

@bp.route('/stats')
def get_stats():
    """Get platform stats and price changes"""
    # Get platform-specific stats
    platform_stats = db.session.query(
        Platform.name,
        func.count(Product.id).label('total_products'),
        func.count(Product.price_history).label('total_prices')
    ).join(Product).group_by(Platform.name).all()
    
    # Calculate price changes in the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    price_changes = db.session.query(
        func.sum(case((Product.current_price < Product.price_history[-1]['price'], 1), else_=0)).label('drops'),
        func.sum(case((Product.current_price > Product.price_history[-1]['price'], 1), else_=0)).label('increases')
    ).filter(Product.last_price_update >= yesterday).first()

    stats = {
        'total_products': Product.query.count(),
        'price_drops': price_changes.drops if price_changes.drops else 0,
        'price_increases': price_changes.increases if price_changes.increases else 0
    }

    # Add platform-specific stats
    for platform in platform_stats:
        stats[f'{platform.name.lower()}_products'] = platform.total_products
        stats[f'{platform.name.lower()}_prices'] = platform.total_prices

    return jsonify(stats)
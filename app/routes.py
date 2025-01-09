from flask import render_template, jsonify, request
from app import app, db
from app.models.models import Product, Platform, Category, Price
from sqlalchemy import func
from datetime import datetime, timedelta

# Frontend Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/price-history')
def price_history():
    return render_template('price_history.html')

# API Routes
@app.route('/api/v1/products')
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    query = Product.query
    
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
    products = [{
        'id': p.id,
        'name': p.name,
        'url': p.url,
        'image_url': p.image_url,
        'platform': p.platform.name,
        'current_price': p.prices[-1].price if p.prices else None
    } for p in pagination.items]
    
    return jsonify({
        'items': products,
        'page': pagination.page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next
    })

@app.route('/api/v1/products/<int:id>')
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'url': product.url,
        'image_url': product.image_url,
        'platform': product.platform.name,
        'prices': [{
            'price': price.price,
            'timestamp': price.timestamp.isoformat()
        } for price in product.prices]
    })

@app.route('/api/v1/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name
    } for c in categories])

@app.route('/api/v1/platforms')
def get_platforms():
    platforms = Platform.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name
    } for p in platforms])

@app.route('/api/v1/stats')
def get_stats():
    total_products = Product.query.count()
    total_platforms = Platform.query.count()
    total_price_points = Price.query.count()
    
    return jsonify({
        'total_products': total_products,
        'total_platforms': total_platforms,
        'total_price_points': total_price_points
    })

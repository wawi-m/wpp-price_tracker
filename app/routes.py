from flask import Blueprint, render_template, jsonify, request, abort
from app import db
from app.models.models import Product, Platform, Category
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

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
        'current_price': p.current_price,
        'currency': p.currency,
        'last_update': p.last_price_update.isoformat() if p.last_price_update else None
    } for p in pagination.items]
    
    return jsonify({
        'items': products,
        'page': pagination.page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next
    })

@bp.route('/api/v1/products/<int:id>')
def get_product(id):
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

@bp.route('/api/v1/categories')
def get_categories():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = Category.query

    pagination = query.paginate(page=page, per_page=per_page)
    categories = [{
        'id': c.id,
        'name': c.name
    } for c in pagination.items]

    return jsonify({
        'items': categories,
        'page': pagination.page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next
    })

@bp.route('/api/v1/platforms')
def get_platforms():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = Platform.query

    pagination = query.paginate(page=page, per_page=per_page)
    platforms = [{
        'id': p.id,
        'name': p.name,
        'url': p.url
    } for p in pagination.items]

    return jsonify({
        'items': platforms,
        'page': pagination.page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next
    })

@bp.route('/api/v1/stats')
def get_stats():
    total_products = Product.query.count()
    total_platforms = Platform.query.count()
    total_categories = Category.query.count()
    
    return jsonify({
        'total_products': total_products,
        'total_platforms': total_platforms,
        'total_categories': total_categories
    })

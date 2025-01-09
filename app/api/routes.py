from flask import jsonify, request
from app.api import bp
from app.models.models import Product, Platform, Category
from app import db
import pandas as pd
import plotly.express as px
import json
from datetime import datetime, timedelta

@bp.route('/products')
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [{
            'id': p.id,
            'name': p.name,
            'url': p.url,
            'image_url': p.image_url,
            'platform': p.platform.name,
            'category': p.category.name,
            'current_price': p.formatted_price
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@bp.route('/products/<int:id>')
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'url': product.url,
        'image_url': product.image_url,
        'description': product.description,
        'platform': product.platform.name,
        'category': product.category.name,
        'current_price': product.formatted_price,
        'price_history': product.price_history
    })

@bp.route('/products/search')
def search_products():
    query = request.args.get('q', '')
    category = request.args.get('category')
    platform = request.args.get('platform')
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(Product.name.ilike(f'%{query}%'))
    if category:
        products_query = products_query.join(Category).filter(Category.name == category)
    if platform:
        products_query = products_query.join(Platform).filter(Platform.name == platform)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    products = products_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [{
            'id': p.id,
            'name': p.name,
            'url': p.url,
            'image_url': p.image_url,
            'platform': p.platform.name,
            'category': p.category.name,
            'current_price': p.formatted_price
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@bp.route('/products/<int:id>/prices')
def get_price_history(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.price_history)

@bp.route('/products/<int:id>/visualization')
def price_visualization(id):
    product = Product.query.get_or_404(id)
    
    if not product.price_history:
        return jsonify({'error': 'No price history available'})
    
    df = pd.DataFrame(product.price_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.line(df, x='timestamp', y='price', title=f'Price History for {product.name}')
    return json.dumps(fig.to_dict())

@bp.route('/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'product_count': len(c.products)
    } for c in categories])

@bp.route('/platforms')
def get_platforms():
    platforms = Platform.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'url': p.url,
        'product_count': len(p.products)
    } for p in platforms])

@bp.route('/stats')
def get_stats():
    # Calculate platform stats
    platforms = Platform.query.all()
    platform_stats = {}
    
    for platform in platforms:
        products = platform.products
        platform_stats[platform.name.lower()] = {
            'total_products': len(products),
            'name': platform.name,
            'url': platform.url
        }
    
    # Calculate price changes in the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    products = Product.query.filter(Product.last_price_update >= yesterday).all()
    
    price_changes = {'increases': 0, 'decreases': 0}
    for product in products:
        if product.price_history and len(product.price_history) > 1:
            current_price = product.current_price
            previous_price = product.price_history[-2]['price']
            
            if current_price > previous_price:
                price_changes['increases'] += 1
            elif current_price < previous_price:
                price_changes['decreases'] += 1
    
    return jsonify({
        'total_products': Product.query.count(),
        'platforms': len(platforms),
        'categories': Category.query.count(),
        'platform_stats': platform_stats,
        'price_increases': price_changes['increases'],
        'price_decreases': price_changes['decreases']
    })

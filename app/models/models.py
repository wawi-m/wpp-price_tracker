from datetime import datetime
from app import db

class Platform(db.Model):
    __tablename__ = 'platform'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    products = db.relationship('Product', backref='platform', lazy=True)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), unique=True, nullable=False)
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    last_price_update = db.Column(db.DateTime, default=datetime.utcnow)
    price_history = db.Column(db.JSON, default=list)  # Store price history as JSON array
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def formatted_price(self):
        return f"{self.currency} {self.current_price:,.2f}"

    def update_price(self, new_price):
        """Update product price and maintain history"""
        if not self.price_history:
            self.price_history = []
            
        # Add current price to history
        if self.current_price is not None:
            self.price_history.append({
                'price': self.current_price,
                'timestamp': self.last_price_update.isoformat()
            })
            
        # Update current price
        self.current_price = new_price
        self.last_price_update = datetime()

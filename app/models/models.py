from datetime import datetime
from app import db

class Platform(db.Model):
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    products = db.relationship('Product', backref='platform', lazy=True)

    @staticmethod
    def insert_default_platforms():
        default_platforms = [
            {'name': 'Jumia', 'url': 'https://www.jumia.co.ke'},
            {'name': 'Kilimall', 'url': 'https://www.kilimall.co.ke'}
        ]
        for platform_data in default_platforms:
            if not Platform.query.filter_by(name=platform_data['name']).first():
                platform = Platform(**platform_data)
                db.session.add(platform)
        db.session.commit()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

    @staticmethod
    def insert_default_categories():
        default_categories = ['Mobile Phones', 'Televisions']
        for category_name in default_categories:
            if not Category.query.filter_by(name=category_name).first():
                category = Category(name=category_name)
                db.session.add(category)
        db.session.commit()

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='KES')
    price_history = db.Column(db.JSON, default=list)
    last_price_update = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def to_dict(self):
        """Convert product to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'image_url': self.image_url,
            'current_price': self.current_price,
            'currency': self.currency,
            'platform': self.platform.name if self.platform else None,
            'category': self.category.name if self.category else None,
            'last_update': self.last_price_update.isoformat() if self.last_price_update else None
        }
    
    def update_price(self, new_price):
        """Update product price and price history"""
        if new_price != self.current_price:
            # Add current price to history before updating
            history_entry = {
                'price': self.current_price,
                'timestamp': datetime.utcnow().isoformat()
            }
            if not self.price_history:
                self.price_history = []
            self.price_history.append(history_entry)
            
            # Update current price
            self.current_price = new_price
            self.last_price_update = datetime.utcnow()

    @property
    def formatted_price(self):
        return f"{self.currency} {self.current_price:,.2f}"

    @property
    def discount(self):
        """Calculate discount if both price and old_price exist"""
        if self.price_history:
            old_price = self.price_history[-1]['price']
            if old_price > self.current_price:
                return round(((old_price - self.current_price) / old_price) * 100, 2)
        return 0.0
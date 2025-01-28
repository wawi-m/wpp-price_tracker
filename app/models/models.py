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
    name = db.Column(db.String(200), nullable=False)  # Increased to 200
    url = db.Column(db.String(500), unique=True, nullable=False)
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    last_price_update = db.Column(db.DateTime, default=datetime.utcnow)
    price_history = db.Column(db.JSON, default=list)  # Store price history as JSON array
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
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
        self.last_price_update = datetime.utcnow()

    @property
    def discount(self):
        """Calculate discount if both price and old_price exist"""
        if self.price_history:
            old_price = self.price_history[-1]['price']
            if old_price > self.current_price:
                return round(((old_price - self.current_price) / old_price) * 100, 2)
        return 0.0

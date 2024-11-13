from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.String(255), primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(255), primary_key=True)
    category_id = db.Column(db.String(255), db.ForeignKey('product_categories.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)  # To manage product availability

    category = db.relationship('ProductCategory', backref='products')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.category_name,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.uid'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # e.g., "Pending", "Completed", "Cancelled"

    user = db.relationship('User', backref='orders')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat(),
            'total_amount': self.total_amount,
            'status': self.status,
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.String(255), primary_key=True)
    order_id = db.Column(db.String(255), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(255), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref='order_items')
    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.uid'), nullable=False)
    order_id = db.Column(db.String(255), db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # e.g., "Success", "Failed", "Pending"
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='transactions')
    order = db.relationship('Order', backref='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'transaction_date': self.transaction_date.isoformat(),
        }

from . import db
from datetime import datetime

# User model
class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Category model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

# Supplier model
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_info": self.contact_info,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='active', nullable=False)

    category = db.relationship('Category', backref='products')
    supplier = db.relationship('Supplier', backref='products')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "purchase_price": float(self.purchase_price),
            "stock_quantity": self.stock_quantity,
            "image_url": self.image_url,
            "category_id": self.category_id,
             'category_name': self.category.name,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Order model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('Pending', 'Shipped', 'Delivered'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='orders')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.name,
            "total_amount": float(self.total_amount),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# OrderItem model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.uid', name='fk_orderitem_user_id'),
        nullable=False
    )
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "product_image": self.product.image_url,
            "quantity": self.quantity,
            "status": self.order.status,
            "supplier": self.product.supplier.name,
            "price": float(self.price),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

#Transaction model
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id', name='fk_transactions_order_id'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.uid', name='fk_transactions_user_id'),
        nullable=False
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    zipCode = db.Column(db.String(255), nullable=False)
    payment_status = db.Column(
        db.Enum('Pending', 'Paid', name='enum_payment_status'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = db.relationship('Order', backref='transaction')

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "zipCode": self.zipCode,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }




# Cart model
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='cart')
    product = db.relationship('Product', backref='cart_items')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

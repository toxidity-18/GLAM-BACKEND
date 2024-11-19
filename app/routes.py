from flask import Blueprint, request, jsonify
from datetime import timedelta
from . import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .model import User, Category, Product, Order, OrderItem, Transaction, Supplier
from sqlalchemy.exc import IntegrityError
import random
import string

main_bp = Blueprint('main', __name__)

# Utility function to generate UID
def generate_uid():
    return ''.join(random.choices(string.digits, k=6))  # Random 6-digit UID

# Login route
@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.uid, expires_delta=timedelta(days=2))
        return jsonify({"isAdmin": user.is_admin, "access_token": access_token, "data": user.to_dict()}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Get all users
@main_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Get a single user by ID
@main_bp.route('/users/<string:uid>', methods=['GET'])
@jwt_required()
def get_user(uid):
    user = User.query.get_or_404(uid)
    return jsonify(user.to_dict())

# Create a new user
@main_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        uid=generate_uid(),
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        password_hash=hashed_password,
        is_admin= False
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": True, "message": "User created successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False, "error": "Email already exists"}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": False, "error": "An internal server error occurred"}), 500

# Update an existing user
@main_bp.route('/users/<string:uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user.is_admin = data.get('is_admin', user.is_admin)
    db.session.commit()
    return jsonify(user.to_dict())

# Delete a user
@main_bp.route('/users/<string:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

# Get admin summary
@main_bp.route('/admin/summary', methods=['GET'])
@jwt_required()
def admin_summary():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"message": "Access forbidden"}), 403

    total_products = Product.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_profits = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0

    summary = {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_profits": round(total_profits, 2)
    }
    return jsonify(summary), 200

# Category routes
@main_bp.route('/product_categories', methods=['GET'])
# @jwt_required()
def get_product_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])

@main_bp.route('/product_categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_product_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict())

@main_bp.route('/product_categories', methods=['POST'])
# @jwt_required()
def create_product_category():
    data = request.get_json()
    new_category = Category(
        id=generate_uid(),
        name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

@main_bp.route('/product_categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_product_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data.get('name', category.name)
    db.session.commit()
    return jsonify(category.to_dict())

@main_bp.route('/product_categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_product_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Product category deleted successfully"}), 200

# Product routes
@main_bp.route('/products', methods=['GET'])
# @jwt_required()
def get_products():
    category_id = request.args.get('category_id')
    status = request.args.get('status')

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)

    products = query.all()
    return jsonify([product.to_dict() for product in products]), 200

@main_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@main_bp.route('/products', methods=['POST'])
# @jwt_required()
def create_product():
    data = request.get_json()

    # Input Validation
    if not data.get('name') or not data.get('price') or not data.get('category_id') or not data.get('supplier_id'):
        return jsonify({"error": "Missing required fields"}), 400

    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        image_url=data.get('image_url'),
        purchase_price=data.get('purchase_price', 0.0),
        stock_quantity=data.get('stock_quantity', 0),
        status=data.get('status', 'active'),
        category_id=data['category_id'],
        supplier_id=data['supplier_id']
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify(new_product.to_dict()), 201


@main_bp.route('/products/<int:product_id>', methods=['PUT'])
# @jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()


    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.image_url = data.get('image_url', product.image_url)
    product.purchase_price = data.get('purchase_price', product.purchase_price)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    product.status = data.get('status', product.status)
    product.category_id = data.get('category_id', product.category_id)
    product.supplier_id = data.get('supplier_id', product.supplier_id)

    db.session.commit()
    return jsonify(product.to_dict()), 200


@main_bp.route('/products/<int:product_id>', methods=['DELETE'])
# @jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


# Order routes
@main_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user_id).all()
    return jsonify([order.to_dict() for order in orders])

@main_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@main_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    new_order = Order(
        id=generate_uid(),
        user_id=current_user_id,
        total_amount=data['total'],
        status=data.get('Status', 'Pending')
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify(new_order.to_dict()), 201

@main_bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    order.status = data.get('status', order.status)
    db.session.commit()
    return jsonify(order.to_dict())

@main_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"}), 200

# OrderItem routes
@main_bp.route('/order_items', methods=['GET'])
@jwt_required()
def get_order_items():
    current_user_id = get_jwt_identity()
    items = OrderItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])

@main_bp.route('/order_items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_order_item(item_id):
    item = OrderItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@main_bp.route('/order_items', methods=['POST'])
@jwt_required()
def create_order_item():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    new_item = OrderItem(
        id=generate_uid(),
        user_id=current_user_id,
        order_id=data['order_id'],
        product_id=data['product_id'],
        quantity=data['quantity'],
        price=data['price']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@main_bp.route('/order_items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_order_item(item_id):
    item = OrderItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Order item deleted successfully"}), 200

@main_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()

    transactions = Transaction.query.filter_by(user_id=current_user_id).all()

    return jsonify([txn.to_dict() for txn in transactions])

@main_bp.route('/transactions/<int:txn_id>', methods=['GET'])
# @jwt_required()
def get_transaction(txn_id):
    transaction = Transaction.query.get_or_404(txn_id)
    return jsonify(transaction.to_dict())

@main_bp.route('/transactions/<int:txn_id>', methods=['PUT'])
# @jwt_required()
def update_transaction(txn_id):
    # Fetch the transaction
    transaction = Transaction.query.get_or_404(txn_id)
    data = request.get_json()

    # Update transaction fields
    # transaction.amount = data.get('amount', transaction.amount)
    transaction.payment_status = data.get('payment_status', transaction.payment_status)

    # Check if payment_status is updated to "Paid" and update the related order
    if transaction.payment_status == 'Paid':
        order = Order.query.get(transaction.order_id)
        if order:
            order.status = 'Shipped'  # or "Delivered," depending on your business logic

    db.session.commit()

    return jsonify(transaction.to_dict())


@main_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    data = request.get_json()
    current_user = get_jwt_identity()

    # Validate required fields
    if not all(key in data for key in ('order_id', 'amount', 'payment_status')):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if the order exists
    order = Order.query.get(data['order_id'])
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # Create a new transaction
    new_transaction = Transaction(
        id=generate_uid(),
        user_id=current_user,
        order_id=data['order_id'],
        name=data['full_name'], 
        email=data['email'], 
        phone=data['phone'], 
        address=data['address'], 
        city=data['city'], 
        zipCode=data['zipCode'], 
        amount=data['amount'],  
        payment_status=data['payment_status']
    )

    db.session.add(new_transaction)
    db.session.commit()

    return jsonify(new_transaction.to_dict()), 201


# Request password reset
@main_bp.route('/users/reset_password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        # Logic to send a password reset email
        return jsonify({"message": "Password reset instructions sent"}), 200
    return jsonify({"message": "User not found"}), 404

# Change user role
@main_bp.route('/users/<string:uid>/role', methods=['PUT'])
@jwt_required()
def change_user_role(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json()
    user.is_admin = data.get('is_admin', user.is_admin)
    db.session.commit()
    return jsonify(user.to_dict())

# Get all orders for a specific user
@main_bp.route('/users/<string:uid>/orders', methods=['GET'])
@jwt_required()
def get_user_orders(uid):
    orders = Order.query.filter_by(user_id=uid).all()
    return jsonify([order.to_dict() for order in orders])


# Get all orders (Admin only)
@main_bp.route('/admin/orders', methods=['GET'])
@jwt_required()
def get_all_orders_admin():
    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)
    if not user.is_admin:
        return jsonify({"message": "Unauthorized"}), 403
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])


# Get all transactions for a specific user
@main_bp.route('/users/<string:uid>/transactions', methods=['GET'])
@jwt_required()
def get_user_transactions(uid):
    transactions = Transaction.query.join(Order).filter(Order.user_id == uid).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

# Get all transactions for a specific order
@main_bp.route('/orders/<int:order_id>/transactions', methods=['GET'])
@jwt_required()
def get_order_transactions(order_id):
    transactions = Transaction.query.filter_by(order_id=order_id).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

# Get all suppliers
@main_bp.route('/suppliers', methods=['GET'])
@jwt_required()  # Optional: If you need JWT authentication
def get_suppliers():
    suppliers = Supplier.query.all()  # Get all suppliers
    return jsonify([supplier.to_dict() for supplier in suppliers])

# Get a single supplier by ID
@main_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)  # Get supplier or 404 if not found
    return jsonify(supplier.to_dict())

# Create a new supplier
@main_bp.route('/suppliers', methods=['POST'])
# @jwt_required()
def create_supplier():
    data = request.get_json()  # Get the data from the request body
    new_supplier = Supplier(
        id=generate_uid(),
        name=data['name'],
        contact_info=data.get('contact_info', ''),
        address=data.get('address', '')
    )
    db.session.add(new_supplier)  # Add the supplier to the database
    db.session.commit()  # Commit the transaction to save the supplier
    return jsonify(new_supplier.to_dict()), 201  # Return the new supplier

# Update an existing supplier
@main_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
# @jwt_required()
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)  # Get supplier or 404 if not found
    data = request.get_json()  # Get the data from the request body
    supplier.name = data.get('name', supplier.name)
    supplier.contact_info = data.get('contact_info', supplier.contact_info)
    supplier.address = data.get('address', supplier.address)
    db.session.commit()  # Commit the changes
    return jsonify(supplier.to_dict())  # Return the updated supplier

# Delete a supplier
@main_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)  # Get supplier or 404 if not found
    db.session.delete(supplier)  # Delete the supplier
    db.session.commit()  # Commit the changes
    return jsonify({"message": "Supplier deleted successfully"}), 200

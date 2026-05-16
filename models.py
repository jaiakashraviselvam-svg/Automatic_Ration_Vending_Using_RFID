from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    max_members = db.Column(db.Integer, default=50)
    users = db.relationship('User', backref='shop', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="kg")
    max_limit = db.Column(db.Integer, default=5)
    image_url = db.Column(db.String(255), default="")
    slot_number = db.Column(db.Integer, unique=True) # 1 to 6 mapped to vending machine keys
    hex_color = db.Column(db.String(10), default="0x00e676") # e.g. 0xf9a825 for 3D model
    is_active = db.Column(db.Boolean, default=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    rfidCard = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    totalAmount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='PENDING') # PENDING, PAID, DISPENSED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    dispensed = db.Column(db.Boolean, default=False)

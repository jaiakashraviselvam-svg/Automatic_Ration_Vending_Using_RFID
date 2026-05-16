import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Shop, Product, Order

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/', methods=['GET', 'POST'])
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_admin=True).first()
        from werkzeug.security import check_password_hash
        from flask_login import login_user
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid Admin Username or Password.', 'error')
            
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    users_count = User.query.filter_by(is_admin=False).count()
    shops_count = Shop.query.count()
    products_count = Product.query.count()
    orders_count = Order.query.count()
    return render_template('admin/dashboard.html', users=users_count, shops=shops_count, products=products_count, orders=orders_count)

# --- Products ---

@admin_bp.route('/products')
@admin_required
def products():
    all_products = Product.query.all()
    return render_template('admin/products.html', products=all_products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price', 0))
        unit = request.form.get('unit', 'kg')
        max_limit = int(request.form.get('max_limit', 5))
        slot_number = int(request.form.get('slot_number'))
        hex_color = request.form.get('hex_color', '0x00e676')
        
        image = request.files.get('image')
        image_url = ""
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            image.save(os.path.join(upload_folder, filename))
            image_url = f'uploads/products/{filename}'
            
        p = Product(name=name, price=price, unit=unit, max_limit=max_limit, slot_number=slot_number, hex_color=hex_color, image_url=image_url)
        db.session.add(p)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', action="Add")

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('name')
        p.price = float(request.form.get('price', 0))
        p.unit = request.form.get('unit', 'kg')
        p.max_limit = int(request.form.get('max_limit', 5))
        p.slot_number = int(request.form.get('slot_number'))
        p.hex_color = request.form.get('hex_color', '0x00e676')
        
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            image.save(os.path.join(upload_folder, filename))
            p.image_url = f'uploads/products/{filename}'
            
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', action="Edit", product=p)

# --- Shops ---

@admin_bp.route('/shops')
@admin_required
def shops():
    all_shops = Shop.query.all()
    return render_template('admin/shops.html', shops=all_shops)

@admin_bp.route('/shops/add', methods=['GET', 'POST'])
@admin_required
def add_shop():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        max_members = int(request.form.get('max_members', 50))
        s = Shop(name=name, location=location, max_members=max_members)
        db.session.add(s)
        db.session.commit()
        flash('Shop added successfully!', 'success')
        return redirect(url_for('admin.shops'))
    return render_template('admin/shop_form.html')

# --- Users ---

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).all()
    shops = Shop.query.all()
    return render_template('admin/users.html', users=all_users, shops=shops)

@admin_bp.route('/users/assign', methods=['POST'])
@admin_required
def assign_user_shop():
    user_id = request.form.get('user_id')
    shop_id = request.form.get('shop_id')
    
    user = User.query.get(user_id)
    shop = Shop.query.get(shop_id)
    
    if user and shop:
        # Enforce 50 members limit
        current_members = User.query.filter_by(shop_id=shop.id).count()
        if current_members >= shop.max_members and user.shop_id != shop.id:
            flash(f'Cannot assign user! {shop.name} has reached its max member limit of {shop.max_members}.', 'error')
            return redirect(url_for('admin.users'))
            
        user.shop_id = shop.id
        db.session.commit()
        flash(f'User {user.username} assigned to {shop.name}.', 'success')
        
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/reset_orders/<int:user_id>', methods=['POST'])
@admin_required
def reset_user_orders(user_id):
    from models import Order
    user = User.query.get_or_404(user_id)
    stuck = Order.query.filter(
        Order.user_id == user.id,
        Order.status.in_(['PAID', 'PENDING'])
    ).all()
    count = len(stuck)
    for o in stuck:
        o.status = 'DISPENSED'
    db.session.commit()
    flash(f'Reset {count} stuck order(s) for {user.username}. They can now place a new order.', 'success')
    return redirect(url_for('admin.users'))

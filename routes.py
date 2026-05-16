from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Order, Product, OrderItem
from werkzeug.security import check_password_hash, generate_password_hash
import time
import razorpay

main = Blueprint('main', __name__)

rfid_scan_cache = {
    'uid': None,
    'timestamp': 0,
    'status': 'waiting'
}

# ── ENROLLMENT CACHE ──
# Temporarily holds the last scanned UID for the enrollment script
enrollment_cache = {'last_uid': None, 'active': False}

# --- Web Portal Routes ---

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        rfid_card = request.form.get('rfidCard')
        password = request.form.get('password')
        
        user = User.query.filter_by(rfidCard=rfid_card).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid RFID card or password. Please try again.', 'error')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    paid_order = Order.query.filter_by(user_id=current_user.id, status='PAID').first()
    products = Product.query.filter_by(is_active=True).order_by(Product.slot_number).all()
    
    # Calculate Remaining Quotas for the current month
    from datetime import datetime
    from sqlalchemy import func
    first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    quotas = {}
    for p in products:
        # Sum of this product taken/paid this month
        taken = db.session.query(func.sum(OrderItem.quantity)).join(Order).filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == p.id,
            Order.status.in_(['PAID', 'DISPENSED']),
            Order.created_at >= first_of_month
        ).scalar() or 0
        
        # If Akash, quota is infinite (set to a high number)
        if current_user.rfidCard == 'RFID001':
            quotas[p.id] = 99
        else:
            quotas[p.id] = max(0, p.max_limit - taken)

    return render_template('dashboard.html', user=current_user, paidOrder=paid_order, products=products, quotas=quotas)

@main.route('/order', methods=['POST'])
@login_required
def place_order():
    # ── INDIVIDUAL PRODUCT MONTHLY QUOTA CHECK ──
    if current_user.rfidCard != 'RFID001':
        from datetime import datetime
        first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all products bought this month
        bought_items = db.session.query(Product.id).join(OrderItem).join(Order).filter(
            Order.user_id == current_user.id,
            Order.status.in_(['PAID', 'DISPENSED']),
            Order.created_at >= first_of_month
        ).all()
        bought_product_ids = [item[0] for item in bought_items]

        # Check if any new item is already bought
        for key, value in request.form.items():
            if key.startswith('product_'):
                qty = int(value)
                if qty > 0:
                    pid = int(key.split('_')[1])
                    if pid in bought_product_ids:
                        p = Product.query.get(pid)
                        flash(f'You have already received your {p.name} quota for this month.', 'error')
                        return redirect(url_for('main.dashboard'))

    if Order.query.filter_by(user_id=current_user.id, status='PAID').first():
        flash('You have a paid order waiting at the vending machine. Please collect it first.', 'error')
        return redirect(url_for('main.dashboard'))
        
    products = Product.query.filter_by(is_active=True).all()
    total_amount = 0.0
    items_to_add = []
    
    for p in products:
        qty_str = request.form.get(f'product_{p.id}', '0')
        try:
            qty = int(qty_str)
        except ValueError:
            qty = 0
            
        if qty > 0:
            if qty > p.max_limit:
                flash(f'Quantity for {p.name} exceeds the maximum limit of {p.max_limit}.', 'error')
                return redirect(url_for('main.dashboard'))
            total_amount += (qty * p.price)
            items_to_add.append({'product_id': p.id, 'qty': qty})
            
    if not items_to_add:
        flash('Please select at least one item.', 'error')
        return redirect(url_for('main.dashboard'))
        
    order = Order(
        user_id=current_user.id,
        totalAmount=total_amount,
        status='PENDING'
    )
    db.session.add(order)
    db.session.flush() # get order.id
    
    for item_data in items_to_add:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['qty']
        )
        db.session.add(order_item)
        
    db.session.commit()
    
    session['pendingOrderId'] = order.id
    return redirect(url_for('main.payment'))

@main.route('/payment', methods=['GET'])
@login_required
def payment():
    order_id = session.get('pendingOrderId')
    if not order_id:
        return redirect(url_for('main.dashboard'))
        
    order = Order.query.get(order_id)
    if not order or order.status != 'PENDING':
        return redirect(url_for('main.dashboard'))
        
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    data = {
        "amount": int(order.totalAmount * 100),
        "currency": "INR",
        "receipt": f"order_rcptid_{order.id}",
        "notes": {
            "order_id": order.id,
            "user_id": current_user.id
        }
    }
    
    try:
        razorpay_order = client.order.create(data=data)
        razorpay_order_id = razorpay_order['id']
    except Exception as e:
        flash('Could not initiate payment. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))
        
    return render_template('payment.html', order=order, razorpay_order_id=razorpay_order_id, razorpay_key_id=current_app.config['RAZORPAY_KEY_ID'])

@main.route('/payment-verify', methods=['POST'])
@login_required
def payment_verify():
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')
    
    order_id = session.get('pendingOrderId')
    if not order_id:
        return redirect(url_for('main.dashboard'))
        
    order = Order.query.get(order_id)
    if not order or order.status != 'PENDING':
        return redirect(url_for('main.dashboard'))
        
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        order.status = 'PAID'
        db.session.commit()
        session.pop('pendingOrderId', None)
        return redirect(url_for('main.payment_success'))
    except razorpay.errors.SignatureVerificationError:
        flash('Payment verification failed. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/payment-success')
@login_required
def payment_success():
    order = Order.query.filter_by(user_id=current_user.id, status='PAID').first()
    return render_template('payment-success.html', order=order)

# --- Vending Machine Routes ---

@main.route('/vending')
@main.route('/vending/login')
def vending_login():
    rfid_scan_cache['uid'] = None
    rfid_scan_cache['status'] = 'waiting'
    return render_template('vending-login.html')

@main.route('/vending/machine')
def vending_machine():
    order_id = session.get('vendingOrderId')
    if not order_id:
        return redirect(url_for('main.vending_login'))
        
    order = Order.query.get(order_id)
    if not order:
        return redirect(url_for('main.vending_login'))
        
    products = Product.query.filter_by(is_active=True).order_by(Product.slot_number).all()
    return render_template('vending-machine.html', order=order, products=products)

@main.route('/vending/dispense/<int:slot_number>', methods=['POST'])
def dispense(slot_number):
    order_id = session.get('vendingOrderId')
    if not order_id:
        return redirect(url_for('main.vending_login'))
        
    order = Order.query.get(order_id)
    if not order:
        return redirect(url_for('main.vending_login'))
        
    for item in order.items:
        if item.product.slot_number == slot_number and item.quantity > 0:
            item.dispensed = True
            break
            
    db.session.commit()
    
    # Check if fully dispensed
    all_dispensed = True
    for item in order.items:
        if item.quantity > 0 and not item.dispensed:
            all_dispensed = False
            break
            
    if all_dispensed:
        order.status = 'DISPENSED'
        db.session.commit()
        # Clean up session but keep order ID for thank you message
        session['last_order_id'] = order.id
        session.pop('vendingOrderId', None)
        session.pop('vendingUserId', None)
        return redirect(url_for('main.vending_thankyou'))
        
    return redirect(url_for('main.vending_machine'))

@main.route('/vending/thank-you')
def vending_thankyou():
    return render_template('thank_you.html')

@main.route('/vending/thankyou')
def vending_thankyou():
    order_id = session.get('dispensedOrderId')
    order = None
    if order_id:
        order = Order.query.get(order_id)
        session.pop('dispensedOrderId', None)
    return render_template('thankyou.html', order=order)


# --- API Routes ---

@main.route('/api/rfid/scan', methods=['POST'])
def rfid_scan():
    data = request.get_json(force=True, silent=True) or {}
    uid = data.get('uid') or data.get('rfid')
    if not uid:
        return jsonify({'error': 'UID missing'}), 400
        
    # ── IF ENROLLING, CATCH THE UID ──
    if enrollment_cache['active']:
        enrollment_cache['last_uid'] = str(uid)
        return jsonify({'message': 'Scan captured for enrollment'}), 200
        
    # Check both Friendly ID (RFID001) and Physical UID (491472769346)
    from sqlalchemy import or_
    user = User.query.filter(or_(User.rfidCard == uid, User.physical_uid == uid)).first()
    
    if not user:
        rfid_scan_cache['uid'] = uid
        rfid_scan_cache['status'] = 'unauthorized'
        rfid_scan_cache['timestamp'] = time.time()
        return jsonify({'message': 'Unauthorized Access'}), 403
        
    paid_order = Order.query.filter_by(user_id=user.id, status='PAID').first()
    if not paid_order:
        rfid_scan_cache['uid'] = uid
        rfid_scan_cache['status'] = 'unauthorized' # Changed from no_paid_order to unauthorized
        rfid_scan_cache['timestamp'] = time.time()
        return jsonify({'message': 'Unauthorized Access'}), 403
        
    rfid_scan_cache['uid'] = uid
    rfid_scan_cache['status'] = 'success'
    rfid_scan_cache['user_id'] = user.id
    rfid_scan_cache['order_id'] = paid_order.id
    rfid_scan_cache['timestamp'] = time.time()
    return jsonify({'message': 'Authentication successful', 'user': user.username, 'order_id': paid_order.id}), 200

@main.route('/api/vending/status', methods=['GET'])
def vending_status():
    if time.time() - rfid_scan_cache['timestamp'] < 10:
        if rfid_scan_cache['status'] == 'success':
            session['vendingUserId'] = rfid_scan_cache['user_id']
            session['vendingOrderId'] = rfid_scan_cache['order_id']
            rfid_scan_cache['status'] = 'waiting'
            return jsonify({'status': 'success', 'redirect': url_for('main.vending_machine')})
        elif rfid_scan_cache['status'] == 'unauthorized':
            rfid_scan_cache['status'] = 'waiting'
            return jsonify({'status': 'error', 'message': 'Unauthorized Access. RFID not recognized.'})
        elif rfid_scan_cache['status'] == 'no_paid_order':
            rfid_scan_cache['status'] = 'waiting'
            return jsonify({'status': 'error', 'message': 'No paid order found. Please pay on the portal first.'})
    return jsonify({'status': 'waiting'})

@main.route('/api/enroll/start', methods=['POST'])
def enroll_start():
    enrollment_cache['active'] = True
    enrollment_cache['last_uid'] = None
    return jsonify({'status': 'listening'})

@main.route('/api/enroll/poll', methods=['GET'])
def enroll_poll():
    uid = enrollment_cache['last_uid']
    if uid:
        enrollment_cache['active'] = False # Stop listening
        enrollment_cache['last_uid'] = None
    return jsonify({'uid': uid})

@main.route('/api/enroll/stop', methods=['POST'])
def enroll_stop():
    enrollment_cache['active'] = False
    return jsonify({'status': 'stopped'})

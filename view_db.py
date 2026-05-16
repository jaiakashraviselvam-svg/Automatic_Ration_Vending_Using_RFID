from app import create_app
from models import db, User, Product, Order, OrderItem, Shop
from tabulate import tabulate

app = create_app()

def show_table(title, headers, data):
    print("\n" + "="*80)
    print(f" {title.center(78)} ")
    print("="*80)
    print(tabulate(data, headers=headers, tablefmt="grid"))

with app.app_context():
    # 1. USERS
    users = User.query.all()
    user_data = [[u.id, u.username, u.rfidCard, u.physical_uid or "None", "Active" if u.is_active else "Inactive"] for u in users]
    show_table("USER ACCOUNTS", ["ID", "Name", "RFID ID", "Physical UID", "Status"], user_data)

    # 2. PRODUCTS
    prods = Product.query.all()
    prod_data = [[p.id, p.name, f"₹{p.price}/{p.unit}", f"Slot {p.slot_number}", "Yes" if p.is_active else "No"] for p in prods]
    show_table("PRODUCT INVENTORY", ["ID", "Item Name", "Price/Unit", "Vending Slot", "Active"], prod_data)

    # 3. ORDERS
    orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    order_data = [[o.id, o.user.username, f"₹{o.totalAmount:.2f}", o.status, o.created_at.strftime('%Y-%m-%d %H:%M')] for o in orders]
    show_table("RECENT ORDERS (Last 10)", ["ID", "Customer", "Total", "Status", "Date"], order_data)

    # 4. ORDER ITEMS (linked to orders)
    items = OrderItem.query.order_by(OrderItem.id.desc()).limit(10).all()
    item_data = [[i.id, f"Order #{i.order_id}", i.product.name, f"{i.quantity} {i.product.unit}", "Dispensed" if i.dispensed else "Pending"] for i in items]
    show_table("INDIVIDUAL ITEMS IN ORDERS", ["ID", "Order Ref", "Product", "Qty", "Dispense Status"], item_data)

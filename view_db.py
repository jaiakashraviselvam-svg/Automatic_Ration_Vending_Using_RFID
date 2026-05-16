from app import create_app
from models import db, User, Product, Order, OrderItem

app = create_app()

def master_audit():
    with app.app_context():
        print("\n" + "█"*70)
        print(" FULL SYSTEM DATABASE AUDIT ".center(70, "█"))
        print("█"*70)

        # 1. USERS TABLE
        print("\n[ 👤 TABLE: USERS ]")
        print(f"{'ID':<3} | {'Username':<12} | {'RFID ID':<10} | {'Status':<8} | {'Physical UID'}")
        print("-" * 70)
        for u in User.query.all():
            status = "ACTIVE" if u.is_active else "INACTIVE"
            print(f"{u.id:<3} | {u.username:<12} | {u.rfidCard:<10} | {status:<8} | {u.physical_uid}")

        # 2. PRODUCTS TABLE
        print("\n[ 📦 TABLE: PRODUCTS ]")
        print(f"{'ID':<3} | {'Slot':<4} | {'Name':<12} | {'Limit':<6} | {'Price':<6} | {'Hex Color'}")
        print("-" * 70)
        for p in Product.query.all():
            # Note: We use max_limit as there is no 'stock' field in models.py
            print(f"{p.id:<3} | {p.slot_number:<4} | {p.name:<12} | {p.max_limit:<6} | ₹{p.price:<5} | {p.hex_color}")

        # 3. ORDERS TABLE
        print("\n[ 🛒 TABLE: ORDERS ]")
        print(f"{'ID':<3} | {'User ID':<8} | {'Total':<8} | {'Status':<10} | {'Date'}")
        print("-" * 70)
        for o in Order.query.all():
            print(f"{o.id:<3} | {o.user_id:<8} | ₹{o.totalAmount:<7} | {o.status:<10} | {o.created_at.strftime('%Y-%m-%d')}")

        # 4. ORDER_ITEMS TABLE
        print("\n[ 🔍 TABLE: ORDER_ITEMS (Detailed Logs) ]")
        print(f"{'ID':<3} | {'Order':<6} | {'Prod ID':<8} | {'Qty':<4} | {'Dispensed'}")
        print("-" * 70)
        for item in OrderItem.query.all():
            disp = "YES" if item.dispensed else "NO"
            print(f"{item.id:<3} | {item.order_id:<6} | {item.product_id:<8} | {item.quantity:<4} | {disp}")

        print("\n" + "█"*70)
        print(" END OF AUDIT ".center(70, "█"))
        print("█"*70 + "\n")

if __name__ == "__main__":
    master_audit()

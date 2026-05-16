"""
reset_user_orders.py — Reset stuck orders for a specific user
Usage:
    python reset_user_orders.py RFID001
    python reset_user_orders.py --all
"""
import sys
from app import create_app
from models import db, User, Order

app = create_app()

def reset_for_rfid(rfid):
    with app.app_context():
        user = User.query.filter_by(rfidCard=rfid).first()
        if not user:
            print(f"❌ No user found with RFID: {rfid}")
            return
        
        stuck = Order.query.filter(
            Order.user_id == user.id,
            Order.status.in_(['PAID', 'PENDING'])
        ).all()
        
        if not stuck:
            print(f"✅ {user.username} ({rfid}) has no stuck orders.")
            return
        
        for o in stuck:
            o.status = 'DISPENSED'
        db.session.commit()
        print(f"✅ Reset {len(stuck)} stuck order(s) for {user.username} ({rfid})")
        print(f"   They can now place a new order.")

def reset_all():
    with app.app_context():
        stuck = Order.query.filter(Order.status.in_(['PAID', 'PENDING'])).all()
        for o in stuck:
            o.status = 'DISPENSED'
        db.session.commit()
        print(f"✅ Reset {len(stuck)} stuck orders across all users.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reset_user_orders.py RFID001")
        print("       python reset_user_orders.py --all")
        sys.exit(1)
    
    arg = sys.argv[1]
    if arg == '--all':
        reset_all()
    else:
        reset_for_rfid(arg)

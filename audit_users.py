from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    print("\n--- DATABASE USER AUDIT ---")
    users = User.query.all()
    if not users:
        print("Empty database!")
    
    for u in users:
        print(f"User: {u.username}")
        print(f"  RFID ID: '{u.rfidCard}' (Length: {len(u.rfidCard)})")
        print(f"  Status: {'ACTIVE' if u.is_active else 'INACTIVE'}")
        print(f"  Physical UID: {u.physical_uid}")
        print("-" * 30)

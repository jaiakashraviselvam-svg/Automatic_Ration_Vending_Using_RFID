from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1. Activate RFID014 and change password
    user14 = User.query.filter_by(rfidCard='RFID014').first()
    if user14:
        user14.password = generate_password_hash('jai123')
        user14.is_active = True
        print(f"✅ User 'jai' (RFID014) is now ACTIVE with password: jai123")
    else:
        print("❌ Could not find user with RFID014")

    # 2. Disable RFID012
    user12 = User.query.filter_by(rfidCard='RFID012').first()
    if user12:
        user12.is_active = False
        print(f"🚫 User 'jai' (RFID012) has been DISABLED.")
    else:
        print("❌ Could not find user with RFID012")

    db.session.commit()
    print("\n[DB SYNC COMPLETE]")

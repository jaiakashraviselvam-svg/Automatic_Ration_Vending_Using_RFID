from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Find user by RFID Card ID
    user = User.query.filter_by(rfidCard='RFID014').first()
    
    if user:
        print(f"🔍 Found User: {user.username}")
        print(f"   RFID: {user.rfidCard}")
        print(f"   Active: {user.is_active}")
        
        # Reset password and ensure active
        user.password = generate_password_hash('jai123')
        user.is_active = True
        db.session.commit()
        
        print("\n✅ Password reset to: jai123")
        print("✅ Account forced to: ACTIVE")
        print("🚀 Try logging in with 'jai' and 'jai123' now.")
    else:
        print("❌ ERROR: No user found with RFID Card ID 'RFID014'.")
        print("   Current users in DB:")
        for u in User.query.all():
            print(f"   - {u.username} (RFID: {u.rfidCard})")

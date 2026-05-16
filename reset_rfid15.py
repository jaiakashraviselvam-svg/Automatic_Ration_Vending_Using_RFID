from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(rfidCard='RFID015').first()
    if user:
        # Set new password
        user.password = generate_password_hash('password123')
        user.is_active = True
        db.session.commit()
        print(f"✅ User '{user.username}' (RFID015) updated!")
        print(f"✅ Password reset to: password123")
    else:
        print("❌ No user found with RFID015")

from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='jai').first()
    if user:
        # Update details
        user.password = generate_password_hash('jai123')
        user.is_active = True
        db.session.commit()
        print(f"✅ User 'jai' updated successfully!")
        print(f"   Password set to: jai123")
        print(f"   Status set to: ACTIVE")
    else:
        print("❌ User 'jai' not found in the database.")

from app import create_app, db
from models import User, Shop, Product
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    
    print("Seeding default Shop...")
    shop = Shop(name="Main Govt Ration Shop", location="Chennai Central", max_members=50)
    db.session.add(shop)
    db.session.commit()

    print("Seeding Users...")
    users = [
        User(username="Admin", rfidCard="ADMIN", password=generate_password_hash("admin123"), phone="9999999999", address="Admin Office", is_admin=True),
        User(username="Akash", rfidCard="RFID001", password=generate_password_hash("akash123"), phone="9876543210", address="Chennai, TN", shop_id=shop.id),
        User(username="Priya", rfidCard="RFID002", password=generate_password_hash("priya123"), phone="9876543211", address="Bangalore, KA", shop_id=shop.id),
        User(username="Rahul", rfidCard="RFID003", password=generate_password_hash("rahul123"), phone="9876543212", address="Mumbai, MH", shop_id=shop.id),
        User(username="Sneha", rfidCard="RFID004", password=generate_password_hash("sneha123"), phone="9876543213", address="Delhi, NCR", shop_id=shop.id),
        User(username="Vikram", rfidCard="RFID005", password=generate_password_hash("vikram123"), phone="9876543214", address="Kochi, KL", shop_id=shop.id),
        User(username="Test User", rfidCard="7594938221", password=generate_password_hash("test"), phone="0000000000", address="Test City", shop_id=shop.id)
    ]
    for u in users:
        db.session.add(u)
        
    print("Seeding Products...")
    products = [
        Product(name="Rice", price=1.0, unit="kg", max_limit=5, slot_number=1, hex_color="0xf9a825"),
        Product(name="Wheat", price=3.0, unit="kg", max_limit=5, slot_number=2, hex_color="0x7cb342"),
        Product(name="Sugar", price=5.0, unit="kg", max_limit=5, slot_number=3, hex_color="0xec407a"),
        Product(name="Cooking Oil", price=40.0, unit="L", max_limit=2, slot_number=4, hex_color="0xffca28"),
        Product(name="Soap", price=10.0, unit="pc", max_limit=5, slot_number=5, hex_color="0x42a5f5"),
        Product(name="Detergent", price=20.0, unit="pc", max_limit=2, slot_number=6, hex_color="0xab47bc"),
    ]
    for p in products:
        db.session.add(p)
        
    db.session.commit()
    print("Database seeded successfully!")

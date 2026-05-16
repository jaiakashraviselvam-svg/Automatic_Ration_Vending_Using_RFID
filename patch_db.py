import sqlite3
import os

db_path = 'instance/ration_vending.db'
if not os.path.exists(db_path):
    print("Database not found at instance/ration_vending.db")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns_to_add = [
        ('pincode', 'TEXT'),
        ('state', 'TEXT DEFAULT "Tamil Nadu"'),
        ('country', 'TEXT DEFAULT "India"')
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists.")
            
    conn.commit()
    conn.close()
    print("Database patch complete!")

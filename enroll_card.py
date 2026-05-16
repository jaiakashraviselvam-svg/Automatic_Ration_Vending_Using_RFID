"""
enroll_card.py — RFID Card Enrollment Utility
Run this on the Raspberry Pi to read a card's UID and register it
to a user in the database.

Usage:
    python enroll_card.py

Requirements:
    pip install mfrc522 RPi.GPIO
"""

import sys
import os

# ── Try importing Pi-specific libraries ──
try:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    ON_PI = False
    print("[SIMULATOR MODE] RPi/MFRC522 not found. Running in simulation mode.")

# ── Add Flask app context ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User

app = create_app()


def read_card_uid():
    """Polls the local Flask server to catch the next scan from the Pi."""
    import requests
    import time
    
    server_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Start enrollment mode
        r_start = requests.post(f"{server_url}/api/enroll/start")
        if r_start.status_code != 200:
            print(f"❌ Server Error ({r_start.status_code}): {r_start.text}")
            return None
            
        print("\n📡 WAITING FOR SCAN...")
        print(">>> PLEASE TAP THE CARD ON THE PI SCANNER NOW <<<")
        
        # 2. Poll for the UID
        for i in range(30): # Timeout after 30 seconds
            resp = requests.get(f"{server_url}/api/enroll/poll")
            if resp.status_code == 200:
                data = resp.json()
                if data.get('uid'):
                    return data['uid']
            time.sleep(1)
            if i % 5 == 0: print(f"   (still waiting... {30-i}s left)")
            
        print("\n❌ Timeout: No card scanned in 30 seconds.")
        requests.post(f"{server_url}/api/enroll/stop")
        return None
    except Exception as e:
        print(f"❌ Error: Could not connect to Flask at {server_url}")
        print("   Make sure you have run 'python app.py' first!")
        return None


def list_users(session):
    """Print all users without an RFID card assigned."""
    print("\n── Users in database ──────────────────────")
    users = session.query(User).filter_by(is_admin=False).all()
    if not users:
        print("  No users found. Seed the database first.")
        return []
    for u in users:
        status = u.rfidCard if u.rfidCard else "⚠️  No card"
        print(f"  [{u.id}] {u.username:<20} | RFID: {status}")
    print("────────────────────────────────────────────")
    return users


def enroll():
    with app.app_context():
        print("\n╔══════════════════════════════════════════╗")
        print("║   RFID Card Enrollment — Ration System   ║")
        print("╚══════════════════════════════════════════╝")

        users = list_users(db.session)
        if not users:
            return

        # Select user by Friendly ID
        rfid_input = input("\nEnter RFID ID to enroll (e.g. RFID001): ").strip()
        user = User.query.filter_by(rfidCard=rfid_input).first()
        
        if not user or user.is_admin:
            print(f"❌ User with RFID ID '{rfid_input}' not found.")
            return

        print(f"\n✅ Selected user: {user.username}")
        if user.rfidCard:
            overwrite = input(f"   This user already has card '{user.rfidCard}'. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                print("Cancelled.")
                return

        # Read the card
        card_uid = read_card_uid()
        if not card_uid:
            print("❌ Could not read card.")
            return

        # Check if this physical card is already with someone else
        previous_owner = User.query.filter_by(physical_uid=card_uid).first()
        if previous_owner and previous_owner.id != user.id:
            print(f"⚠️  This card was previously with {previous_owner.username}. Moving it to {user.username}...")
            previous_owner.physical_uid = None
            previous_owner.is_active = False # Deactivate the old user

        # Assign to new user and make them Active
        user.physical_uid = card_uid
        user.is_active = True
        db.session.commit()

        print(f"\n✅ Success! Physical Card linked to {user.username}")
        print(f"   Friendly ID: {user.rfidCard}")
        print(f"   Physical UID: {card_uid}")
        print(f"   Status: ACTIVE")


if __name__ == '__main__':
    enroll()

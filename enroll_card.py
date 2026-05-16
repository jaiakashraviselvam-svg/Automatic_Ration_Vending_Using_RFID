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
    """Read UID from the RFID card placed on the reader."""
    if ON_PI:
        reader = SimpleMFRC522()
        print("\n📡 Hold the RFID card near the scanner...")
        try:
            uid, text = reader.read()
            return str(uid).strip()
        finally:
            GPIO.cleanup()
    else:
        # Simulation mode for testing on non-Pi hardware
        uid = input("\n[SIM] Enter a simulated card UID (e.g. RFID001): ").strip()
        return uid


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

        # Select user
        try:
            uid_input = int(input("\nEnter User ID to enroll card for: ").strip())
        except ValueError:
            print("❌ Invalid input.")
            return

        user = db.session.get(User, uid_input)
        if not user or user.is_admin:
            print(f"❌ User ID {uid_input} not found.")
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

        # Check if UID already used
        existing = User.query.filter_by(rfidCard=card_uid).first()
        if existing and existing.id != user.id:
            print(f"❌ This card (UID: {card_uid}) is already assigned to user: {existing.username}")
            return

        # Save
        user.rfidCard = card_uid
        db.session.commit()

        print(f"\n✅ Success! Card UID '{card_uid}' enrolled for user '{user.username}'")
        print("   The user can now tap this card at the vending machine to login.")


if __name__ == '__main__':
    enroll()

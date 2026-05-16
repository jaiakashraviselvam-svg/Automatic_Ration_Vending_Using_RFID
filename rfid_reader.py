#!/usr/bin/env python3
import time
import requests
import json
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

# Configure the backend API URL
# Replace 'localhost' with the IP address of the Flask server if running on a different machine
BACKEND_URL = "http://localhost:5000/api/rfid/scan"

# Initialize the RFID reader
reader = SimpleMFRC522()

print("========================================")
print("   Ration Vending RFID Reader Started   ")
print("========================================")
print(f"Connecting to Backend: {BACKEND_URL}")
print("Hold a tag near the reader...")

try:
    while True:
        # reader.read() blocks until a card is detected
        uid, text = reader.read()
        
        # Convert UID to a string format (e.g. "RFID123456")
        uid_str = str(uid)
        print(f"\n[INFO] Card Detected! UID: {uid_str}")
        
        # Send to backend
        try:
            print("       Sending to backend for verification...")
            response = requests.post(
                BACKEND_URL, 
                json={'uid': uid_str},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Access Granted! User: {data.get('user')}")
                # Optional: trigger a green LED or buzzer here
            elif response.status_code == 403:
                data = response.json()
                print(f"[DENIED] {data.get('message')}")
                # Optional: trigger a red LED or error buzzer here
            else:
                print(f"[ERROR] Backend returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to connect to backend: {e}")
            
        # Wait a moment before allowing the next scan to prevent duplicate reads
        time.sleep(2.5)

except KeyboardInterrupt:
    print("\n[INFO] Shutting down...")
finally:
    GPIO.cleanup()

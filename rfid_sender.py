"""
rfid_sender.py — Raspberry Pi RFID Scanner
Reads RFID cards and sends the UID to the Flask server
running on your LAPTOP over the local network.

Setup on Pi:
    pip install mfrc522 RPi.GPIO requests

Run:
    python rfid_sender.py --server http://192.168.1.105:5000

Replace 192.168.1.105 with your LAPTOP's local IP address.
"""

import time
import argparse
import requests

try:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    ON_PI = False
    print("[SIM MODE] MFRC522 not available — simulating scans via keyboard input")


def get_server_url():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default='http://192.168.1.105:5000',
                        help='URL of the Flask server on your laptop')
    args = parser.parse_args()
    return args.server.rstrip('/')


def send_uid(server_url, raw_uid):
    """POST the raw scanned UID to the Flask /api/rfid/scan endpoint."""
    uid = str(raw_uid)
    print(f"  📡 Sending RAW UID: {uid}")

    try:
        resp = requests.post(
            f"{server_url}/api/rfid/scan",
            json={"uid": uid},
            timeout=5
        )
        data = resp.json()
        if resp.status_code == 200:
            print(f"  ✅ Server accepted: {data.get('message', 'OK')}")
        else:
            print(f"  ❌ Server rejected: {data.get('message', 'Unknown error')}")
        return data
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  Cannot reach server at {server_url}")
        print(f"      Make sure Flask is running on your laptop and both devices are on the same WiFi.")
        return None
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return None


def run_pi_reader(server_url):
    """Read cards using the physical MFRC522 on Raspberry Pi."""
    reader = SimpleMFRC522()
    print(f"\n📡 RFID Scanner Active")
    print(f"   Server : {server_url}")
    print(f"   Status : Waiting for card scan...\n")

    last_uid = None
    last_time = 0

    try:
        while True:
            uid, _ = reader.read_no_block()
            if uid:
                uid_str = str(uid).strip()
                now = time.time()
                # Debounce: ignore same card within 3 seconds
                if uid_str != last_uid or (now - last_time) > 3:
                    print(f"🔍 Card detected: UID = {uid_str}")
                    send_uid(server_url, uid_str)
                    last_uid = uid_str
                    last_time = now
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n⛔ Scanner stopped.")
    finally:
        GPIO.cleanup()


def run_simulation(server_url):
    """Simulate RFID scans via keyboard — for testing without hardware."""
    print(f"\n⌨️  SIMULATION MODE — RFID Scanner")
    print(f"   Server : {server_url}")
    print(f"   Type a card UID and press Enter to simulate a scan.")
    print(f"   Press Ctrl+C to stop.\n")

    while True:
        try:
            uid = input("Scan (enter UID): ").strip()
            if uid:
                print(f"🔍 Simulated card: UID = {uid}")
                send_uid(server_url, uid)
        except KeyboardInterrupt:
            print("\n⛔ Simulator stopped.")
            break


def check_server(server_url):
    """Verify connection to the Flask server before starting."""
    print(f"\n🔗 Connecting to Flask server at {server_url} ...")
    try:
        r = requests.get(f"{server_url}/", timeout=4)
        print(f"   ✅ Server reachable (HTTP {r.status_code})")
        return True
    except Exception:
        print(f"   ❌ Cannot reach server!")
        print(f"      Check: Is Flask running? Same WiFi? Correct IP?")
        return False


if __name__ == '__main__':
    server_url = get_server_url()

    if not check_server(server_url):
        proceed = input("\nServer unreachable. Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            exit(1)

    if ON_PI:
        run_pi_reader(server_url)
    else:
        run_simulation(server_url)

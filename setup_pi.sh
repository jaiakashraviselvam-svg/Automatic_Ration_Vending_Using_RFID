#!/bin/bash
echo "==============================================="
echo "   Ration Vending Machine Pi Setup Script      "
echo "==============================================="

# Update system
echo "[1/4] Updating package lists..."
sudo apt-get update -y

# Enable SPI
echo "[2/4] Enabling SPI interface..."
sudo raspi-config nonint do_spi 0
echo "SPI enabled."

# Install Python and pip
echo "[3/4] Installing Python3 and Pip..."
sudo apt-get install python3 python3-pip python3-venv spidev python3-spidev -y

# Setup virtual environment
echo "[4/4] Setting up Python virtual environment and dependencies..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install spidev mfrc522 RPi.GPIO

echo "==============================================="
echo "   Setup Complete!                             "
echo "==============================================="
echo "To run the web backend:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To run the RFID reader (in a separate terminal):"
echo "  source venv/bin/activate"
echo "  python rfid_reader.py"
echo "==============================================="

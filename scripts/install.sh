#!/bin/bash
# DigitoolDB Installation Script for Linux

set -e

# Default installation directory
INSTALL_DIR="/opt/digitooldb"
CONFIG_DIR="/etc/digitooldb"
DATA_DIR="/var/lib/digitooldb"
LOG_DIR="/var/log/digitooldb"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --prefix)
      INSTALL_DIR="$2"
      shift
      shift
      ;;
    --help)
      echo "DigitoolDB Installation Script"
      echo ""
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --prefix DIR    Install to DIR (default: /opt/digitooldb)"
      echo "  --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $key"
      exit 1
      ;;
  esac
done

echo "Installing DigitoolDB..."
echo "Installation directory: $INSTALL_DIR"
echo "Configuration directory: $CONFIG_DIR"
echo "Data directory: $DATA_DIR"
echo "Log directory: $LOG_DIR"

# Create directories
sudo mkdir -p "$INSTALL_DIR"
sudo mkdir -p "$CONFIG_DIR"
sudo mkdir -p "$DATA_DIR"
sudo mkdir -p "$LOG_DIR"

# Install Python package
echo "Installing Python package..."
sudo pip install -e .

# Copy configuration file
if [ ! -f "$CONFIG_DIR/digid.conf" ]; then
  echo "Creating default configuration file..."
  sudo cp config/digid.conf "$CONFIG_DIR/digid.conf"
  
  # Update paths in config file
  sudo sed -i "s|\"data_dir\": \"data\"|\"data_dir\": \"$DATA_DIR\"|g" "$CONFIG_DIR/digid.conf"
  sudo sed -i "s|\"log_file\": \"logs/digitooldb.log\"|\"log_file\": \"$LOG_DIR/digitooldb.log\"|g" "$CONFIG_DIR/digid.conf"
fi

# Create systemd service file
echo "Creating systemd service..."
cat > digitooldb.service << EOF
[Unit]
Description=DigitoolDB Server
After=network.target

[Service]
Type=simple
ExecStart=$(which digid) --config $CONFIG_DIR/digid.conf
Restart=on-failure
User=nobody
Group=nogroup
WorkingDirectory=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

sudo mv digitooldb.service /etc/systemd/system/

# Set permissions
sudo chown -R nobody:nogroup "$DATA_DIR"
sudo chown -R nobody:nogroup "$LOG_DIR"

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "To start the server, run:"
echo "  sudo systemctl start digitooldb"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable digitooldb"
echo ""
echo "To check status:"
echo "  sudo systemctl status digitooldb"
echo ""
echo "To use the client:"
echo "  digi --help"

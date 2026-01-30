#!/bin/bash

MOSQ_CONF="/etc/mosquitto/mosquitto.conf"
INCLUDE_LINE="include_dir /etc/mosquitto/conf.d"
CONF_D_DIR="/etc/mosquitto/conf.d"
CUSTOM_CONF_FILE="$CONF_D_DIR/mosquitto.conf"
PASSWD_FILE="$CONF_D_DIR/passwd"
USERNAME="username"  # Replace with your desired MQTT username

# 1. Install Mosquitto if not installed
if ! command -v mosquitto >/dev/null 2>&1; then
    echo "Installing Mosquitto..."
    sudo apt-get update -y
    sudo apt-get install mosquitto mosquitto-clients -y
else
    echo "Mosquitto is already installed."
fi

# 2. Ensure include_dir is present in /etc/mosquitto/mosquitto.conf
if grep -Fxq "$INCLUDE_LINE" "$MOSQ_CONF"; then
    echo "include_dir already present in $MOSQ_CONF"
else
    echo "Adding include_dir to $MOSQ_CONF"
    echo "$INCLUDE_LINE" | sudo tee -a "$MOSQ_CONF" > /dev/null
fi

# 3. Ensure /etc/mosquitto/conf.d directory exists
if [ ! -d "$CONF_D_DIR" ]; then
    echo "Creating directory $CONF_D_DIR"
    sudo mkdir -p "$CONF_D_DIR"
else
    echo "Directory $CONF_D_DIR already exists."
fi

# 4. Create /etc/mosquitto/conf.d/mosquitto.conf with required settings
if [ -f "$CUSTOM_CONF_FILE" ]; then
    echo "Configuration file $CUSTOM_CONF_FILE already exists. Skipping creation."
else
    echo "Creating configuration file at $CUSTOM_CONF_FILE"
    sudo tee "$CUSTOM_CONF_FILE" > /dev/null <<EOF
# MQTT Broker Configuration

listener 1883
allow_anonymous false
password_file $PASSWD_FILE
EOF
fi

# 5. Start and enable the Mosquitto service
echo "Starting Mosquitto service..."
sudo systemctl start mosquitto

echo "Enabling Mosquitto to start on boot..."
sudo systemctl enable mosquitto

# 6. Check if service is running
SERVICE_STATUS=$(systemctl is-active mosquitto)

if [ "$SERVICE_STATUS" == "active" ]; then
    echo "Mosquitto service is active."
    
    # 7. Create password file
    echo "Creating Mosquitto password file..."
    sudo mosquitto_passwd -c "$PASSWD_FILE" "$USERNAME"
else
    echo "Mosquitto service failed to start. Exiting."
    exit 1
fi

echo "Setup complete."
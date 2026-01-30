# mqtt_client.py
import logging
import json
import threading
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import paho.mqtt.client as mqtt
from configurations.mqtt_config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_COMMAND_TOPIC,
    MQTT_STATUS_TOPIC
)

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.connection_lock = threading.Lock()
        self.message_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when client connects to MQTT broker."""
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

            # Subscribe to topics where Raspberry Pis send their state updates
            if MQTT_STATUS_TOPIC:
                client.subscribe(MQTT_STATUS_TOPIC)
                logger.info(f"Subscribed to status topic: {MQTT_STATUS_TOPIC}")

            # Removed subscriptions to "state/+" and "response/+"
            # If you want to subscribe to other specific topics, add them here.
            # Example: client.subscribe("my/specific/topic")

        else:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when client disconnects from broker."""
        self.is_connected = False
        if rc != 0:
            logger.warning("Unexpected MQTT disconnection. Will attempt to reconnect.")
        else:
            logger.info("MQTT client disconnected")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received from Raspberry Pi."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            logger.info(f"Received from Pi - Topic: '{topic}', Payload: {payload}")

            # Parse JSON payload
            try:
                json_payload = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from Pi on {topic}: {payload}")
                json_payload = {"raw_message": payload}

            # Call the message callback if set
            if self.message_callback:
                self.message_callback(topic, json_payload)

        except Exception as e:
            logger.error(f"Error processing Pi message: {e}")

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        with self.connection_lock:
            if self.is_connected:
                return True

            try:
                # Create MQTT client
                self.client = mqtt.Client()

                # Set credentials 
                if MQTT_USERNAME and MQTT_PASSWORD:
                    self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

                # Set callbacks
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message

                # Connect to broker
                logger.info(f"Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
                self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

                # Start network loop
                self.client.loop_start()

                # Wait for connection
                timeout = 10
                start_time = time.time()
                while not self.is_connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)

                if not self.is_connected:
                    logger.error("Failed to connect to MQTT broker within timeout")
                    return False

                return True

            except Exception as e:
                logger.error(f"Error connecting to MQTT broker: {e}")
                self.is_connected = False
                return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        with self.connection_lock:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                self.is_connected = False
                logger.info("Disconnected from MQTT broker")

    def send_command_to_pi(self, device_id: str, command_payload: Dict[str, Any]) -> bool:
        """
        Send command to a specific Raspberry Pi.

        Args:
            device_id: ID of the target Raspberry Pi
            command_payload: Command data to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Cannot send command: not connected to MQTT broker")
            return False

        try:
            # Build topic based on device ID and role
            role = command_payload.get("role", "unknown")
            logger.info(f"Sending to role: {role}") 

            topic = f"command/{device_id}/req/start"
            logger.info(f"Sending to topic: {topic}") 

            json_payload = json.dumps(command_payload)
            logger.info(f"And json payload: {json_payload}") 
            result = self.client.publish(topic, json_payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Command sent to Pi {device_id} on '{topic}': {json_payload}")
                return True
            else:
                logger.error(f"Failed to send command to Pi {device_id}, error code: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error sending command to Pi {device_id}: {e}")
            return False

    def set_message_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Set callback function to handle incoming messages from Raspberry Pis.

        Args:
            callback: Function that takes (topic, payload) and processes Pi responses
        """
        self.message_callback = callback
        logger.info("Message callback registered for Pi responses")

    def subscribe_to_pi_topic(self, topic: str) -> bool:
        """Subscribe to additional Pi topic if needed."""
        if not self.is_connected:
            logger.error("Cannot subscribe: not connected to MQTT broker")
            return False

        try:
            result, _ = self.client.subscribe(topic, 1)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to Pi topic: {topic}")
                return True
            else:
                logger.error(f"Failed to subscribe to '{topic}', error code: {result}")
                return False

        except Exception as e:
            logger.error(f"Error subscribing to '{topic}': {e}")
            return False

    def ensure_connection(self) -> bool:
        """Ensure connection is active, reconnect if needed."""
        if not self.is_connected:
            logger.info("Connection lost, attempting to reconnect...")
            return self.connect()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current MQTT client status for monitoring."""
        return {
            "connected": self.is_connected,
            "broker_host": MQTT_BROKER_HOST,
            "broker_port": MQTT_BROKER_PORT,
            "has_message_callback": self.message_callback is not None
        }
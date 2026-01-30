# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC")
MQTT_STATUS_TOPIC = os.getenv("MQTT_STATUS_TOPIC")
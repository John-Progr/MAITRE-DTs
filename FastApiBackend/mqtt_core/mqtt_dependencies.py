# mqtt_dependencies.py
import logging
from typing import Dict
from fastapi import Depends, HTTPException
from mqtt_core.mqtt_client import MQTTClient
from services.mqtt_service import MQTTService

logger = logging.getLogger(__name__)

# Global MQTT client instance
mqtt_client = MQTTClient()

mqtt_service = MQTTService(mqtt_client)

def get_mqtt_client() -> MQTTClient:
    """
    FastAPI dependency function to get the MQTT client.
    Ensures connection is active before returning client.
    """
    if not mqtt_client.ensure_connection():
        logger.error("MQTT client connection failed")
        raise HTTPException(
            status_code=503, 
            detail="MQTT service unavailable - cannot connect to broker"
        )
    return mqtt_client

async def startup_mqtt():
    connected = mqtt_client.connect()
    if not connected:
        raise RuntimeError("Could not connect to MQTT broker")
    
    # Subscribe to telemetry topic
    subscribed = mqtt_service.subscribe_to_telemetry()
    if not subscribed:
        raise RuntimeError("Could not subscribe to telemetry topic")

    # Register callback for incoming messages
    mqtt_client.set_message_callback(mqtt_service.receive_results)

async def shutdown_mqtt():
    """
    Clean up MQTT connection on application shutdown.
    Call this in your FastAPI app shutdown event.
    """
    logger.info("Shutting down MQTT client...")
    mqtt_client.disconnect()
    logger.info("MQTT client shutdown complete")

def get_mqtt_status() -> Dict:
    """
    Get current MQTT connection status.
    Useful for health checks and monitoring.
    """
    return mqtt_client.get_status()
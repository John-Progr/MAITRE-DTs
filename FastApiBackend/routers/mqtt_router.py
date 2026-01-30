import logging
from typing import Dict, Any, Union, List

from fastapi import APIRouter, Depends, HTTPException, status

# Correct imports based on your provided files
from mqtt_dependencies import get_mqtt_client # Provides MQTTClient instance
from schemas import ClientCommand, ForwarderCommand, ServerCommand, CommandMessage, NetworkSetupRequest # Your schemas.py
from mqtt_service import MQTTService, create_mqtt_service # Your mqtt_service.py
from mqtt_core.mqtt_client import MQTTClient # For type hinting from your mqtt_client.py

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get an instance of MQTTService
async def get_mqtt_service_instance(mqtt_client: MQTTClient = Depends(get_mqtt_client)) -> MQTTService:
    """Provides an MQTTService instance, ensuring the MQTT client is available."""
    # get_mqtt_client already ensures connection or raises HTTPException
    return create_mqtt_service(mqtt_client)


@router.get("/health", summary="Health check endpoint for the MQTT FastAPI service")
async def health_check():
    """
    Returns the health status of the MQTT FastAPI service.
    """
    return {"status": "healthy", "service": "mqtt-fastapi"}

@router.post(
    "/commands/send-single",
    response_model=Dict[str, Any],
    summary="Send a single command to a Raspberry Pi device"
)
async def send_single_command(
    command: CommandMessage, # This will automatically parse based on 'role' field
    mqtt_service: MQTTService = Depends(get_mqtt_service_instance)
) -> Dict[str, Any]:
    """
    Sends a single command (client, forwarder, or server) to a specified Raspberry Pi device.

    The type of command is determined by the 'role' field in the payload.
    - **role**: "client", "intermediate" (for forwarder), or "server"
    - Other fields depend on the role (e.g., 'ip_server' for client).
    """
    logger.info(f"Received request to send single command: {command.model_dump()}") # Use model_dump for Pydantic V2
    result = mqtt_service.send_command(command)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to send command")
        )
    return result

@router.post(
    "/commands/send-network-setup",
    response_model=Dict[str, Any],
    summary="Send a complete network setup configuration"
)
async def send_network_setup(
    setup_request: NetworkSetupRequest,
    mqtt_service: MQTTService = Depends(get_mqtt_service_instance)
) -> Dict[str, Any]:
    """
    Sends a complete network setup configuration by sending commands
    to the server, forwarders, and client devices in the correct order.

    The request body expects:
    - `server_command`: Details for the server device.
    - `forwarder_commands`: A list of details for intermediate/forwarder devices.
    - `client_command`: Details for the client device.
    """
    logger.info(f"Received request to send network setup.")
    result = mqtt_service.send_network_setup(
        setup_request.server_command,
        setup_request.forwarder_commands,
        setup_request.client_command
    )
    if result.get("overall_status") in ["failure", "partial_failure"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to fully apply network setup", "details": result}
        )
    return result
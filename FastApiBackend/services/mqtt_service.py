# mqtt_service.py
import logging
import threading
from typing import Dict, Any, Union, Optional
from mqtt_core.mqtt_client import MQTTClient
from models.mqtt_model import ClientCommand, ForwarderCommand, ServerCommand


logger = logging.getLogger(__name__)

class MQTTService:
    """Service layer for sending commands to Raspberry Pi devices via MQTT."""
    
    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt_client = mqtt_client
        self.latest_telemetry: Optional[Dict[str, Any]] = None  

        # Here we add blocking message functionality
        self.waiting_for_messages = {} # topic -> {"event": Event, "message":data}
        self.message_lock = threading.Lock()


        # Register our receive_results as the callback for mqtt_client
        self.mqtt_client.set_message_callback(self.receive_results)




    
        
    def subscribe_to_telemetry(self) -> bool:
        """Subscribe to the 'telemetry' topic."""
        return self.mqtt_client.subscribe_to_pi_topic("telemetry")

    
    def get_latest_telemetry(self) -> Optional[Dict[str, Any]]:
        """Return the most recent telemetry data received."""
        return self.latest_telemetry

    

    def send_command(self, cmd: Union[ClientCommand, ForwarderCommand, ServerCommand]) -> Dict[str, Any]:
        """Send any type of command to a Raspberry Pi."""
        logger.info(f"I am on send_command") 
        try:
            # Build payload based on command type
            if isinstance(cmd, ClientCommand):
                payload = {
                    "value": {
                        "role": "client",
                        "wireless_channel": cmd.wireless_channel,
                        "region": cmd.region,
                        "ip_server": cmd.ip_server,
                        "ip_routing": cmd.ip_routing,
                    }
                }
            elif isinstance(cmd, ForwarderCommand):
                payload = {
                    "value": {
                        "role": "forwarder",
                        "wireless_channel": cmd.wireless_channel,
                        "region": cmd.region,
                        "ip_routing_next": cmd.ip_routing_next ,
                        "ip_routing_previous": cmd.ip_routing_previous,
                        "ip_server": cmd.ip_server,
                        "ip_client": cmd.ip_client,
                    }
                }
            elif isinstance(cmd, ServerCommand):
                payload = {
                    "value": {
                        "role": "server",
                        "wireless_channel": cmd.wireless_channel,
                        "region": cmd.region,
                        "ip_client": cmd.ip_client,
                        "previous_ip": cmd.previous_ip,
                    }

                }
            else:
                return {"status": "error", "message": "Unknown command type"}
                
                # Send the command
            success = self.mqtt_client.send_command_to_pi(cmd.device_id, payload)
            logger.info(f"Success: {success}") 
            if success:
                return {
                    "status": "success",
                    "device_id": cmd.device_id,
                    "role": payload["role"]
                }
            else:
                return {
                    "status": "error",
                    "device_id": cmd.device_id,
                    "message": "Failed to send command"
                    }
                    
        except Exception as e:
                logger.error(f"Error sending command to {cmd.device_id}: {e}")
                return {
                    "status": "error",
                    "device_id": cmd.device_id,
                    "message": str(e)
                }
        

    def receive_results(self, topic: str, payload: Dict[str, Any]):
        """Callback for MQTT messages from mqtt_client._on_message."""
        logger.info(f"[MQTTService] Incoming message on topic '{topic}': {payload}")

        if topic == "telemetry":
            # Save the latest telemetry payload
            self.latest_telemetry = payload
            logger.info("[MQTTService] Telemetry updated")
        
        with self.message_lock:
            if topic in self.waiting_for_messages:
                self.waiting_for_messages[topic]["message"] = payload
                self.waiting_for_messages[topic]["event"].set()
                logger.info(f"[MQTTService] Released thread waiting for topic '{topic}'")

        if topic == "telemetry":
            return self.latest_telemetry
        else:
            logger.warning(f"[MQTTService] Unhandled topic '{topic}'")

    def wait_for_message(self, topic: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        BLOCK and wait for a message on the specified topic.
        
        Args:
            topic: The MQTT topic to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            The message payload or None if timeout
        """
        logger.info(f"[MQTTService] Blocking and waiting for message on topic '{topic}' (timeout: {timeout}s)")
        
        # Create event to block on
        event = threading.Event()
        
        with self.message_lock:
            self.waiting_for_messages[topic] = {
                "event": event,
                "message": None
            }
        
        # BLOCK HERE until message arrives or timeout
        if event.wait(timeout):
            with self.message_lock:
                message = self.waiting_for_messages[topic]["message"]
                del self.waiting_for_messages[topic]
            logger.info(f"[MQTTService] Received message for topic '{topic}': {message}")
            return message
        else:
            # Timeout occurred
            with self.message_lock:
                if topic in self.waiting_for_messages:
                    del self.waiting_for_messages[topic]
            logger.warning(f"[MQTTService] Timeout waiting for message on topic '{topic}'")
            return None





    def send_network_setup(self, server_cmd: ServerCommand, 
                          forwarder_cmds: list[ForwarderCommand], 
                          client_cmd: ClientCommand) -> Dict[str, Any]:
        """Send complete network setup commands in correct order."""
        results = []
        
        # Send server first
        results.append(self.send_command(server_cmd))
        
        # Send forwarders
        for forwarder_cmd in forwarder_cmds:
            results.append(self.send_command(forwarder_cmd))
        
        # Send client last
        results.append(self.send_command(client_cmd))
        
        # Check overall status
        failed = [r for r in results if r["status"] != "success"]
        
        return {
            "overall_status": "success" if not failed else "partial_failure" if len(failed) < len(results) else "failure",
            "results": results,
            "failed_count": len(failed)
        }


# Factory function
def create_mqtt_service(mqtt_client: MQTTClient) -> MQTTService:
    return MQTTService(mqtt_client)
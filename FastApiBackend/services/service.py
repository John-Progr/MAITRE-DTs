import logging
import time
from datetime import datetime
from models.api_model import DataTransferRateResponse, DataTransferRateRequest
from typing import List, Optional 
from services.mqtt_service import MQTTService
from utils.wireless_channels import get_channel_regions, get_region
from utils.things import get_thing_id_by_ip
from models.mqtt_model import ClientCommand, ForwarderCommand, ServerCommand

logger = logging.getLogger(__name__)


def get_data_transfer_rate(
    source: str,
    destination: str,
    path: List[str],
    wireless_channel: Optional[int],
    mqtt_service: MQTTService
) -> DataTransferRateResponse:

    region = get_channel_regions(wireless_channel) # hardcoded region


    # get IDs
    source_id = get_thing_id_by_ip(source)
    destination_id = get_thing_id_by_ip(destination)



    # Multi-hop
    if path:

        server_cmd = ServerCommand(
                device_id=destination_id,
                wireless_channel=wireless_channel,
                region=region,
                ip_client = source,
                previous_ip = path[len(path) - 1]
        )
        logger.info(f"SERVER value: {server_cmd}")
        mqtt_service.send_command(server_cmd)



        next_hops = list(path[1:]) + [destination]

        for idx, (intermediate_ip, next_ip) in enumerate(zip(filter(None, path), next_hops)):
            
            previous_ip = source if idx == 0 else path[idx - 1]

            intermediate_id = get_thing_id_by_ip(intermediate_ip)

            forwarder_cmd = ForwarderCommand(
                device_id=intermediate_id,
                wireless_channel=wireless_channel,
                region=region,
                ip_routing_next=next_ip,
                ip_routing_previous=previous_ip,
                ip_server=destination,
                ip_client=source  
            )
            logger.info(f"FORWARDER value: {forwarder_cmd}")

            mqtt_service.send_command(forwarder_cmd)

            
            client_cmd = ClientCommand(
                device_id=source_id,
                wireless_channel=wireless_channel,
                region=region,
                ip_server=destination,
                ip_routing=path[0] if path else destination
            )
            mqtt_service.send_command(client_cmd)
            logger.info(f"CLIENT value: {client_cmd}")

    # Single Hop
    else:
        # INFO level
        
        server_cmd = ServerCommand(
                device_id=destination_id,
                wireless_channel=wireless_channel,
                region=region,
                ip_client = source,
                previous_ip = source
        )
        logger.info("_______________________________________________")
        logger.info(f"My variable value: {server_cmd}")
        mqtt_service.send_command(server_cmd)


        # --- Send client command ---
        client_cmd = ClientCommand(
            device_id=source_id,
            wireless_channel=wireless_channel,
            region=region,
            ip_server=destination,
            ip_routing=destination
        )

        logger.info("_______________________________________________")
        logger.info(f"My variable value: {client_cmd}")

        mqtt_service.send_command(client_cmd)


    # wait for telemetry
    message = mqtt_service.wait_for_message("telemetry", timeout=100.0)
    rate_mbps = message["sent_rate_mbps"]

    return DataTransferRateResponse(
        source=source,
        destination=destination,
        rate_mbps=rate_mbps,
        wireless_channel=wireless_channel,
        timestamp=int(datetime.utcnow().timestamp() * 1000)
    )

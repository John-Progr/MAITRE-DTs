from pydantic import BaseModel
from typing import Optional, Union, List, Literal


class BaseCommand(BaseModel):
    device_id: str
    wireless_channel: int
    region: str


class ClientCommand(BaseCommand):
    role: Literal["client"] = "client"
    ip_server: str
    ip_routing: Optional[str]


class ForwarderCommand(BaseCommand):
    role: Literal["intermediate"] = "intermediate"
    ip_routing_next: str
    ip_routing_previous: str
    ip_server: str
    ip_client: str


class ServerCommand(BaseCommand):
    role: Literal["server"] = "server"
    ip_client: str
    previous_ip: str


# For use in request bodies where the type could be any one of the three
CommandMessage = Union[ClientCommand, ForwarderCommand, ServerCommand]


class NetworkSetupRequest(BaseModel):
    server_command: ServerCommand
    forwarder_commands: List[ForwarderCommand]
    client_command: ClientCommand

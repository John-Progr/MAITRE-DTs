# utils.py
from constants.things import ThingsConstants

def get_thing_id_by_ip(ip: str) -> str:
    """Get thing ID for a given IP address."""
    return ThingsConstants.IP_TO_THING_ID.get(ip)
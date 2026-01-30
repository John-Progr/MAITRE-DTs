from typing import Optional, Tuple, Union, List
from constants.wireless_channels import CHANNEL_INFO



# Helper functions
def get_channel_frequency(channel: int) -> int:
    """Get frequency for a channel"""
    info = CHANNEL_INFO.get(channel)
    return info["frequency"] if info else None

def get_channel_regions(channel: int) -> tuple:
    """Get regions where this channel is allowed"""
    info = CHANNEL_INFO.get(channel)
    return info["regions"] if info else ()

def is_channel_allowed_in_region(channel: int, region: str) -> bool:
    """Check if channel is allowed in specific region"""
    regions = get_channel_regions(channel)
    return region.upper() in regions

def get_channels_for_region(region: str) -> list:
    """Get all channels allowed in a region"""
    return [channel for channel, info in CHANNEL_INFO.items() 
            if region.upper() in info["regions"]]


def get_region(regions: Union[Tuple, List[Tuple]]) -> Optional[Tuple]:
    """
    Extract a single region tuple from input.

    If regions is a list or iterable of tuples, return the first one.
    If it's already a single tuple, just return it.
    If regions is empty or None, return None.
    """

    if not regions:
        return None

    if isinstance(regions, tuple) and (not isinstance(regions[0], (list, tuple))):
        # Single tuple, e.g., (start_freq, end_freq)
        return regions

    if isinstance(regions, list) or (isinstance(regions, tuple) and isinstance(regions[0], (list, tuple))):
        # List/tuple of tuples
        return regions[0]

    return None
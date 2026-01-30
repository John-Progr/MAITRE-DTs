from pydantic import BaseModel, Field
from typing import List, Optional 


class DataTransferRateRequest(BaseModel):
    source: str = Field(..., description="Source IP address")
    destination: str = Field(..., description="Destination IP address")
    path: List[str] = Field(..., description="List of IP addresses in the path")
    wireless_channel: Optional[int] =Field ( None, description="Wireless channel used in the ad hoc network")


class DataTransferRateResponse(BaseModel):
    source: str
    destination: str
    rate_mbps: float
    wireless_channel: int
    timestamp: int


class HealthCheckResponse(BaseModel):
    status: str
    message: str
    timestamp: int
# exceptions.py
from fastapi import HTTPException

def raise_bad_request(message: str):
    raise HTTPException(status_code=400, detail=message)

def raise_internal_server_error(message: str = "Internal server error"):
    raise HTTPException(status_code=500, detail=message)
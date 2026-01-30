import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.router import router
from mqtt_core.mqtt_dependencies import startup_mqtt, shutdown_mqtt

# ✅ Configure logging once here
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

app = FastAPI(
    title="Data Transfer Rate API",
    description="An API to get the data transfer rate between two nodes in a multihop scenario",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    await startup_mqtt()

@app.on_event("shutdown") 
async def shutdown():
    await shutdown_mqtt()

@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(exc), status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

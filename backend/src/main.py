from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from infrastructure.settings import settings
from interfaces.api import health, sensors
from interfaces.api import health, sensors, devices
from interfaces.api import health, sensors, devices, locations

app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(sensors.router)
app.include_router(devices.router)
app.include_router(locations.router)

@app.get("/")
def discovery():
    return {
        "message": "Welcome to the Smart Greenhouse API",
        "api_reference": "/scalar",
        "openapi": "/openapi.json"
    }

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API Reference"
    )
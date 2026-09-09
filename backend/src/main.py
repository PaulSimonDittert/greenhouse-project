from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from infrastructure.settings import settings
from interfaces.api import health, sensors

# Create the app with Swagger/ReDoc explicitly disabled per requirements
app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the health route we made earlier
app.include_router(health.router)
app.include_router(sensors.router)

# GET / discovery route
@app.get("/")
def discovery():
    return {
        "message": "Welcome to the Smart Greenhouse API",
        "api_reference": "/scalar",
        "openapi": "/openapi.json"
    }

# Scalar API documentation UI
@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API Reference"
    )
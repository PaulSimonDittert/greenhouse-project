import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from application.readings.sampler import SimulationSampler
from infrastructure.db import SessionLocal
from infrastructure.settings import settings
from interfaces.api import health, sensors, devices, locations

logger = logging.getLogger(__name__)


def _sample_once() -> None:
    with SessionLocal() as db:
        SimulationSampler(db).run_once(datetime.now(timezone.utc))


async def _simulation_sampler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(_sample_once)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Simulation sampler tick failed")
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    sampler_task = asyncio.create_task(_simulation_sampler_loop())
    try:
        yield
    finally:
        sampler_task.cancel()
        try:
            await sampler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
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
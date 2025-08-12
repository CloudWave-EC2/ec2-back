from fastapi import FastAPI
from app.models import Base
from app.database import writer_engine
from app.routers.api import api

app = FastAPI(title="CGV Booking API")

@app.on_event("startup")
async def on_startup():
    try:
        async with writer_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[startup] DB connected & tables created.")
    except Exception as e:
        print(f"[startup][ERROR] DB init failed: {e}")
        raise

app.include_router(api)
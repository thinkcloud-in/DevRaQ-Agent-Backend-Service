from fastapi import FastAPI
from routes.metrics_routes import router as influx_router
from routes.kill_process import router as kill_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(influx_router, prefix="/api")
app.include_router(kill_router, prefix="/api")


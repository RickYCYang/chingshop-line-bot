from fastapi import Request, FastAPI, HTTPException
from loguru import logger

from app.apis.routers import router

app = FastAPI()

app.include_router(router)

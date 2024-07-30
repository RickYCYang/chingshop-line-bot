from fastapi import FastAPI

from app.apis.routers import router

app = FastAPI()

app.include_router(router)

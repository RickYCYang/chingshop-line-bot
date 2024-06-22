from fastapi import APIRouter
from app.apis.line_apis import router as line_router

router = APIRouter()
router.include_router(line_router)

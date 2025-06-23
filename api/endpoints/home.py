from fastapi import APIRouter

router = APIRouter(prefix="/rooms")

@router.get("/")
async def home():
    return {
        "success": True,
        "warning": "This REST API uses POST method.",
        "doc_url": "/docs",
        "redoc_url": "/redoc"
    }

@router.post("/")
async def home():
    return {
        "success": True,
        "doc_url": "/docs",
        "redoc_url": "/redoc"
    }
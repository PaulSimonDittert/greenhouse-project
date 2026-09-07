from fastapi import APIRouter
from infrastructure.db import check_database

router = APIRouter()

@router.get("/health")
def health_check():
    db_ok = check_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "fail"
    }
from fastapi import APIRouter, Depends
from backend.app.core.deps import get_db
from sqlalchemy import text
import redis
from backend.app.core.config import settings
from backend.app.services.ai_service import AIService

router = APIRouter()

@router.get("/ready")
def ready(db=Depends(get_db)):
    # check db
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        return {"db": "unavailable", "error": str(e)}
    # check redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception as e:
        return {"redis": "unavailable", "error": str(e)}
    # check model
    ai = AIService()
    ok, info = ai.health_check()
    return {"db": "ok", "redis": "ok", "model": info}

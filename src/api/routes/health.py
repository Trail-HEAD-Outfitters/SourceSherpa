from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["infra"])

@router.get("/ping")
def ping() -> dict[str, str]:
    """Basic health probe for load-balancers and CI."""
    return {"status": "ok"}
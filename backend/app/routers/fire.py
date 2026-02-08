"""FIRe API endpoints."""

from fastapi import APIRouter

from app.models.fire import CreditSimRequest, CreditSimResult, FIReData
from app.services import fire_service

router = APIRouter(prefix="/api/fire", tags=["fire"])


@router.get("/relationships", response_model=FIReData)
def get_relationships():
    """Get all encompassing relationships."""
    return fire_service.get_fire_data()


@router.post("/simulate", response_model=CreditSimResult)
def simulate_credit(req: CreditSimRequest):
    """Simulate credit flow for a card."""
    return fire_service.simulate_credit(req.card_id, req.passed)


@router.get("/heatmap")
def get_heatmap():
    """Get heatmap data for visualization."""
    return fire_service.get_heatmap_data()

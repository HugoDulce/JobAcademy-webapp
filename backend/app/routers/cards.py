"""Card API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.models.card import Card, CardCreate, CardUpdate, ValidationResult
from app.services import card_service
from app.services.validation_service import validate_card

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=list[Card])
def list_cards(
    pillar: str | None = Query(None),
    layer: str | None = Query(None),
    search: str | None = Query(None),
):
    """List all cards with optional filters."""
    cards = card_service.list_cards()

    if pillar:
        cards = [c for c in cards if c.pillar and pillar.lower() in c.pillar.lower()]
    if layer:
        cards = [
            c
            for c in cards
            if c.knowledge_layer and layer.lower() in c.knowledge_layer.lower()
        ]
    if search:
        q = search.lower()
        cards = [
            c
            for c in cards
            if q in c.card_id.lower()
            or q in c.prompt.lower()
            or q in c.solution.lower()
        ]

    return cards


@router.get("/{card_id}", response_model=Card)
def get_card(card_id: str):
    """Get a single card by ID."""
    card = card_service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    return card


@router.post("", response_model=Card, status_code=201)
def create_card(data: CardCreate):
    """Create a new card."""
    existing = card_service.get_card(data.card_id)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Card {data.card_id} already exists"
        )

    from app.parsers.card_parser import parse_card_id
    from datetime import datetime, timezone

    id_info = parse_card_id(data.card_id)
    card = Card(
        card_id=data.card_id,
        deck=data.deck,
        tags=data.tags,
        fire_weight=data.fire_weight,
        notion_last_edited=datetime.now(timezone.utc).isoformat(),
        prompt=data.prompt,
        solution=data.solution,
        pillar=id_info["pillar"],
        knowledge_layer=id_info["knowledge_layer"],
        filename=f"{data.card_id}.md",
    )
    card_service.save_card(card)
    return card


@router.put("/{card_id}", response_model=Card)
def update_card(card_id: str, data: CardUpdate):
    """Update an existing card."""
    card = card_service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")

    if data.deck is not None:
        card.deck = data.deck
    if data.tags is not None:
        card.tags = data.tags
    if data.fire_weight is not None:
        card.fire_weight = data.fire_weight
    if data.prompt is not None:
        card.prompt = data.prompt
    if data.solution is not None:
        card.solution = data.solution

    card_service.save_card(card)
    return card


@router.get("/{card_id}/validate", response_model=ValidationResult)
def validate_card_endpoint(card_id: str):
    """Validate a card against quality rules."""
    card = card_service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    return validate_card(card.model_dump())


@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: str):
    """Delete a card."""
    if not card_service.delete_card(card_id):
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")

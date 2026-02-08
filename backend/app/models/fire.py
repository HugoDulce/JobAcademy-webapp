from pydantic import BaseModel


class EncompassingRelationship(BaseModel):
    parent_card_id: str
    child_card_id: str
    weight: float


class FIReData(BaseModel):
    relationships: list[EncompassingRelationship]
    standalone_cards: list[str]


class CreditSimRequest(BaseModel):
    card_id: str
    passed: bool


class CreditSimResult(BaseModel):
    card_id: str
    passed: bool
    credits: list[dict]  # [{card_id, credit}]

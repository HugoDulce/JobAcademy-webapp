from pydantic import BaseModel


class Card(BaseModel):
    card_id: str
    deck: str
    tags: list[str]
    fire_weight: float
    notion_last_edited: str
    prompt: str
    solution: str
    # Derived from card_id
    pillar: str | None = None
    knowledge_layer: str | None = None
    cognitive_layer: str | None = None
    filename: str | None = None
    topic: str | None = None
    concept: str | None = None
    has_visual: bool = False
    concept_node: str | None = None
    subtopic: str | None = None


class CardCreate(BaseModel):
    card_id: str
    deck: str
    tags: list[str]
    fire_weight: float = 0.5
    prompt: str
    solution: str
    concept_node: str | None = None
    subtopic: str | None = None


class CardUpdate(BaseModel):
    deck: str | None = None
    tags: list[str] | None = None
    fire_weight: float | None = None
    prompt: str | None = None
    solution: str | None = None


class ValidationResult(BaseModel):
    card_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    checks: dict[str, bool]

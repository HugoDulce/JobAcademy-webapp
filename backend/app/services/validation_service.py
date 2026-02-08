"""Card quality validation — enforces Matuschak's 5 properties + atomicity rules."""

import re

from app.models.card import ValidationResult


def validate_card(card_data: dict) -> ValidationResult:
    """Validate a card against quality rules. Returns errors (blocking) and warnings."""
    card_id = card_data.get("card_id", "unknown")
    prompt = card_data.get("prompt", "")
    solution = card_data.get("solution", "")
    knowledge_layer = card_data.get("knowledge_layer", "")
    fire_weight = card_data.get("fire_weight", 0.5)
    deck = card_data.get("deck", "")
    tags = card_data.get("tags", [])

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    # --- Required fields ---
    checks["has_prompt"] = bool(prompt.strip())
    if not checks["has_prompt"]:
        errors.append("Prompt is empty")

    checks["has_solution"] = bool(solution.strip())
    if not checks["has_solution"]:
        errors.append("Solution is empty")

    checks["has_deck"] = "::" in deck
    if not checks["has_deck"]:
        errors.append("Deck must use :: hierarchy (e.g. JobAcademy::Concept::Pillar)")

    checks["has_tags"] = len(tags) > 0
    if not checks["has_tags"]:
        warnings.append("No tags specified")

    # --- Card ID format ---
    id_pattern = r"^[a-z]+-\d+[CMPI]-\d+[a-z]?$|^[a-z]+-[A-Z]+-\d+[a-z]?$"
    checks["valid_card_id"] = bool(re.match(id_pattern, card_id))
    if not checks["valid_card_id"]:
        warnings.append(f"Card ID '{card_id}' doesn't follow naming convention")

    # --- FIRe weight range ---
    checks["valid_fire_weight"] = 0.0 <= fire_weight <= 1.0
    if not checks["valid_fire_weight"]:
        errors.append(f"FIRe weight {fire_weight} must be between 0.0 and 1.0")

    # --- M1: FOCUSED — One retrieval target ---
    # Check for numbered lists in answer (suggests multiple targets)
    numbered_lines = re.findall(r"^\d+\.\s", solution, re.MULTILINE)
    checks["focused"] = len(numbered_lines) <= 1
    if not checks["focused"]:
        errors.append(
            f"Answer has {len(numbered_lines)} numbered items — "
            "each should be a separate card (Rule A1)"
        )

    # --- M2: PRECISE — No vague words in prompt ---
    vague_words = ["important", "main", "best", "describe everything", "tell me about"]
    prompt_lower = prompt.lower()
    found_vague = [w for w in vague_words if w in prompt_lower]
    checks["precise"] = len(found_vague) == 0
    if not checks["precise"]:
        warnings.append(f"Prompt contains vague words: {found_vague} (Rule M2)")

    # --- M3: CONSISTENT — No "it depends" ---
    solution_lower = solution.lower()
    checks["consistent"] = "it depends" not in solution_lower
    if not checks["consistent"]:
        errors.append("Answer contains 'it depends' — violates consistency (Rule M3)")

    # --- S1: TELEGRAPHIC — Answer length ---
    answer_lines = len([l for l in solution.split("\n") if l.strip()])
    is_code = knowledge_layer == "Programming" or "```" in solution
    checks["telegraphic"] = answer_lines <= 10 or is_code
    if not checks["telegraphic"]:
        warnings.append(
            f"Answer is {answer_lines} lines — consider telegraphic style (Rule S1)"
        )

    # --- S3: NO HEDGING ---
    hedging_words = ["however", "although", "sometimes", "it depends"]
    found_hedging = [w for w in hedging_words if w in solution_lower]
    checks["no_hedging"] = len(found_hedging) == 0
    if not checks["no_hedging"]:
        warnings.append(f"Answer contains hedging: {found_hedging} (Rule S3)")

    # --- Math card structure ---
    if knowledge_layer == "Mathematical":
        has_latex = "$" in solution
        has_reading = "reading:" in solution_lower
        has_table = "| symbol" in solution_lower or "| " in solution

        checks["math_has_latex"] = has_latex
        if not has_latex:
            errors.append("Math card missing LaTeX formula")

        checks["math_has_reading"] = has_reading
        if not has_reading:
            errors.append("Math card missing plain-English reading")

        checks["math_has_table"] = has_table
        if not has_table:
            warnings.append("Math card should have component table")
    else:
        checks["math_has_latex"] = True
        checks["math_has_reading"] = True
        checks["math_has_table"] = True

    # --- M5: EFFORTFUL — No answer leaking ---
    if prompt and solution:
        prompt_words = set(re.findall(r"\b\w{5,}\b", prompt_lower))
        solution_words = set(re.findall(r"\b\w{5,}\b", solution_lower))
        overlap = prompt_words & solution_words
        # Exclude common words
        common = {"which", "about", "given", "class", "model", "naive", "bayes", "what's"}
        overlap -= common
        checks["effortful"] = len(overlap) < 5
        if not checks["effortful"]:
            sample = list(overlap)[:4]
            warnings.append(f"Prompt may leak answer — {len(overlap)} word overlaps: {sample}")
    else:
        checks["effortful"] = True

    return ValidationResult(
        card_id=card_id,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checks=checks,
    )

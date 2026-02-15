---
deck: "JobAcademy::Uncategorized::4-Objective"
tags: [uncategorized, conceptual, explain]
card_id: "nb-4C-02b"
fire_weight: 0.5
notion_last_edited: "2026-02-08T17:05:00.000Z"
concept_node: "NB"
---

# nb-4C-02b

START
If NB can't overfit via iteration, what failure mode does it have?
END

START
Assumption violation: Features aren't actually independent.

When features correlate strongly, NB double-counts evidence → overconfident predictions.

Example: 
- Feature 1: "contains word 'viagra'"
- Feature 2: "contains word 'pills'"

These correlate in spam. NB treats them as independent → overstates spam probability.

Result: Poor calibration, but rank-ordering might still work.
END

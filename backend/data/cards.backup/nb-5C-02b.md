---
deck: "JobAcademy::Uncategorized::5-Evaluation"
tags: [uncategorized, conceptual, explain]
card_id: "nb-5C-02b"
fire_weight: 0.5
notion_last_edited: "2026-02-08T17:06:00.000Z"
concept_node: "NB"
---

# nb-5C-02b

START
When does NB's poor calibration NOT matter?
END

START
When you only use rankings, not probabilities.

Examples:
- Spam filter: rank emails by score, take top K
- Recommendation: rank items, show top 10
- Search: rank documents by relevance

Calibration = "are predicted probabilities accurate?"
Ranking = "is the order correct?"

NB often ranks well even with bad calibration. If P(A) = 0.8 and P(B) = 0.6 are both wrong but preserve order, ranking still works.
END

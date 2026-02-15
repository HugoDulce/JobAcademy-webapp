---
deck: "JobAcademy::Uncategorized::4-Objective"
tags: [uncategorized, mathematical, explain]
card_id: "nb-4M-01a"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:05:00.000Z"
concept_node: "NB"
subtopic: "algorithm"
---

# nb-4M-01a

START
Write the log-likelihood NB maximizes (for GaussianNB).
END

START
log L = ∑ₙ log P(yₙ | xₙ)

Expanding:
= ∑ₙ [ log P(yₙ) + ∑ᵢ log P(xₙᵢ | yₙ) ]

For Gaussian:
log P(xᵢ|y) = -½ log(2πσ²) - (xᵢ - μ)² / (2σ²)

NB doesn't iterate to maximize this — closed-form MLE solutions exist.
END

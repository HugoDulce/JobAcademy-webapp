---
deck: "JobAcademy::Uncategorized::5-Evaluation"
tags: [uncategorized, conceptual, explain]
card_id: "nb-5C-01b"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:06:00.000Z"
concept_node: "NB"
subtopic: "evaluation"
---

# nb-5C-01b

START
Which metrics should you use for imbalanced classification with NB?
END

START
Precision: Of predicted positives, how many are correct?
Use when: False positives are costly

Recall: Of actual positives, how many did we catch?
Use when: False negatives are costly

F1: Harmonic mean of precision and recall
Use when: Balance both errors

ROC-AUC: Rank-ordering quality across thresholds
Use when: Threshold isn't fixed

Don't use: Accuracy (majority-class bias)
END

---
deck: "JobAcademy::Uncategorized::5-Evaluation"
tags: [uncategorized, conceptual, explain]
card_id: "nb-5C-01a"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:06:00.000Z"
---

# nb-5C-01a

START
When is accuracy a misleading metric for Naive Bayes?
END

START
Imbalanced classes.

Example: 95% normal emails, 5% spam
Model predicts "normal" for everything → 95% accuracy
But catches zero spam → useless model

Why NB vulnerable: Already biased toward majority class via priors. Accuracy doesn't penalize this.

Use instead: Precision, recall, F1, or ROC-AUC.
END

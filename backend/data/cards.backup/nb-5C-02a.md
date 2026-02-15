---
deck: "JobAcademy::Uncategorized::5-Evaluation"
tags: [uncategorized, conceptual, explain]
card_id: "nb-5C-02a"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:06:00.000Z"
concept_node: "NB"
---

# nb-5C-02a

START
What calibration problem does NB have?
END

START
Overconfident predictions due to independence assumption violation.

When features correlate, NB double-counts evidence → predicted probabilities too extreme (close to 0 or 1).

Example: Predicts 0.99 when true probability is 0.70.

Why it matters: If you use predicted probabilities for decisions (not just rankings), miscalibration causes bad choices.

Fix: Calibrate with CalibratedClassifierCV.
END

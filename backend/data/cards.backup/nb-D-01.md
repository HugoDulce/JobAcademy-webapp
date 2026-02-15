---
deck: "JobAcademy::Uncategorized::5-Evaluation"
tags: [uncategorized, programming, debug]
card_id: "nb-D-01"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:07:00.000Z"
concept_node: "NB"
---

# nb-D-01

START
This code computes ROC-AUC wrong. Find the bug.

python
y_proba = nb.predict_proba(X_test)
auc = roc_auc_score(y_test, y_proba[:, 0])

END

START
Bug: Using column 0 instead of column 1.

predict_proba returns [P(class_0), P(class_1)]

ROC-AUC needs P(positive class)

If classes = [0, 1], positive = 1 → use column 1
If classes = ['no', 'yes'], positive = 'yes' → use column 1

Fix:
python
y_proba = nb.predict_proba(X_test)[:, 1]  # Column 1 for positive class
auc = roc_auc_score(y_test, y_proba)


Safe approach:
python
pos_label = 1
pos_idx = list(nb.classes_).index(pos_label)
y_proba = nb.predict_proba(X_test)[:, pos_idx]

END

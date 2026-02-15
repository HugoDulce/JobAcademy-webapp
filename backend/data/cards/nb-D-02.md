---
deck: "JobAcademy::Uncategorized::2-Data"
tags: [uncategorized, programming, debug]
card_id: "nb-D-02"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:07:00.000Z"
concept_node: "NB"
subtopic: "implementation-sklearn"
---

# nb-D-02

START
Model performs poorly. Find the bug.

python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

nb = GaussianNB()
nb.fit(X_train_scaled, y_train)
y_pred = nb.predict(X_test)  # Bug here

END

START
Bug: Forgot to scale test data.

Train was scaled, test wasn't → different distributions → wrong predictions.

Fix:
python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Use same scaler

nb = GaussianNB()
nb.fit(X_train_scaled, y_train)
y_pred = nb.predict(X_test_scaled)  # Fixed


Why it matters: GaussianNB computes means/vars from training. If test data is on different scale, predicted probabilities are nonsense.

Prevention: Use Pipeline to enforce scaling.
END

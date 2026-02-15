---
deck: "JobAcademy::Uncategorized::1-Use Case"
tags: [uncategorized, programming, extend]
card_id: "nb-EXT-02"
fire_weight: 0.7
notion_last_edited: "2026-02-08T17:09:00.000Z"
concept_node: "NB"
subtopic: "applications"
---

# nb-EXT-02

START
Extend binary NB code to handle 3+ classes. Test on iris dataset.
END

START
python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report

# Load multi-class data
iris = load_iris()
X, y = iris.data, iris.target  # 3 classes: 0, 1, 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# NB handles multi-class natively
nb = GaussianNB()
nb.fit(X_train, y_train)

y_pred = nb.predict(X_test)
y_proba = nb.predict_proba(X_test)  # Shape: (n_samples, 3)

print(classification_report(y_test, y_pred, target_names=iris.target_names))
print(f"\nClasses: {nb.classes_}")  # [0, 1, 2]
print(f"Priors: {nb.class_prior_}")  # P(y=0), P(y=1), P(y=2)


Key insight: NB naturally extends to multi-class via one-vs-rest comparison of posteriors.
END

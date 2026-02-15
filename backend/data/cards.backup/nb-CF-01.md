---
deck: "JobAcademy::Uncategorized::2-Data"
tags: [uncategorized, programming, extend]
card_id: "nb-CF-01"
fire_weight: 0.7
notion_last_edited: "2026-02-08T17:07:00.000Z"
concept_node: "COND"
---

# nb-CF-01

START
Generate synthetic data where features ARE correlated. Train NB. Show it fails.
END

START
python
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

# Correlated features
np.random.seed(42)
X1 = np.random.randn(1000)
X2 = X1 + 0.5 * np.random.randn(1000)  # Highly correlated with X1
y = (X1 + X2 > 0).astype(int)  # Label depends on both

X = np.column_stack([X1, X2])

# NB assumes independence
nb = GaussianNB()
nb_score = nb.fit(X[:800], y[:800]).score(X[800:], y[800:])

# LogReg models correlation
lr = LogisticRegression()
lr_score = lr.fit(X[:800], y[:800]).score(X[800:], y[800:])

print(f"NB: {nb_score:.3f}")   # Lower due to double-counting
print(f"LogReg: {lr_score:.3f}")  # Higher, handles correlation


Insight: When CI violated, NB underperforms.
END

---
deck: "JobAcademy::Uncategorized::2-Data"
tags: [uncategorized, programming, debug]
card_id: "nb-CF-02"
fire_weight: 0.6
notion_last_edited: "2026-02-08T17:07:00.000Z"
concept_node: "NB"
subtopic: "implementation-numpy"
---

# nb-CF-02

START
Create data that crashes GaussianNB due to zero variance. Show the error.
END

START
python
import numpy as np
from sklearn.naive_bayes import GaussianNB

# Feature with zero variance in one class
X = np.array([[1, 5], [1, 6], [1, 7],  # Class 0: X[:,0] is constant
              [2, 5], [3, 6], [4, 7]]) # Class 1: varies
y = np.array([0, 0, 0, 1, 1, 1])

nb = GaussianNB(var_smoothing=0)  # Disable smoothing
nb.fit(X, y)

# Crashes on predict
X_test = np.array([[1, 5]])
try:
    nb.predict(X_test)
except:
    print("Error: Division by zero in Gaussian PDF")

# Fix: Enable smoothing (default 1e-9)
nb_fixed = GaussianNB()  # var_smoothing=1e-9
nb_fixed.fit(X, y)
print(nb_fixed.predict(X_test))  # Works

END

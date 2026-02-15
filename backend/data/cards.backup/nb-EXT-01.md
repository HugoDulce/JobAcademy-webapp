---
deck: "JobAcademy::Uncategorized::3-Algorithm"
tags: [uncategorized, programming, extend]
card_id: "nb-EXT-01"
fire_weight: 0.9
notion_last_edited: "2026-02-08T17:09:00.000Z"
concept_node: "NB"
---

# nb-EXT-01

START
Implement MultinomialNB fit() and predict() from scratch. Handle Laplace smoothing.
END

START
python
import numpy as np

class MultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha  # Laplace smoothing
    
    def fit(self, X, y):
        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)
        n_features = X.shape[1]
        
        # Priors
        self.class_count_ = np.zeros(n_classes)
        # Feature counts per class
        self.feature_count_ = np.zeros((n_classes, n_features))
        
        for idx, c in enumerate(self.classes_):
            X_c = X[y == c]
            self.class_count_[idx] = X_c.shape[0]
            self.feature_count_[idx, :] = X_c.sum(axis=0)
        
        # Log probabilities with smoothing
        self.class_log_prior_ = np.log(self.class_count_ / self.class_count_.sum())
        
        smoothed_fc = self.feature_count_ + self.alpha
        smoothed_cc = smoothed_fc.sum(axis=1)
        self.feature_log_prob_ = np.log(smoothed_fc / smoothed_cc[:, np.newaxis])
        
        return self
    
    def predict(self, X):
        log_probs = X @ self.feature_log_prob_.T + self.class_log_prior_
        return self.classes_[np.argmax(log_probs, axis=1)]

END

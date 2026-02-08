# Naive Bayes — Complete Card Set
## Rewritten with 14 Quality Rules · Organized by FIRe Hierarchy

---

## FIRe Encompassing Tree

```
⭐ MASTERY GATE: Build GaussianNB from scratch in numpy
│
├─ Level 3 — Programming (numpy/sklearn)
│  ├─ nb-3P-01  fit() in numpy                    [encompasses: 4M-01a, 4M-02, 4C-01, 3M-02a, 2C-01]
│  ├─ nb-3P-02  predict() in numpy                [encompasses: 3M-01a, 3M-01b, 3M-02a, 3C-01, 3C-02]
│  ├─ nb-3P-03  var_smoothing bug fix             [encompasses: 2C-03]
│  ├─ nb-2P-01  train_test_split with stratify    [standalone]
│  ├─ nb-2P-02  sklearn Pipeline                  [standalone]
│  ├─ nb-2P-03  GridSearchCV                      [standalone]
│  ├─ nb-5P-01  evaluation code (metrics)         [encompasses: 5M-01, 5M-02, 5C-01a]
│  └─ nb-5P-02  calibration code                  [encompasses: 5C-02a, 5C-02b]
│
├─ Level 2 — Mathematical (formulas + computation)
│  ├─ nb-3M-03  Full classification computation   [encompasses: 3M-01a, 3M-01b, 3M-02a, 3M-02b]
│  │  ├─ nb-3M-02b  Gaussian PDF numerical        [encompasses: 3M-02a]
│  │  │  └─ nb-3M-02a  Gaussian PDF formula ✅
│  │  ├─ nb-3M-02c  Gaussian intuition + proof ✅  [encompasses: 3M-02a]
│  │  ├─ nb-3M-01b  Log-space formula ✅           [encompasses: 3M-01a]
│  │  │  └─ nb-3M-01a  Direct NB formula ✅
│  │  └─ nb-3M-01c  Why P(x) drops out ✅
│  ├─ nb-3M-04  MultinomialNB formula             [standalone — different variant]
│  ├─ nb-4M-02  Derive MLE mean = sample mean     [encompasses: 4M-01a, 4M-01b]
│  │  ├─ nb-4M-01a  Log-likelihood formula
│  │  └─ nb-4M-01b  Log-likelihood reading: "what does MLE maximize?"
│  ├─ nb-5M-01  Log loss formula
│  └─ nb-5M-02  Model comparison (accuracy vs log loss)
│
├─ Level 1 — Conceptual (retrieval of ideas)
│  ├─ Pillar 1: Use Case
│  │  ├─ nb-1C-01   Two properties: fast + strong baseline ✅
│  │  ├─ nb-1C-02a  Generative classifier definition ✅
│  │  ├─ nb-1C-02b  Discriminative classifier definition ✅
│  │  ├─ nb-1C-02c  Generative vs discriminative contrast ✅
│  │  ├─ nb-1C-02d  Example generative ✅
│  │  ├─ nb-1C-02e  Example discriminative ✅
│  │  ├─ nb-1C-03a  When CI works despite violation ✅
│  │  └─ nb-1C-03b  When CI violation breaks NB ✅
│  │
│  ├─ Pillar 2: Data
│  │  ├─ nb-2C-01   Core data assumption (CI given class)
│  │  ├─ nb-2C-02   Feature type → NB variant decision
│  │  └─ nb-2C-03   What var_smoothing does
│  │
│  ├─ Pillar 3: Algorithm
│  │  ├─ nb-3C-01   NB algorithm in 3 steps
│  │  └─ nb-3C-02   Why log trick is necessary
│  │
│  ├─ Pillar 4: Objective
│  │  ├─ nb-4C-01   What fit() computes (counting + averaging)
│  │  ├─ nb-4C-02a  Why NB can't overfit via iteration
│  │  └─ nb-4C-02b  What failure mode NB has instead
│  │
│  └─ Pillar 5: Evaluation
│     ├─ nb-5C-01a  When accuracy is misleading
│     ├─ nb-5C-01b  What metric replaces accuracy (imbalanced)
│     ├─ nb-5C-02a  NB's calibration problem
│     └─ nb-5C-02b  When calibration matters vs doesn't
```

---

## Lesson Sequence

The lesson teaches NB by walking DOWN the tree, then the spaced repetition
system reviews by walking UP (FIRe compression).

```
LESSON ORDER (top-down through pillars, bottom-up through layers):

Session 1 — Conceptual Foundation
  nb-1C-01 → 1C-02a → 1C-02b → 1C-02c → 1C-02d → 1C-02e → 1C-03a → 1C-03b
  nb-2C-01 → 2C-02 → 2C-03
  nb-3C-01 → 3C-02
  nb-4C-01 → 4C-02a → 4C-02b
  nb-5C-01a → 5C-01b → 5C-02a → 5C-02b

Session 2 — Mathematical Layer
  nb-3M-01a → 3M-01b → 3M-01c                    (already calibrated)
  nb-3M-02a → 3M-02b → 3M-02c                    (already calibrated)
  nb-3M-03                                         (integrates 01+02)
  nb-3M-04
  nb-4M-01a → 4M-01b → 4M-02
  nb-5M-01 → 5M-02

Session 3 — Programming: Data Pipeline
  nb-2P-01 → 2P-02 → 2P-03

Session 4 — Programming: Build from Scratch
  nb-3P-01 → 3P-02 → 3P-03                        (this IS the mastery gate)

Session 5 — Programming: Evaluation
  nb-5P-01 → 5P-02

REVIEW ORDER (FIRe compression):
  Schedule mastery gate drill → knocks out 3P, 3M, 3C, 4M, 4C
  Schedule 5P-01 → knocks out 5M-01, 5M-02, 5C-01a
  Schedule 3M-03 → knocks out 3M-01a, 01b, 02a, 02b
  Remaining: 1C, 2C, 2P stand alone (low encompassing)
```

---

## REMAINING CARDS — Rewritten

All cards below apply the 14 confirmed quality rules.
Cards marked ✅ were already calibrated and are shown for completeness only.

---

### Pillar 2: Data — Conceptual

**Q:** What is the core data assumption Naive Bayes makes?
**A:** Conditional independence given the class label.
$P(x_1, x_2, \ldots, x_n \mid y) = \prod_i P(x_i \mid y)$

Reading: "The joint probability of all features given the class equals the product of each feature's individual probability given the class."

Each feature contributes evidence independently, therefore the joint factors into a simple product.
<!--ID: nb-2C-01-->
<!--FIRe: encompassed by nb-3P-01 (w=0.5), nb-3M-01a (w=0.3)-->

---

**Q:** You have a new dataset. How do you decide which NB variant to use?
**A:** Feature type determines variant:
- Continuous features → GaussianNB (models each as bell curve)
- Word counts / frequencies → MultinomialNB (models as count ratios)
- Binary features (0/1) → BernoulliNB (models as coin flips)
<!--ID: nb-2C-02-->
<!--FIRe: standalone-->

---

**Q:** What does sklearn's `var_smoothing` parameter do?
**A:** Adds ε × max(variance) to all feature variances.
Prevents division by zero when a feature has zero variance in one class, therefore stabilizes log-likelihood computation.
<!--ID: nb-2C-03-->
<!--FIRe: encompassed by nb-3P-03 (w=0.8)-->

---

### Pillar 2: Data — Programming

**Q:** Write train/test split for a classification task with imbalanced classes. Why `stratify`?
**A:**
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```
`stratify=y` preserves class proportions in both splits, therefore minority class isn't accidentally absent from test set.
<!--ID: nb-2P-01-->
<!--FIRe: standalone-->

---

**Q:** Write a sklearn Pipeline that scales features and fits GaussianNB.
**A:**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("nb", GaussianNB()),
])
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
```
Pipeline ensures scaling fits on train only, therefore no data leakage.
<!--ID: nb-2P-02-->
<!--FIRe: standalone-->

---

**Q:** Write GridSearchCV to tune GaussianNB's `var_smoothing`.
**A:**
```python
from sklearn.model_selection import GridSearchCV
import numpy as np

param_grid = {"nb__var_smoothing": np.logspace(-12, -1, 20)}

search = GridSearchCV(pipe, param_grid, cv=5, scoring="f1")
search.fit(X_train, y_train)
print(search.best_params_)
```
Log-spaced grid because var_smoothing spans many orders of magnitude.
`nb__` prefix targets the named step inside the Pipeline.
<!--ID: nb-2P-03-->
<!--FIRe: encompasses nb-2C-03 (w=0.4)-->

---

### Pillar 3: Algorithm — Conceptual

**Q:** Describe the Naive Bayes prediction algorithm. No formulas.
**A:** Three steps:
1. **Prior** — count how common each class is
2. **Likelihood** — for each class, learn what each feature typically looks like
3. **Posterior** — for a new sample, multiply prior × all likelihoods per class; predict the class with the highest product

"Which class most likely generated this combination of features?"
<!--ID: nb-3C-01-->
<!--FIRe: encompassed by nb-3P-02 (w=0.7)-->

---

**Q:** Why does NB use log-probabilities instead of raw probabilities?
**A:** Multiplying many small probabilities underflows to 0.0 in floating point, therefore all classes score zero and comparison is impossible.

Log converts products to sums: $\log(a \times b \times c) = \log a + \log b + \log c$.
Sums of negative numbers don't underflow. Argmax is preserved (monotonic transformation).
<!--ID: nb-3C-02-->
<!--FIRe: encompassed by nb-3P-02 (w=0.8)-->

---

### Pillar 3: Algorithm — Mathematical (remaining)

**Q:** Given two classes with these statistics, classify $x_1 = 3$:
- $P(\text{spam}) = 0.4$, $P(\text{ham}) = 0.6$
- $P(x_1 \mid \text{spam})$: $\mu = 5, \sigma^2 = 4$
- $P(x_1 \mid \text{ham})$: $\mu = 2, \sigma^2 = 1$

Compute log-posteriors for both classes. Which wins and why?

**A:**
Spam: $\log P(\text{spam}) + \log \mathcal{N}(3; 5, 4)$
$= \log(0.4) + \log(0.1210) = -0.916 + (-2.112) = -3.028$

Ham: $\log P(\text{ham}) + \log \mathcal{N}(3; 2, 1)$
$= \log(0.6) + \log(0.2420) = -0.511 + (-1.418) = -1.929$

Ham wins ($-1.929 > -3.028$).

Key insight: $x_1 = 3$ is between both means, but ham's tighter variance ($\sigma^2 = 1$) concentrates more density near its mean, therefore ham assigns higher likelihood despite being farther from spam's mean.

| Symbol | Value | Role |
|--------|-------|------|
| $\log P(y)$ | $-0.916$ / $-0.511$ | Log-prior (ham starts ahead) |
| $\log \mathcal{N}(x; \mu, \sigma^2)$ | $-2.112$ / $-1.418$ | Log-likelihood (ham also wins here) |
| Sum | $-3.028$ / $-1.929$ | Log-posterior (higher = winner) |
<!--ID: nb-3M-03-->
<!--FIRe: encompasses nb-3M-01a (w=0.9), nb-3M-01b (w=0.9), nb-3M-02a (w=0.8), nb-3M-02b (w=0.9)-->

---

**Q:** Write the MultinomialNB likelihood formula with Laplace smoothing. Explain each component in plain English.

**A:** $$P(x_i \mid y) = \frac{\text{count}(x_i, y) + \alpha}{\sum_j \text{count}(x_j, y) + \alpha |V|}$$

Reading: "The probability of feature $x_i$ given class $y$ is the smoothed count of $x_i$ in class $y$, divided by the total smoothed count of all features in class $y$."

| Symbol | Name | Meaning |
|--------|------|---------|
| $\text{count}(x_i, y)$ | Feature-class count | Times feature $x_i$ appeared in class $y$ |
| $\alpha$ | Smoothing parameter | Pseudocount added to prevent zero probabilities |
| $\sum_j \text{count}(x_j, y)$ | Class total | Total feature occurrences in class $y$ |
| $\|V\|$ | Vocabulary size | Number of unique features |

Contrast with GaussianNB: this is a ratio of counts (discrete), not a bell curve density (continuous).
<!--ID: nb-3M-04-->
<!--FIRe: standalone (different NB variant)-->

---

### Pillar 3: Algorithm — Programming

**Q:** Implement `fit()` for GaussianNB in numpy. What three statistics does it store?

**A:**
```python
def fit(self, X, y):
    self.classes_ = np.unique(y)
    n_classes = len(self.classes_)
    n_features = X.shape[1]

    self.prior_ = np.zeros(n_classes)
    self.mean_ = np.zeros((n_classes, n_features))
    self.var_ = np.zeros((n_classes, n_features))

    for idx, c in enumerate(self.classes_):
        X_c = X[y == c]
        self.prior_[idx] = X_c.shape[0] / X.shape[0]
        self.mean_[idx] = X_c.mean(axis=0)
        self.var_[idx] = X_c.var(axis=0) + 1e-9
```
Three statistics: prior (class frequency), mean (class-conditional), variance (class-conditional). The `+ 1e-9` is var_smoothing.
<!--ID: nb-3P-01-->
<!--FIRe: encompasses nb-4M-01a (w=0.8), nb-4M-02 (w=0.7), nb-4C-01 (w=0.9), nb-3M-02a (w=0.6), nb-2C-01 (w=0.5), nb-2C-03 (w=0.7)-->

---

**Q:** Implement `_log_posterior()` and `predict()` for GaussianNB in numpy.

**A:**
```python
def _log_posterior(self, X):
    log_post = np.zeros((X.shape[0], len(self.classes_)))
    for idx, c in enumerate(self.classes_):
        log_prior = np.log(self.prior_[idx])
        # Log Gaussian PDF per feature, summed
        log_lik = -0.5 * np.sum(
            np.log(2 * np.pi * self.var_[idx])
            + (X - self.mean_[idx])**2 / self.var_[idx],
            axis=1
        )
        log_post[:, idx] = log_prior + log_lik
    return log_post

def predict(self, X):
    return self.classes_[np.argmax(self._log_posterior(X), axis=1)]
```
The `axis=1` sum is the "naive" product becoming a sum in log-space.
`argmax` over classes selects the winner per sample.
<!--ID: nb-3P-02-->
<!--FIRe: encompasses nb-3M-01a (w=0.9), nb-3M-01b (w=0.9), nb-3M-02a (w=0.9), nb-3C-01 (w=0.7), nb-3C-02 (w=0.8)-->

---

**Q:** There's a subtle bug in GaussianNB: a feature has zero variance in one class. What happens? Fix it.

**A:** $\log(2\pi\sigma^2) = -\infty$ and $(x - \mu)^2 / (2\sigma^2) = \infty/0$. Division by zero crashes or produces NaN.

Fix — add smoothing after computing variances in `fit()`:
```python
self.var_[idx] = X_c.var(axis=0) + 1e-9  # epsilon smoothing
```
Or proportional: `epsilon = 1e-9 * np.max(self.var_); self.var_ += epsilon`

This is exactly what sklearn's `var_smoothing` does.
<!--ID: nb-3P-03-->
<!--FIRe: encompasses nb-2C-03 (w=0.9)-->

---

### Pillar 4: Objective — Conceptual

**Q:** What does NB's `fit()` actually compute? (Don't say "optimize.")

**A:** Counting and averaging in one pass:
- Count samples per class → priors
- Compute mean per feature per class → means
- Compute variance per feature per class → variances

No iteration, no loss minimization. The "best" parameters given the data are computed directly.
<!--ID: nb-4C-01-->
<!--FIRe: encompassed by nb-3P-01 (w=0.9)-->

---

**Q:** Why can't NB overfit by "training too long"?

**A:** No iterations — fit() runs once and computes exact sufficient statistics. There is no training loop to run too many times, therefore no overfitting-via-iteration is possible.
<!--ID: nb-4C-02a-->
<!--FIRe: encompassed by nb-4C-02b (w=0.3) — knowing what fails implies knowing what doesn't-->

---

**Q:** NB can't overfit via iteration. What failure mode does it have instead?

**A:** Underfitting (structural). The conditional independence assumption forces a simpler model than the data warrants, therefore NB misses feature interactions. No amount of data fixes this — it's a model limitation, not a data limitation.

Secondary: small-sample overfitting. If a class has few samples, mean/variance estimates are noisy. Var_smoothing helps here.
<!--ID: nb-4C-02b-->
<!--FIRe: standalone-->

---

### Pillar 4: Objective — Mathematical

**Q:** Write the log-likelihood function for Gaussian Naive Bayes. Explain each component in plain English.

**A:** $$\ell(\theta) = \sum_{i=1}^{n} \left[ \log \pi_{y_i} + \sum_{j=1}^{d} \log \mathcal{N}(x_{ij};\, \mu_{y_i,j},\, \sigma^2_{y_i,j}) \right]$$

Reading: "The log-likelihood is the sum over all samples of: the log-prior of that sample's class, plus the sum over all features of the log-Gaussian-density of that feature given its class parameters."

| Symbol | Name | Meaning |
|--------|------|---------|
| $\ell(\theta)$ | Log-likelihood | Total log-probability of observed data given parameters |
| $\pi_{y_i}$ | Class prior | Frequency of class $y_i$ in training data |
| $\mu_{y_i,j}$ | Class-feature mean | Average of feature $j$ among samples in class $y_i$ |
| $\sigma^2_{y_i,j}$ | Class-feature variance | Spread of feature $j$ among samples in class $y_i$ |
| $\mathcal{N}(x; \mu, \sigma^2)$ | Gaussian density | How likely value $x$ is under that bell curve |

MLE maximizes this over $\theta = \{\pi_c, \mu_{cj}, \sigma^2_{cj}\}$.
<!--ID: nb-4M-01a-->
<!--FIRe: encompassed by nb-4M-02 (w=0.9), nb-3P-01 (w=0.8)-->

---

**Q:** What are the MLE solutions for GaussianNB? What does "MLE = counting and averaging" mean concretely?

**A:**
$$\hat{\pi}_c = \frac{n_c}{n} \qquad \hat{\mu}_{cj} = \frac{1}{n_c}\sum_{i:\,y_i=c} x_{ij} \qquad \hat{\sigma}^2_{cj} = \frac{1}{n_c}\sum_{i:\,y_i=c}(x_{ij} - \hat{\mu}_{cj})^2$$

Reading: "Prior = class frequency. Mean = class-conditional average. Variance = class-conditional spread."

| Parameter | Computation | Plain English |
|-----------|-------------|---------------|
| $\hat{\pi}_c$ | $n_c / n$ | "What fraction of samples belong to class $c$?" |
| $\hat{\mu}_{cj}$ | Sample mean | "What's the average of feature $j$ in class $c$?" |
| $\hat{\sigma}^2_{cj}$ | Sample variance | "How spread out is feature $j$ in class $c$?" |

These are exactly what `fit()` computes. No gradient, no iteration.
<!--ID: nb-4M-01b-->
<!--FIRe: encompassed by nb-4M-02 (w=0.8), nb-3P-01 (w=0.9)-->

---

**Q:** Derive why the MLE estimate for the Gaussian mean is the sample mean. Start from the log-likelihood for one feature in one class.

**A:** For feature $j$ in class $c$:
$$\ell(\mu) = \sum_{i} \left[ -\frac{1}{2}\log(2\pi\sigma^2) - \frac{(x_i - \mu)^2}{2\sigma^2} \right]$$

Take derivative w.r.t. $\mu$:
$$\frac{d\ell}{d\mu} = \sum_i \frac{x_i - \mu}{\sigma^2} = \frac{1}{\sigma^2}\left[\sum_i x_i - n\mu\right]$$

Set to zero:
$$\sum_i x_i - n\mu = 0 \implies \hat{\mu}_{\text{MLE}} = \frac{1}{n}\sum_i x_i = \bar{x}$$

The derivative of the squared term gives sum of residuals. Setting residuals to zero gives the average, therefore MLE = sample mean.
<!--ID: nb-4M-02-->
<!--FIRe: encompasses nb-4M-01a (w=0.9), nb-4M-01b (w=0.8)-->

---

### Pillar 5: Evaluation — Conceptual

**Q:** When is accuracy a misleading metric for NB classification?

**A:** Imbalanced classes. If 90% of samples are class A, a model that always predicts A achieves 90% accuracy, therefore accuracy inflates performance on the majority class and hides failure on the minority class.
<!--ID: nb-5C-01a-->
<!--FIRe: encompassed by nb-5P-01 (w=0.5)-->

---

**Q:** What metrics replace accuracy for imbalanced classification?

**A:** Precision, recall, F1 per class (especially the minority class). Confusion matrix to see which errors dominate. Always report the majority-class baseline to contextualize any metric.
<!--ID: nb-5C-01b-->
<!--FIRe: encompassed by nb-5P-01 (w=0.5)-->

---

**Q:** What calibration problem does NB have?

**A:** Overconfident probabilities. NB pushes predicted probabilities toward 0 and 1 because the CI assumption multiplies likelihoods that are already partially redundant, therefore the posterior is more extreme than the true probability.

Rankings are usually correct (higher score = more likely positive), but absolute values are wrong.
<!--ID: nb-5C-02a-->
<!--FIRe: encompassed by nb-5P-02 (w=0.7)-->

---

**Q:** When does NB's poor calibration matter, and when can you ignore it?

**A:** **Matters:** when you use absolute probabilities for decisions (e.g., "contact fans with >80% buy probability" — the threshold is meaningless if probabilities are inflated).

**Ignore:** when you only use the argmax (class label) or the ranking (top-k most likely). Argmax is preserved, therefore classification accuracy is unaffected.
<!--ID: nb-5C-02b-->
<!--FIRe: encompassed by nb-5P-02 (w=0.6)-->

---

### Pillar 5: Evaluation — Mathematical

**Q:** Write the log loss formula. Explain each component in plain English.

**A:** $$\text{LogLoss} = -\frac{1}{n}\sum_{i=1}^{n}\left[y_i \log(\hat{p}_i) + (1 - y_i)\log(1 - \hat{p}_i)\right]$$

Reading: "Log loss is the average negative log-probability assigned to the true class. Lower = better calibrated probabilities."

| Symbol | Name | Meaning |
|--------|------|---------|
| $y_i$ | True label | 0 or 1 |
| $\hat{p}_i$ | Predicted probability | Model's $P(y=1 \mid x_i)$ |
| $y_i \log(\hat{p}_i)$ | Positive term | Penalizes when $\hat{p}$ is low but $y = 1$ |
| $(1-y_i)\log(1-\hat{p}_i)$ | Negative term | Penalizes when $\hat{p}$ is high but $y = 0$ |

Key property: punishes confident wrong predictions exponentially (log of a near-zero probability → large negative).
<!--ID: nb-5M-01-->
<!--FIRe: encompassed by nb-5P-01 (w=0.7)-->

---

**Q:** Model A: accuracy 85%, log loss 0.45. Model B: accuracy 82%, log loss 0.38. Which is better and when?

**A:** Depends on use case:
- **Need class labels** (e.g., spam/not-spam) → Model A (higher accuracy)
- **Need probability estimates** (e.g., ranking fans by buy likelihood) → Model B (lower log loss = better calibrated)

Log loss 0.38 < 0.45, therefore Model B's probabilities are more honest. In marketing (where you rank and prioritize), calibration usually matters more than accuracy.
<!--ID: nb-5M-02-->
<!--FIRe: encompasses nb-5C-01a (w=0.4)-->

---

### Pillar 5: Evaluation — Programming

**Q:** Write complete evaluation for a trained NB model: confusion matrix, classification report, log loss, cross-validated F1.

**A:**
```python
from sklearn.metrics import (
    confusion_matrix, classification_report, log_loss
)
from sklearn.model_selection import cross_val_score

cm = confusion_matrix(y_test, y_pred)
print(classification_report(y_test, y_pred))

# Log loss needs probabilities, not labels
y_proba = model.predict_proba(X_test)
print(f"Log loss: {log_loss(y_test, y_proba):.4f}")

# Cross-validated F1 (error bars on performance)
cv = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")
print(f"CV F1: {cv.mean():.3f} ± {cv.std():.3f}")
```
Key: `log_loss` takes `predict_proba()`, not `predict()`.
<!--ID: nb-5P-01-->
<!--FIRe: encompasses nb-5M-01 (w=0.7), nb-5M-02 (w=0.5), nb-5C-01a (w=0.5), nb-5C-01b (w=0.4)-->

---

**Q:** Write code to calibrate NB probabilities and compare before/after with a reliability diagram.

**A:**
```python
from sklearn.calibration import (
    CalibratedClassifierCV, calibration_curve
)
import matplotlib.pyplot as plt

cal_nb = CalibratedClassifierCV(model, method="sigmoid", cv=5)
cal_nb.fit(X_train, y_train)

for name, m in [("Raw NB", model), ("Calibrated", cal_nb)]:
    prob = m.predict_proba(X_test)[:, 1]
    frac_pos, mean_pred = calibration_curve(y_test, prob, n_bins=10)
    plt.plot(mean_pred, frac_pos, marker="o", label=name)

plt.plot([0, 1], [0, 1], "k--", label="Perfect")
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of positives")
plt.legend()
```
Perfect calibration follows the diagonal. NB's raw curve is sigmoid-shaped (overconfident).
<!--ID: nb-5P-02-->
<!--FIRe: encompasses nb-5C-02a (w=0.7), nb-5C-02b (w=0.6)-->

---

## Card Census

| Pillar | Conceptual | Mathematical | Programming | Total |
|--------|-----------|-------------|-------------|-------|
| 1. Use Case | 8 ✅ | — | — | 8 |
| 2. Data | 3 🆕 | — | 3 🆕 | 6 |
| 3. Algorithm | 2 🆕 | 4 (1🆕 + 3✅ decomposed) | 3 🆕 | 9 |
| 4. Objective | 3 🆕 | 3 🆕 | (in mastery gate) | 6 |
| 5. Evaluation | 4 🆕 | 2 🆕 | 2 🆕 | 8 |
| **Total** | **20** | **9** | **8** | **37 + 6✅ math = 43** |

Previously calibrated: 14 cards (8 from Pillar 1 + 6 math decompositions)
New rewrites: 29 cards
**Grand total: 43 cards**

---

## Domino Review Schedule

When all cards are active, the scheduler needs at most **4 drills** to
implicitly review the entire deck:

| Drill | Cards explicitly reviewed | Cards implicitly reviewed via FIRe |
|-------|--------------------------|-------------------------------------|
| ⭐ Mastery gate (build class) | 3P-01, 3P-02, 3P-03 | 3M-01a/b, 3M-02a, 3C-01, 3C-02, 4M-01a/b, 4M-02, 4C-01, 4C-02a, 2C-01, 2C-03 |
| nb-3M-03 (full computation) | 3M-03 | 3M-01a, 3M-01b, 3M-02a, 3M-02b |
| nb-5P-01 (eval code) | 5P-01 | 5M-01, 5M-02, 5C-01a, 5C-01b |
| nb-5P-02 (calibration code) | 5P-02 | 5C-02a, 5C-02b |

**Remaining standalone cards** (need their own explicit reviews):
nb-1C-01, 1C-02a-e, 1C-03a/b, 2C-02, 2P-01, 2P-02, 2P-03, 3M-04, 3M-02c, 3M-01c, 4C-02b

That's 4 domino drills + ~13 standalone cards = **17 review items** to cover all 43 cards.
Standard Anki would need 43. FIRe saves ~60% of review load.

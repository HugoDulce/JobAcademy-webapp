---
deck: "JobAcademy::Uncategorized::4-Objective"
tags: [uncategorized, conceptual, explain]
card_id: "nb-4C-02a"
fire_weight: 0.5
notion_last_edited: "2026-02-08T17:05:00.000Z"
concept_node: "NB"
---

# nb-4C-02a

START
Why can't Naive Bayes overfit through too many training iterations?
END

START
There are no iterations.

NB doesn't optimize anything. It directly computes statistics (mean, variance, class frequency) from data in one pass.

No hyperparameters to tune (except var_smoothing), no learning rate, no epochs.

Contrast: Neural nets can overfit by training too long. NB can't — one pass is all it does.
END

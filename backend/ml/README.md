# Review III ML Integration Guide

This module adds ML-based task prioritization using `GradientBoostingRegressor`.

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Train model

From project root:

```bash
python -m backend.ml.train_model
```

This reads:

- `backend/ml/data/task_priority_training.csv`

And writes:

- `backend/ml/model/priority_model.joblib`

## 3) Enable ML in runtime

Set environment values:

```env
USE_ML_PRIORITIZATION=true
ML_MODEL_PATH=backend/ml/model/priority_model.joblib
```

If disabled (or model is missing), API falls back to heuristic prioritization.

## 4) Test endpoint

Call:

- `GET /ai/prioritize`

The endpoint returns tasks sorted by `priority_score`.


import csv
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from .features import FEATURE_NAMES, feature_vector, task_to_feature_map

DATA_FILE = Path(__file__).parent / "data" / "task_priority_training.csv"
MODEL_FILE = Path(__file__).parent / "model" / "priority_model.joblib"


def load_dataset() -> Tuple[List[List[float]], List[float]]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset file not found: {DATA_FILE}")

    X: List[List[float]] = []
    y: List[float] = []

    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "")
            description = row.get("description", "")
            importance = int(row.get("importance", "3"))
            hours_to_deadline = float(row.get("hours_to_deadline", "999"))
            has_deadline = int(row.get("has_deadline", "1"))
            target_priority = float(row.get("target_priority", "3.0"))

            fmap = task_to_feature_map(
                title=title,
                description=description,
                importance=importance,
                hours_to_deadline=hours_to_deadline,
                has_deadline=has_deadline,
            )
            X.append(feature_vector(fmap))
            y.append(target_priority)

    return X, y


def train_and_save() -> None:
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = math.sqrt(sum((p - t) ** 2 for p, t in zip(preds, y_test)) / len(y_test))
    r2 = r2_score(y_test, preds)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {"mae": mae, "rmse": rmse, "r2": r2},
    }
    joblib.dump(artifact, MODEL_FILE)

    print("Model trained successfully.")
    print(f"Saved model to: {MODEL_FILE}")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")


if __name__ == "__main__":
    train_and_save()


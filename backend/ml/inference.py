from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from .. import models
from ..config import ML_MODEL_PATH, USE_ML_PRIORITIZATION
from .features import feature_vector, task_to_feature_map

try:
    import joblib  # type: ignore
except Exception:  # pragma: no cover - safe fallback if dependency missing
    joblib = None


_loaded_model = None
_loaded_model_path: Optional[str] = None


def heuristic_priority(task: models.Task) -> float:
    base = float(task.importance)
    if task.deadline:
        delta_hours = (task.deadline - datetime.utcnow()).total_seconds() / 3600.0
        if delta_hours <= 0:
            base += 5.0
        elif delta_hours <= 24:
            base += 4.0
        elif delta_hours <= 72:
            base += 2.0
        else:
            base += 0.5
    return base


def _load_model():
    global _loaded_model, _loaded_model_path
    if not USE_ML_PRIORITIZATION or joblib is None:
        return None

    if _loaded_model is not None and _loaded_model_path == ML_MODEL_PATH:
        return _loaded_model

    model_path = Path(ML_MODEL_PATH)
    if not model_path.exists():
        return None

    artifact = joblib.load(model_path)
    # Artifact may be either model directly or {"model": ...}
    model = artifact.get("model") if isinstance(artifact, dict) else artifact
    _loaded_model = model
    _loaded_model_path = ML_MODEL_PATH
    return model


def predict_priority(task: models.Task) -> Tuple[float, str]:
    """
    Returns: (priority_score, score_source)
    score_source = "ml" if model is available, else "heuristic".
    """
    model = _load_model()
    if model is None:
        return heuristic_priority(task), "heuristic"

    if task.deadline:
        hours_to_deadline = (task.deadline - datetime.utcnow()).total_seconds() / 3600.0
        has_deadline = 1
    else:
        hours_to_deadline = 999.0
        has_deadline = 0

    fmap = task_to_feature_map(
        title=task.title or "",
        description=task.description or "",
        importance=task.importance or 3,
        hours_to_deadline=hours_to_deadline,
        has_deadline=has_deadline,
    )
    vec = [feature_vector(fmap)]
    score = float(model.predict(vec)[0])
    return score, "ml"


def model_status() -> dict:
    model = _load_model()
    return {
        "use_ml_prioritization": USE_ML_PRIORITIZATION,
        "model_loaded": model is not None,
        "model_path": ML_MODEL_PATH,
        "fallback": "heuristic",
    }


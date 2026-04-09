from typing import Dict, List


FEATURE_NAMES: List[str] = [
    "importance",
    "hours_to_deadline",
    "has_deadline",
    "is_overdue",
    "title_len",
    "description_len",
    "has_keyword_urgent",
    "has_keyword_exam",
    "has_keyword_meeting",
    "has_keyword_project",
]


def _contains(text: str, keyword: str) -> int:
    return 1 if keyword in (text or "").lower() else 0


def task_to_feature_map(
    *,
    title: str,
    description: str,
    importance: int,
    hours_to_deadline: float,
    has_deadline: int,
) -> Dict[str, float]:
    text = f"{title or ''} {description or ''}".lower()
    is_overdue = 1 if has_deadline and hours_to_deadline <= 0 else 0
    clipped_hours = max(-168.0, min(720.0, float(hours_to_deadline)))

    return {
        "importance": float(importance),
        "hours_to_deadline": clipped_hours,
        "has_deadline": float(has_deadline),
        "is_overdue": float(is_overdue),
        "title_len": float(len(title or "")),
        "description_len": float(len(description or "")),
        "has_keyword_urgent": float(_contains(text, "urgent")),
        "has_keyword_exam": float(_contains(text, "exam")),
        "has_keyword_meeting": float(_contains(text, "meeting")),
        "has_keyword_project": float(_contains(text, "project")),
    }


def feature_vector(feature_map: Dict[str, float]) -> List[float]:
    return [feature_map[name] for name in FEATURE_NAMES]


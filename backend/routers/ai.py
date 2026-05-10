from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth_utils import get_current_user
from ..database import get_db
from ..ml.inference import model_status, predict_priority

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/prioritize", response_model=schemas.PrioritizedTaskList)
def prioritize_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return the current user's tasks sorted by priority score.
    Uses ML model when enabled/available, else falls back to heuristic logic.
    """
    tasks: List[models.Task] = (
        db.query(models.Task)
        .filter(models.Task.owner_id == current_user.id)
        .order_by(models.Task.created_at.desc())
        .all()
    )

    prioritized: List[schemas.PrioritizedTask] = []
    for task in tasks:
        score, _source = predict_priority(task)
        prioritized.append(
            schemas.PrioritizedTask(
                id=task.id,
                title=task.title,
                description=task.description,
                deadline=task.deadline,
                importance=task.importance,
                created_at=task.created_at,
                priority_score=score,
            )
        )

    # Sort by score (descending).
    prioritized.sort(key=lambda t: t.priority_score, reverse=True)

    return schemas.PrioritizedTaskList(tasks=prioritized)


@router.get("/model-status")
def get_model_status():
    """
    Simple debug endpoint to show whether ML mode is active and model is loaded.
    """
    return model_status()


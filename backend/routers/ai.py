from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth_utils import get_current_user
from ..database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])


def _compute_priority(task: models.Task) -> float:
    """
    Simple "AI-like" prioritization heuristic.

    Higher score = higher priority.

    - Start with importance (1-5).
    - Add extra points based on how close the deadline is.
    """
    base = float(task.importance)
    if task.deadline:
        now = datetime.utcnow()
        # Number of hours until the deadline (could be negative).
        delta_hours = (task.deadline - now).total_seconds() / 3600.0
        # Tasks overdue or due very soon get a big boost.
        if delta_hours <= 0:
            base += 5.0
        elif delta_hours <= 24:
            base += 4.0
        elif delta_hours <= 72:
            base += 2.0
        else:
            base += 0.5
    return base


@router.get("/prioritize", response_model=schemas.PrioritizedTaskList)
def prioritize_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return the current user's tasks sorted by an AI-like priority score.
    """
    tasks: List[models.Task] = (
        db.query(models.Task)
        .filter(models.Task.owner_id == current_user.id)
        .order_by(models.Task.created_at.desc())
        .all()
    )

    prioritized: List[schemas.PrioritizedTask] = []
    for task in tasks:
        score = _compute_priority(task)
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


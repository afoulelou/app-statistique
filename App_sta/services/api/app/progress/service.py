from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User, UserProgress


def mark_method_progress(
    database: Session, user: User, method_id: str, completion: int, score: float | None = None
) -> UserProgress:
    progress = database.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user.id, UserProgress.method_id == method_id
        )
    )
    if progress is None:
        progress = UserProgress(user_id=user.id, method_id=method_id, completion=completion, score=score)
        database.add(progress)
    else:
        progress.completion = max(progress.completion or 0, completion)
        if score is not None:
            progress.score = score
    return progress

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, Database
from app.db.models import UserProgress
from app.progress.schemas import ProgressResponse, ProgressSummary, ProgressUpdate

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressSummary)
def get_progress(current_user: CurrentUser, database: Database) -> ProgressSummary:
    items = list(
        database.scalars(
            select(UserProgress)
            .where(UserProgress.user_id == current_user.id)
            .order_by(UserProgress.updated_at.desc())
        ).all()
    )
    completions = [item.completion for item in items]
    module_ids = {
        "descriptive": {"mean", "standard_deviation"},
        "inference": {"ttest", "anova", "chi_square", "fisher", "vif", "breusch_pagan"},
        "econometrics": {"ols", "logit", "probit"},
    }
    modules = {
        module: sum(item.completion for item in items if item.method_id in methods) / len(methods)
        for module, methods in module_ids.items()
    }
    return ProgressSummary(
        methods_started=sum(completion > 0 for completion in completions),
        methods_completed=sum(completion == 100 for completion in completions),
        average_completion=(sum(completions) / len(completions)) if completions else 0,
        global_completion=(sum(completions) / len(completions)) if completions else 0,
        items=[ProgressResponse.model_validate(item) for item in items],
        modules=modules,
    )


@router.put("/{method_id}", response_model=ProgressResponse)
def update_progress(
    method_id: str,
    payload: ProgressUpdate,
    current_user: CurrentUser,
    database: Database,
) -> UserProgress:
    progress = database.scalar(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id, UserProgress.method_id == method_id
        )
    )
    if progress is None:
        progress = UserProgress(user_id=current_user.id, method_id=method_id)
        database.add(progress)
    progress.completion = max(progress.completion or 0, payload.completion)
    progress.score = payload.score if payload.score is not None else progress.score
    database.commit()
    database.refresh(progress)
    return progress


@router.get("/{method_id}", response_model=ProgressResponse)
def get_method_progress(
    method_id: str, current_user: CurrentUser, database: Database
) -> UserProgress:
    progress = database.scalar(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id, UserProgress.method_id == method_id
        )
    )
    if progress is None:
        raise HTTPException(status_code=404, detail="Progression introuvable.")
    return progress

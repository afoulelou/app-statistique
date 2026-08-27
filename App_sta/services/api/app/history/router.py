from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, Database
from app.db.models import AnalysisHistory
from app.history.schemas import AnalysisHistoryResponse

router = APIRouter(prefix="/analysis/history", tags=["history"])


@router.get("", response_model=list[AnalysisHistoryResponse])
def list_analysis_history(
    current_user: CurrentUser,
    database: Database,
    limit: int = Query(25, ge=1, le=100),
) -> list[AnalysisHistory]:
    return list(
        database.scalars(
            select(AnalysisHistory)
            .where(AnalysisHistory.user_id == current_user.id)
            .order_by(AnalysisHistory.created_at.desc())
            .limit(limit)
        ).all()
    )


@router.get("/{analysis_id}", response_model=AnalysisHistoryResponse)
def get_analysis_history(
    analysis_id: UUID, current_user: CurrentUser, database: Database
) -> AnalysisHistory:
    analysis = database.scalar(
        select(AnalysisHistory).where(
            AnalysisHistory.id == analysis_id, AnalysisHistory.user_id == current_user.id
        )
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analyse introuvable.")
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis_history(
    analysis_id: UUID, current_user: CurrentUser, database: Database
) -> None:
    analysis = database.scalar(
        select(AnalysisHistory).where(
            AnalysisHistory.id == analysis_id, AnalysisHistory.user_id == current_user.id
        )
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analyse introuvable.")
    database.delete(analysis)
    database.commit()

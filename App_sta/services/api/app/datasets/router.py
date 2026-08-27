from pathlib import Path
from uuid import UUID, uuid4

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser, Database
from app.config import settings
from app.datasets.schemas import DatasetListItem, DatasetPreviewResponse, DatasetResponse
from app.datasets.service import (
    dataframe_preview,
    detect_delimiter,
    detect_encoding,
    read_dataset,
    storage_root,
)
from app.db.models import Dataset, DatasetColumn

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    current_user: CurrentUser,
    database: Database,
    file: UploadFile = File(...),
) -> Dataset:
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(status_code=415, detail="Seuls les fichiers CSV sont acceptes.")

    dataset_id = uuid4()
    destination = storage_root() / f"{current_user.id}_{dataset_id}.csv"
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.dataset_max_bytes:
                    raise HTTPException(status_code=413, detail="Le fichier depasse la taille maximale autorisee.")
                output.write(chunk)
        encoding = detect_encoding(destination)
        delimiter = detect_delimiter(destination, encoding)
        dataframe = read_dataset(destination, encoding, delimiter)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Fichier CSV invalide : {error}") from error

    dataset = Dataset(
        id=dataset_id,
        user_id=current_user.id,
        name=Path(file.filename).name,
        storage_path=str(destination),
        file_size_bytes=size,
        row_count=len(dataframe.index),
        column_count=len(dataframe.columns),
        delimiter=delimiter,
        encoding=encoding,
        columns=[
            DatasetColumn(
                name=str(column),
                position=position,
                data_type=str(dataframe[column].dtype),
                missing_count=int(dataframe[column].isna().sum()),
                unique_count=int(dataframe[column].nunique(dropna=True)),
            )
            for position, column in enumerate(dataframe.columns)
        ],
    )
    database.add(dataset)
    database.commit()
    database.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetListItem])
def list_datasets(current_user: CurrentUser, database: Database) -> list[Dataset]:
    return list(
        database.scalars(
            select(Dataset)
            .where(Dataset.user_id == current_user.id)
            .order_by(Dataset.created_at.desc())
        ).all()
    )


def owned_dataset(dataset_id: UUID, current_user: CurrentUser, database: Database) -> Dataset:
    dataset = database.scalar(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset introuvable.")
    return dataset


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: UUID, current_user: CurrentUser, database: Database) -> Dataset:
    return owned_dataset(dataset_id, current_user, database)


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(
    dataset_id: UUID,
    current_user: CurrentUser,
    database: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
) -> DatasetPreviewResponse:
    dataset = owned_dataset(dataset_id, current_user, database)
    dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        columns=[str(column) for column in dataframe.columns],
        rows=dataframe_preview(dataframe, page, page_size),
        page=page,
        page_size=page_size,
        total_rows=dataset.row_count,
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: UUID, current_user: CurrentUser, database: Database) -> None:
    dataset = owned_dataset(dataset_id, current_user, database)
    Path(dataset.storage_path).unlink(missing_ok=True)
    database.delete(dataset)
    database.commit()

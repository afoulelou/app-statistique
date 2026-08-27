import csv
from pathlib import Path
import pandas as pd

from app.config import settings

ALLOWED_ENCODINGS = ("utf-8", "utf-8-sig", "latin-1")


def storage_root() -> Path:
    root = Path(settings.dataset_storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def detect_encoding(file_path: Path) -> str:
    raw = file_path.read_bytes()[:1_000_000]
    for encoding in ALLOWED_ENCODINGS:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("L'encodage du fichier CSV n'est pas pris en charge.")


def detect_delimiter(file_path: Path, encoding: str) -> str:
    sample = file_path.read_text(encoding=encoding)[:10_000]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_dataset(file_path: Path, encoding: str, delimiter: str) -> pd.DataFrame:
    dataframe = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
    if dataframe.columns.empty or any(not str(column).strip() for column in dataframe.columns):
        raise ValueError("Le fichier CSV doit contenir des noms de colonnes valides.")
    if dataframe.columns.duplicated().any():
        raise ValueError("Le fichier CSV ne doit pas contenir de noms de colonnes dupliques.")
    if len(dataframe.index) > settings.dataset_max_rows:
        raise ValueError(f"Le fichier depasse la limite de {settings.dataset_max_rows} lignes.")
    return dataframe


def json_value(value: object) -> object:
    if pd.isna(value):  # type: ignore[call-overload]
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def dataframe_preview(dataframe: pd.DataFrame, page: int, page_size: int) -> list[dict[str, object]]:
    start = (page - 1) * page_size
    return [
        {str(key): json_value(value) for key, value in row.items()}
        for row in dataframe.iloc[start : start + page_size].to_dict(orient="records")
    ]

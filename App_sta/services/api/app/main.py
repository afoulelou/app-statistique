from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.auth.router import router as auth_router
from app.auth.router import users_router
from app.config import settings
from app.datasets.router import router as datasets_router
from app.statistics.router import router as statistics_router
from app.statistics.tests_router import router as tests_router
from app.statistics.anova_router import router as anova_router
from app.statistics.association_router import router as association_router
from app.statistics.diagnostic_router import router as diagnostic_router
from app.statistics.regression_router import router as regression_router
from app.statistics.binary_router import router as binary_router
from app.history.router import router as history_router
from app.content.router import router as content_router
from app.progress.router import router as progress_router


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

app = FastAPI(
    title="App Statistique API",
    description="API pedagogique pour l'apprentissage et l'analyse statistique.",
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-statistique.vercel.app",
        "https://app-statistique-git-main-afou.vercel.app",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(datasets_router)
app.include_router(statistics_router)
app.include_router(tests_router)
app.include_router(anova_router)
app.include_router(association_router)
app.include_router(diagnostic_router)
app.include_router(regression_router)
app.include_router(binary_router)
app.include_router(history_router)
app.include_router(content_router)
app.include_router(progress_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api", version=settings.api_version)

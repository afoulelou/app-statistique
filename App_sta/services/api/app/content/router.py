from fastapi import APIRouter, HTTPException

from app.content.catalog import CATALOG, all_methods
from app.content.schemas import MethodResponse, ModuleResponse

router = APIRouter(tags=["content"])


@router.get("/modules", response_model=list[ModuleResponse])
def list_modules() -> list[ModuleResponse]:
    return [ModuleResponse.model_validate(module) for module in CATALOG]


@router.get("/modules/{module_id}", response_model=ModuleResponse)
def get_module(module_id: str) -> ModuleResponse:
    module = next((item for item in CATALOG if item["id"] == module_id), None)
    if module is None:
        raise HTTPException(status_code=404, detail="Module introuvable.")
    return ModuleResponse.model_validate(module)


@router.get("/methods", response_model=list[MethodResponse])
def list_methods() -> list[MethodResponse]:
    return [MethodResponse.model_validate(method) for method in all_methods()]


@router.get("/methods/{method_id}", response_model=MethodResponse)
def get_method(method_id: str) -> MethodResponse:
    method = next((item for item in all_methods() if item["id"] == method_id), None)
    if method is None:
        raise HTTPException(status_code=404, detail="Methode introuvable.")
    return MethodResponse.model_validate(method)

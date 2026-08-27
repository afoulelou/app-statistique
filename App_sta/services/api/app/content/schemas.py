from pydantic import BaseModel


class CommandResponse(BaseModel):
    software: str
    command: str


class MethodResponse(BaseModel):
    id: str
    name: str
    definition: str
    formula: str
    utility: str
    conditions: list[str]
    example: str
    commands: list[CommandResponse]


class ModuleResponse(BaseModel):
    id: str
    name: str
    description: str
    methods: list[MethodResponse]

from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from uuid import UUID
import re

class ClientBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    cpf: str = Field(..., description="Apenas os 11 dígitos do CPF")
    birth_date: date
    phone: str

    @field_validator('cpf')
    @classmethod
    def validate_cpf_format(cls, v: str) -> str:
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('O CPF deve conter exatamente 11 dígitos numéricos')
        return cpf

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None

class ClientResponse(ClientBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
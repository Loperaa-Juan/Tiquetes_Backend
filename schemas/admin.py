from uuid import UUID
import re
import pydantic as _pydantic
from pydantic import field_validator


class _AdminBase(_pydantic.BaseModel):
    identificacion: str
    nombres: str
    apellidos: str
    telefono: str
    cargo: str
    empresa: str
    email: str


class AdminCreate(_AdminBase):
    hashed_password: str

    @field_validator("hashed_password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "La contraseña debe contener al menos una letra mayúscula."
            )
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "La contraseña debe contener al menos una letra minúscula."
            )
        if not re.search(r"[0-9]", value):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial."
            )
        return value

    model_config = _pydantic.ConfigDict(from_attributes=True)


class Admin(_AdminBase):
    administrador_id: UUID

    model_config = _pydantic.ConfigDict(from_attributes=True)

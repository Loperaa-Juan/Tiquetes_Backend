import re
from uuid import UUID

import pydantic as _pydantic
from pydantic import field_validator


class _EstudianteBase(_pydantic.BaseModel):
    tipo_identificacion: str
    identificacion: str
    nombres: str
    apellidos: str
    institucion: str
    telefono: str
    direccion: str
    email: str


class EstudianteCreate(_EstudianteBase):
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


class Estudiante(_EstudianteBase):
    estudiante_id: UUID
    codigo_QR: str

    model_config = _pydantic.ConfigDict(from_attributes=True)

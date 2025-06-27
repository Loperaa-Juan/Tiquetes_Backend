import datetime as _dt
from uuid import UUID
import pydantic as _pydantic

class _ViajeBase(_pydantic.BaseModel):
    estudiante_id: UUID
    administrador_id: UUID

class ViajeCreate(_ViajeBase):
    pass

class Viaje(_ViajeBase):
    viaje_id: UUID
    fecha_viaje: str
    hora: str
    estudiante_id: UUID
    administrador_id: UUID
    fecha_creacion: _dt.datetime
    activo: bool

    model_config = _pydantic.ConfigDict(from_attributes=True)
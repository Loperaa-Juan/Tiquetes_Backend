import datetime as _dt
from uuid import uuid4 as _uuid4
import database as _database
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from passlib.context import CryptContext 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Estudiante(_database.Base):
    __tablename__ = "estudiante"

    estudiante_id = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid4)
    tipo_identificacion = _sql.Column(_sql.String, nullable=False)
    identificacion = _sql.Column(_sql.String, unique=True, nullable=False, index=True)
    nombres = _sql.Column(_sql.String, nullable=False)
    apellidos = _sql.Column(_sql.String, nullable=False)
    institucion = _sql.Column(_sql.String, nullable=False)
    telefono = _sql.Column(_sql.String, nullable=False)
    direccion = _sql.Column(_sql.String, nullable=False)
    email = _sql.Column(_sql.String, unique=True, nullable=False)
    hashed_password = _sql.Column(_sql.String, nullable=False)
    numero_tiquetes = _sql.Column(_sql.Integer, default=0, nullable=False)
    numero_viajes = _sql.Column(_sql.Integer, default=0, nullable=False)
    codigoQR = _sql.Column(_sql.String, nullable=False)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True, nullable=False)
    actualiza = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow, onupdate=_dt.datetime.utcnow)

    viaje = _orm.relationship("Viaje", back_populates="estudiante")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
class Administrador(_database.Base):
    __tablename__ = "administrador"

    administrador_id = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid4)
    identificacion = _sql.Column(_sql.String, unique=True, nullable=False, index=True)
    nombres = _sql.Column(_sql.String, nullable=False)
    apellidos = _sql.Column(_sql.String, nullable=False)
    telefono = _sql.Column(_sql.String, nullable=False)
    cargo = _sql.Column(_sql.String, nullable=False)
    empresa = _sql.Column(_sql.String, nullable=False)
    email = _sql.Column(_sql.String, unique=True, nullable=False)
    hashed_password = _sql.Column(_sql.String, nullable=False)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True, nullable=False)
    actualiza = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow, onupdate=_dt.datetime.utcnow)

    viaje = _orm.relationship("Viaje", back_populates="administrador")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

class Viaje(_database.Base):
    __tablename__ = "viaje"

    viaje_id = _sql.Column(UUID(as_uuid=True), primary_key=True, default=_uuid4)
    fecha_viaje = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    hora = _sql.Column(_sql.Time, nullable=False, default=lambda: _dt.datetime.utcnow().time())
    estudiante_id = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("estudiante.estudiante_id"), nullable=False)
    administrador_id = _sql.Column(UUID(as_uuid=True), _sql.ForeignKey("administrador.administrador_id"), nullable=False)
    fecha_creacion = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    activo = _sql.Column(_sql.Boolean, default=True, nullable=False)
    actualiza = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow, onupdate=_dt.datetime.utcnow)

    estudiante = _orm.relationship("Estudiante", back_populates="viaje")
    administrador = _orm.relationship("Administrador", back_populates="viaje")
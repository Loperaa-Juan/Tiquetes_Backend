import io

import qrcode

# Import the ORM since sqlalchemy
import sqlalchemy.orm as _orm

# Import the dotenv library to work with enviromental variables
from dotenv import load_dotenv
from fastapi import HTTPException
from passlib.context import CryptContext

import models as _models
from schemas import admin as _admin
from schemas import estudiante as _student

# Create the context for the bcrypt's hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()


async def create_student(student: _student.EstudianteCreate, db: _orm.session):
    qr_data = student.identificacion

    qr = qrcode.make(data=qr_data)
    qr_byte_array = io.BytesIO()
    qr.save(qr_byte_array, format="PNG")
    qr_byte_array = qr_byte_array.getvalue()

    student_obj = _models.Estudiante(
        tipo_identificacion=student.tipo_identificacion,
        identificacion=student.identificacion,
        nombres=student.nombres,
        apellidos=student.apellidos,
        institucion=student.institucion,
        telefono=student.telefono,
        direccion=student.direccion,
        email=student.email,
        hashed_password=pwd_context.hash(student.hashed_password),
        codigoQR=qr_byte_array,
    )

    db.add(student_obj)
    db.commit()
    db.refresh(student_obj)
    return student_obj


async def get_user_by_identificacion(
    identificacion: str, db: _orm.session, admin: _admin.Admin
):
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return (
        db.query(_models.Estudiante)
        .filter(_models.Estudiante.identificacion == identificacion)
        .first()
    )


async def get_all_students(db: _orm.session, admin: _admin.Admin):
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(_models.Estudiante).all()


def update_tickets(
    student_identification: str,
    tickets_number: int,
    db: _orm.session,
    admin: _admin.Admin,
):
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not student_identification:
        raise HTTPException(
            status_code=400, detail="Identificacion del estudiante es requerida"
        )
    if tickets_number < 0:
        raise HTTPException(
            status_code=400, detail="El numero de tiquetes debe ser mayor o igual a 0"
        )

    estudiante = (
        db.query(_models.Estudiante)
        .filter(_models.Estudiante.identificacion == student_identification)
        .first()
    )

    if estudiante is None:
        HTTPException(
            status_code=404,
            detail=f"El estudiante con id {student_identification} no se encuentra registrado",
        )

    estudiante.numero_tiquetes = tickets_number
    estudiante.numero_viajes = 0
    db.commit()
    db.refresh(estudiante)

    return estudiante


def discount_ticket(student_identification: str, db: _orm.session, admin: _admin.Admin):
    estudiante = (
        db.query(_models.Estudiante)
        .filter(_models.Estudiante.identificacion == student_identification)
        .first()
    )

    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not student_identification:
        raise HTTPException(
            status_code=400, detail="Identificacion del estudiante es requerida"
        )

    if estudiante is None:
        HTTPException(
            status_code=404,
            detail=f"El estudiante con id {student_identification} no se encuentra registrado",
        )

    if estudiante.numero_tiquetes <= 0:
        raise HTTPException(
            status_code=400,
            detail="El estudiante no tiene tiquetes disponibles para descontar",
        )

    # Añadimos un registro de viaje
    viaje_obj = _models.Viaje(
        estudiante_id=estudiante.estudiante_id, administrador_id=admin.administrador_id
    )

    db.add(viaje_obj)

    estudiante.numero_tiquetes = estudiante.numero_tiquetes - 1
    estudiante.numero_viajes = estudiante.numero_viajes + 1

    db.commit()
    db.refresh(viaje_obj)
    db.refresh(estudiante)
    return estudiante


def delete_student(student_identification: str, db: _orm.session, admin: _admin.Admin):
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not student_identification:
        raise HTTPException(
            status_code=400, detail="Identificacion del estudiante es requerida"
        )

    estudiante = (
        db.query(_models.Estudiante)
        .filter(_models.Estudiante.identificacion == student_identification)
        .first()
    )
    if estudiante is None:
        HTTPException(
            status_code=404,
            detail=f"El estudiante con id {student_identification} no se encuentra registrado",
        )

    db.delete(estudiante)
    db.commit()

    return {
        "Detail": f"El estudiante con identificacion {estudiante.identificacion} y nombre {estudiante.nombres + ' ' + estudiante.apellidos} fue eliminado correctamente"
    }

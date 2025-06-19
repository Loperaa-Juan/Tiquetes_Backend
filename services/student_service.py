import fastapi.security as _security
from fastapi import HTTPException, Depends

# Import the dotenv library to work with enviromental variables
from dotenv import load_dotenv

# Import the ORM since sqlalchemy
import sqlalchemy.orm as _orm
import os
import io
import qrcode

from passlib.context import CryptContext

import models as _models
from schemas import estudiante as _student

# Create the context for the bcrypt's hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

async def create_student(student: _student.EstudianteCreate, db: _orm.session):
    qr_data = student.identificacion

    qr = qrcode.make(data=qr_data)
    qr_byte_array = io.BytesIO()
    qr.save(qr_byte_array, format='PNG')
    qr_byte_array = qr_byte_array.getvalue()

    student_obj = _models.Estudiante(
        identificacion= student.identificacion,
        nombres = student.nombres,
        apellidos = student.apellidos,
        institucion = student.institucion,
        telefono = student.telefono,
        direccion = student.direccion,
        email = student.email,
        hashed_password = pwd_context.hash(student.hashed_password),
        codigoQR = qr_byte_array
    )

    db.add(student_obj)
    db.commit()
    db.refresh(student_obj)
    return student_obj

# TODO: Incorporar validación, solo un administrador puede ver el perfil de un estudiante
async def get_user_by_identificacion(identificacion: str, db: _orm.session):
    return db.query(_models.Estudiante).filter(_models.Estudiante.identificacion == identificacion).first()

# TODO: Incorporar validación, solo un administrador debe acceder a este listado
async def get_all_students(db: _orm.session):
    return db.query(_models.Estudiante).all()

def update_tickets(student_identification: str, tickets_number: int, db: _orm.session):
    estudiante = db.query(_models.Estudiante).filter(_models.Estudiante.identificacion == student_identification).first()
    
    if estudiante is None:
        HTTPException(status_code=404, detail=f"El estudiante con id {student_identification} no se encuentra registrado") 

    estudiante.numero_tiquetes = tickets_number
    db.commit()
    db.refresh(estudiante)
       
    return estudiante

def discount_ticket(student_identification: str, db: _orm.session):
    estudiante = db.query(_models.Estudiante).filter(_models.Estudiante.identificacion == student_identification).first()
    if estudiante is None:
        HTTPException(status_code=404, detail=f"El estudiante con id {student_identification} no se encuentra registrado")
    
    estudiante.numero_tiquetes = estudiante.numero_tiquetes - 1
    db.commit()
    db.refresh(estudiante)
    return estudiante

def delete_student(student_identification: str, db: _orm.session):
    estudiante = db.query(_models.Estudiante).filter(_models.Estudiante.identificacion == student_identification).first()
    if estudiante is None:
        HTTPException(status_code=404, detail=f"El estudiante con id {student_identification} no se encuentra registrado")
    
    db.delete(estudiante)
    db.commit()

    return {
        "Detail" : f"Estudiante con identificacion {estudiante.identificacion} y nombre {estudiante.nombres} eliminado correctamente"
    }
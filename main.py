from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

import sqlalchemy.orm as _orm

import schemas.admin as _admin
import schemas.estudiante as _estudiante
import schemas.viajes as _viajes

import services.database as _databaseServices
import services.student_service as _studentService
import services.admin_services as _adminServices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints para la creación de estudiantes
@app.post('/api/v1/students', tags=["Estudiante"])
async def create_student(
    student: _estudiante.EstudianteCreate,
    db: _orm.session = Depends(_databaseServices.get_db)
):
    user = await _studentService.create_student(student=student, db=db)
    return user

@app.get("/api/v1/students/{identificacion}", tags=["Estudiante"])
async def get_user_by_id(
    identificacion: str,
    db: _orm.session = Depends( _databaseServices.get_db )
):
    student = await _studentService.get_user_by_identificacion(db=db, identificacion=identificacion)

    if student is None:
        raise HTTPException(status_code=404, detail="El estudiante no se encuentra registrado")
    
    return student

@app.get("/api/v1/estudiantes", tags=["Estudiante"])
async def get_students(db: _orm.session = Depends(_databaseServices.get_db)):
    estudiantes = await _studentService.get_all_students(db=db)
    return estudiantes

@app.put("/api/v1/estudiantes/tickets/{identification}", tags=["Estudiante"])
def update_tickets(
    student_id: str,
    tickets: int,
    db: _orm.session = Depends(_databaseServices.get_db)
):
    estudiante = _studentService.update_tickets(db=db, student_identification=student_id, tickets_number=tickets)
    return estudiante

@app.put("/api/v1/estudiantes/tickets/delete/{identificacion}", tags=["Estudiante"])
def discount_ticket(
    identification: str,
    db: _orm.session = Depends( _databaseServices.get_db )
):
    estudiante = _studentService.discount_ticket(student_identification=identification, db=db)
    return estudiante

@app.delete("/api/v1/estudiantes", tags=["Estudiante"])
def delete_student(
    identification: str,
    db: _orm.session = Depends( _databaseServices.get_db )
):
    estudiante = _studentService.delete_student(student_identification=identification, db=db)
    return estudiante
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

import sqlalchemy.orm as _orm

import schemas.admin as _admin
import schemas.estudiante as _estudiante

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

@app.post("/api/v1/token", tags=["Login"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: _orm.Session = Depends(_databaseServices.get_db)):
    user = await _adminServices.authenticate_admin(form_data.username, form_data.password, db)

    access_token_expires = timedelta(minutes=30)
    access_token_jwt = _adminServices.create_token({"sub": str(user.administrador_id), "id": user.identificacion}, access_token_expires)

    return {
        "access_token": access_token_jwt,
        "token_type": "bearer"
    }

# Endpoints para la creación de estudiantes
@app.post('/api/v1/estudiantes', tags=["Estudiante"])
async def create_student(
    student: _estudiante.EstudianteCreate,
    user: _estudiante.Estudiante = Depends(_adminServices.get_current_user),
    db: _orm.session = Depends(_databaseServices.get_db)
):
    user = await _studentService.create_student(student=student, db=db)
    return user

@app.get("/api/v1/estudiantes/{identificacion}", tags=["Estudiante"])
async def get_user_by_id(
    identificacion: str,
    user: _estudiante.Estudiante = Depends(_adminServices.get_current_user),
    db: _orm.session = Depends( _databaseServices.get_db )
):
    student = await _studentService.get_user_by_identificacion(db=db, identificacion=identificacion, admin=user)

    if student is None:
        raise HTTPException(status_code=404, detail="El estudiante no se encuentra registrado")
    
    return student

@app.get("/api/v1/estudiantes", tags=["Estudiante"])
async def get_students(db: _orm.session = Depends(_databaseServices.get_db), user: _estudiante.Estudiante = Depends(_adminServices.get_current_user)):
    estudiantes = await _studentService.get_all_students(db=db, admin=user)
    return estudiantes

@app.put("/api/v1/estudiantes/tickets/{identification}", tags=["Estudiante"])
def update_tickets(
    student_id: str,
    tickets: int,
    db: _orm.session = Depends(_databaseServices.get_db),
    user: _estudiante.Estudiante = Depends(_adminServices.get_current_user)
):
    estudiante = _studentService.update_tickets(db=db, student_identification=student_id, tickets_number=tickets, admin=user)
    return estudiante

@app.put("/api/v1/estudiantes/tickets/delete/{identificacion}", tags=["Estudiante"])
def discount_ticket(
    identification: str,
    db: _orm.session = Depends( _databaseServices.get_db ),
    user: _estudiante.Estudiante = Depends(_adminServices.get_current_user)
):
    estudiante = _studentService.discount_ticket(student_identification=identification, db=db, admin=user)
    return estudiante

@app.delete("/api/v1/estudiantes", tags=["Estudiante"])
def delete_student(
    identification: str,
    db: _orm.session = Depends( _databaseServices.get_db ),
    user: _estudiante.Estudiante = Depends(_adminServices.get_current_user)
):
    estudiante = _studentService.delete_student(student_identification=identification, db=db, admin=user)
    return estudiante

# Endpoints para la creación de administradores
@app.post('/api/v1/administrador', tags=["Administrador"])
async def create_admin(
    admin: _admin.AdminCreate,
    db: _orm.session = Depends(_databaseServices.get_db),
    user: _admin.Admin = Depends(_adminServices.get_current_user)
):
    user = await _adminServices.create_admin(admin= admin, db=db, admin_user=user)
    return user

@app.delete('/api/v1/administrador', tags=["Administrador"])
async def delete_admin(
    admin_id: str,
    db: _orm.session = Depends(_databaseServices.get_db),
    user: _admin.Admin = Depends(_adminServices.get_current_user)
):
    admin_deleted = await _adminServices.delete_admin(admin_identification=admin_id, admin=user, db=db)
    return admin_deleted
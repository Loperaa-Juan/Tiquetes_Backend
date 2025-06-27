from fastapi import Depends, HTTPException
import sqlalchemy.orm as _orm
import models as _models
import os
from dotenv import load_dotenv

import services.database as _databaseServices

from passlib.context import CryptContext

from typing import Union
from datetime import datetime, timedelta

from jose import JWTError, jwt

import schemas.admin as _admin

import fastapi.security as _security

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET = os.getenv("JWT_SECRET")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OAuth2_scheme = _security.OAuth2PasswordBearer("/api/v1/token")


async def get_current_user(
    db: _orm.Session = Depends(_databaseServices.get_db),
    token: str = Depends(OAuth2_scheme),
):
    try:
        token_decode = jwt.decode(token, key=JWT_SECRET, algorithms=[ALGORITHM])
        user_id = token_decode.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = (
            db.query(_models.Administrador)
            .filter(_models.Administrador.identificacion == user_id)
            .first()
        )
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def create_admin(
    admin: _admin.AdminCreate,
    db: _orm.session,
    admin_user: _admin.Admin = Depends(get_current_user),
):
    if not admin_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized, only administrators can create new admins",
        )

    admin_obj = _models.Administrador(
        identificacion=admin.identificacion,
        nombres=admin.nombres,
        apellidos=admin.apellidos,
        telefono=admin.telefono,
        cargo=admin.cargo,
        empresa=admin.empresa,
        email=admin.email,
        hashed_password=pwd_context.hash(admin.hashed_password),
    )

    db.add(admin_obj)
    db.commit()
    db.refresh(admin_obj)
    return admin_obj


async def delete_admin(
    admin_identification: str, db: _orm.session, admin: _admin.Admin
):
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")

    administrador = await get_admin_by_identification(id=admin_identification, db=db)

    if not administrador:
        raise HTTPException(
            status_code=404,
            detail=f"El administrador con idenficación {admin_identification} no se encuentra registrada",
        )

    db.delete(administrador)
    db.commit()

    return {
        "detail": f"Administrador con identificación {administrador.identificacion} y nombre {administrador.nombres + ' ' + administrador.apellidos} fue eliminado exitosamente."
    }


async def get_admin_by_identification(id: str, db: _orm.session):
    return (
        db.query(_models.Administrador)
        .filter(_models.Administrador.identificacion == id)
        .first()
    )


async def authenticate_admin(
    admin_identification: str, password: str, db: _orm.session
):
    user = await get_admin_by_identification(id=admin_identification, db=db)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.verify_password(password):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def create_token(data: dict, time_expire: Union[datetime, None] = None):
    data_copy = data.copy()

    if time_expire is None:
        expires = datetime.utcnow() + timedelta(minutes=15)
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=JWT_SECRET, algorithm=ALGORITHM)

    return token_jwt


async def edit_admin(
    admin: _admin.AdminCreate,
    db: _orm.session,
    admin_user: _admin.Admin = Depends(get_current_user),
):
    if not admin_user:
        raise HTTPException(
            status_code=401, detail="Unauthorized, only administrators can edit admins"
        )

    administrador = await get_admin_by_identification(id=admin.identificacion, db=db)

    if not administrador:
        raise HTTPException(
            status_code=404,
            detail=f"El administrador con identificación {admin.identificacion} no se encuentra registrado",
        )

    if administrador.nombres:
        administrador.nombres = admin.nombres
    if administrador.apellidos:
        administrador.apellidos = admin.apellidos
    if administrador.telefono:
        administrador.telefono = admin.telefono
    if administrador.cargo:
        administrador.cargo = admin.cargo
    administrador.empresa = admin.empresa
    administrador.email = admin.email

    if admin.hashed_password:
        administrador.hashed_password = pwd_context.hash(admin.hashed_password)

    db.commit()
    db.refresh(administrador)

    return administrador

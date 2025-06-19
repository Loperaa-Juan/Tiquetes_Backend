import sqlalchemy.orm as _orm
import models as _models
import os
from dotenv import load_dotenv

import fastapi.security as _security

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET = os.getenv("JWT_SECRET")
OAuth2_scheme = _security.OAuth2PasswordBearer("/api/v1/token")

async def get_admin_by_identification(id: str, db:_orm.session):
    return db.query(_models.Administrador).filter(_models.Administrador.identificacion == id).first()
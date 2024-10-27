from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models import Roles
from starlette import status

from app.database import get_db

roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db_session: Session = Depends(get_db)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    all_todos = db_session.exec(select(Roles)).all()
    return {"todos": all_todos} #Devuelve
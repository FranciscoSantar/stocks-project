from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models import AssetsType
from starlette import status

from app.database import get_db

assets_types_router = APIRouter(prefix="/assets-types", tags=["assets-types"])


@assets_types_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db_session: Session = Depends(get_db)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    all_todos = db_session.exec(select(AssetsType)).all()
    return {"todos": all_todos} #Devuelve
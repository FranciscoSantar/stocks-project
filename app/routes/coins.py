from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models import Coins
from app.database import get_db
from starlette import status

coins_router = APIRouter(prefix="/coins", tags=["coins"])

@coins_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db_session: Session = Depends(get_db)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    all_todos = db_session.exec(select(Coins)).all()
    return {"todos": all_todos} #Devuelve
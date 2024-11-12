from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.controllers.coins_controller import CoinsController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
coins_router = APIRouter(prefix="/coins", tags=["coins"])

@coins_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_coins(db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user), page_number:int | None = 1, items_per_page:int | None = 10): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    
    coins = CoinsController().get_coins(page_number=page_number, items_per_page=items_per_page, db_session=db_session)
    return {"coins": coins}


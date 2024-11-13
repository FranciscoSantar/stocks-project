from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.controllers.coins_controller import CoinsController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
coins_router = APIRouter(prefix="/coins", tags=["coins"])

@coins_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_coins(db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user), page_number:int | None =Query(default=1, gt=0), items_per_page:int | None = Query(default=10, le=100)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    coins = CoinsController().get_coins(page_number=page_number, items_per_page=items_per_page, db_session=db_session)
    return {"coins": coins}


@coins_router.get("/{coin_id}", status_code=status.HTTP_200_OK)
async def get_coin_by_id(db_session: Session = Depends(get_db), user : dict = Depends(AuthController().get_current_user), coin_id:int = Path(gt=0)):
    coin = CoinsController().get_coin_by_id(coin_id=coin_id, db=db_session)
    return {"coin": coin}



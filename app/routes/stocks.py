from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.controllers.stocks_controlller import StocksController
from app.database import get_db
from starlette import status

stocks_router = APIRouter(prefix="/stocks", tags=["stocks"])

@stocks_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_stocks(db_session: Session = Depends(get_db), page_number:int | None = 1, items_per_page:int | None = 10): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    stocks = StocksController().get_stocks(page_number=page_number, items_per_page=items_per_page, db_session=db_session)
    return {"stocks": stocks}

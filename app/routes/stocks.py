from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from app.controllers.auth_controller import AuthController
from app.controllers.stocks_controlller import StocksController
from app.database import get_db
from starlette import status

stocks_router = APIRouter(prefix="/stocks", tags=["stocks"])

@stocks_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_stocks(db_session: Session = Depends(get_db), user : dict = Depends(AuthController().get_current_user), page_number:int | None =Query(default=1, gt=0), items_per_page:int | None = Query(default=10, le=100)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    stocks = StocksController().get_all_stocks(page_number=page_number, items_per_page=items_per_page, db=db_session)
    return {"stocks": stocks}

@stocks_router.get("/{stock_id}", status_code=status.HTTP_200_OK)
async def get_stock_by_id(db_session: Session = Depends(get_db), user : dict = Depends(AuthController().get_current_user), stock_id:int = Path(gt=0)):
    stock = StocksController().get_stock_by_id(stock_id=stock_id, db=db_session)
    return {"stock": stock}


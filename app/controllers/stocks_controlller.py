from sqlmodel import Session, select
from app.models import Stocks
from fastapi import HTTPException
class StocksController():

    def __init__(self):
        self.model=Stocks

    def get_all_stocks(self, page_number:int, items_per_page:int, db:Session):
        return db.exec(select(self.model).offset((page_number - 1) * items_per_page).limit(items_per_page)).all()

    def get_stock_by_id(self, stock_id:int, db:Session):
        stock = db.exec(select(self.model).where(self.model.id == stock_id)).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock no encontrado.")
        return stock
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
    
    def get_stock_by_asset_id(self, asset_id:int, db:Session):
        query = select(self.model).where(self.model.asset_id == asset_id)
        stock = db.exec(query).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock no encontrado.")
        return stock
    
    def get_stock_name_by_asset_id(self, asset_id:int, db:Session):
        query = select(self.model.name).where(self.model.asset_id == asset_id)
        name = db.exec(query).first()
        if not name:
            raise HTTPException(status_code=404, detail="Stock no encontrado.")
        return name
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import Coins
class CoinsController():

    def __init__(self):
        self.model = Coins

    def get_coins(self, page_number:int, items_per_page:int, db_session:Session):
        coins = db_session.exec(select(Coins).offset((page_number - 1) * items_per_page).limit(items_per_page)).all()
        return coins
    
    def get_coin_by_id(self, coin_id:int, db:Session):
        coin = db.exec(select(self.model).where(self.model.id == coin_id)).first()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin no encontrado.")
        return coin
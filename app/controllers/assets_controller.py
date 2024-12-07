from fastapi import HTTPException
from sqlmodel import Session, select
from app.controllers.coingecko_controller import CoingeckoController
from app.controllers.coins_controller import CoinsController
from app.controllers.fmp_controller import FMPController
from app.controllers.stocks_controlller import StocksController
from app.models import Assets

class AssetsController():

    def __init__(self):
        self.model = Assets

    def get_type_by_asset_id(self, asset_id:int, db:Session) -> str:
        query = select(self.model).where(self.model.id == asset_id)
        asset = db.exec(query).first()
        if not asset:
            return None
        return asset.asset_type.type

    def get_asset_by_id(self, asset_id:int, db:Session) -> Assets:
        query = select(self.model).where(self.model.id == asset_id)
        asset = db.exec(query).first()
        if not asset:
            return None
        return asset

    def get_asset_price_by_id(self, asset_id:int, db:Session):
        asset_type = self.get_type_by_asset_id(asset_id=asset_id, db=db)
        if asset_type == 'stock':
            stock = StocksController().get_stock_by_asset_id(asset_id=asset_id, db=db)
            current_price = FMPController().get_stock_current_price(symbol=stock.symbol)
        else:
            coin = CoinsController().get_coin_by_asset_id(db=db, asset_id=asset_id)
            current_price = CoingeckoController().get_only_current_coin_price_by_name(name=coin.name)
        return current_price
    
    def get_asset_name_by_id(self, asset_id:int, db:Session) -> str:
        asset_type = self.get_type_by_asset_id(asset_id=asset_id, db=db)
        if asset_type == 'stock':
            name = StocksController().get_stock_name_by_asset_id(asset_id=asset_id, db=db)
        else:
            name = CoinsController().get_coin_name_by_asset_id(asset_id=asset_id, db=db)
        return name

#TODO:
'''
Arreglar metodos de todo el controlador, ya que se modificaron las columnas de purchase_price, purcharse_date y purchase_quantity por price, date y quantity respectivamente.
Modificar el get_portfolio_data para que ahora filte por accion (buy o sell)
'''

import redis
from sqlmodel import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models import PortfolioData
from app.utils import get_difference_percentage
from app.services.portfolio_service import PortfolioService
from app.controllers.assets_controller import AssetsController
from app.services.portfolio_data_service import PortfolioDataService

r = redis.Redis(host='redis-container', port=6379, decode_responses=True)
class PortfolioDataController():

    def __init__(self):
        self.model = PortfolioData

    def get_total_portfolio_data(self, portfolio_id:int, user_id:int, db:Session):
        if not PortfolioService().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data = self.get_portfolio_simplify_info(portfolio_id=portfolio_id,db=db, user_id=user_id)
        for asset in portfolio_data['assets_data']:
            for asset_data in asset.values():
                asset_data['percentage'] = "{:.4g}".format((asset_data['current_value']/portfolio_data['current_value'])*100) + '%'
        return portfolio_data

    def get_portfolio_simplify_info(self, portfolio_id:int, db:Session, user_id:int):
        portfolio_data = {}
        data = []
        assets_id = PortfolioDataService().get_assets_id_by_portfolio_id(portfolio_id=portfolio_id, db=db)
        portfolio_current_value = 0
        portfolio_buy_value = 0
        for asset_id in assets_id:
            asset_data={}
            asset_movements = PortfolioDataService().get_simplify_movements_by_asset_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
            asset_total_quantity = 0
            asset_buy_price = 0
            asset_total_buy = 0
            for movement in asset_movements:
                asset_quantity = movement[0]
                asset_price = movement[1]
                asset_action = movement[2]
                if asset_action == 'buy':
                    asset_total_quantity += asset_quantity
                    asset_total_buy += asset_quantity
                    asset_buy_price += asset_quantity*asset_price
                elif asset_action == "sell":
                    asset_total_quantity -= asset_quantity
            asset_average_buy_price = float("{:.3g}".format(asset_buy_price / asset_total_buy))
            asset_total_quantity = float("{:.3g}".format(asset_total_quantity))
            asset_name = AssetsController().get_asset_name_by_id(asset_id=asset_id, db=db)
            asset_current_price = self.get_asset_price(db=db, asset_id=asset_id)
            portfolio_current_value += asset_current_price*asset_total_quantity
            portfolio_buy_value += asset_average_buy_price*asset_total_quantity
            asset_data[asset_name]={
                'id': asset_id,
                'average_price':asset_average_buy_price,
                'quantity':asset_total_quantity,
                'current_price': asset_current_price,
                'current_value':float("{:.6g}".format(asset_current_price*asset_total_quantity)),
                'buy_value': float("{:.6g}".format(asset_average_buy_price*asset_total_quantity)),
                'W/L percetage':get_difference_percentage(current_price=asset_current_price,purchase_price=asset_average_buy_price)
            }
            data.append(asset_data)
            portfolio_data['assets_data'] = data
            portfolio_data['id'] = portfolio_id
            portfolio_data['current_value'] = float("{:.4g}".format(portfolio_current_value))
            portfolio_data['buy_value'] = float("{:.4g}".format(portfolio_buy_value))
            portfolio_data['W/L percentage'] = get_difference_percentage(current_price=portfolio_data['current_value'], purchase_price=portfolio_data['buy_value'])

        return portfolio_data

    def get_asset_price(self, db:Session, asset_id:int):
        if r.exists(f"price-{asset_id}"):
            asset_current_price = float(r.get(f"price-{asset_id}"))
        else:
            asset_current_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
            now = datetime.now()
            if now.hour >=17:
                adding_days = 7 - now.weekday() if now.weekday() >= 4 else 1
                next_day  = now + timedelta(days=adding_days)
                market_open_our = datetime(next_day.year, next_day.month, next_day.day, 10, 30)
                seconds_to_expire = int((market_open_our - now).total_seconds())
                r.setex(name=f"price-{asset_id}", time=seconds_to_expire, value=asset_current_price)
            else:
                r.setex(name=f"price-{asset_id}", time=15, value=asset_current_price)
        return asset_current_price

    def get_movements_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session, user_id:int):
        if not PortfolioService().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        if not PortfolioDataService().exist_asset_in_portfolio(portfolio_id=portfolio_id, asset_id=asset_id, db=db):
            raise HTTPException(status_code=404, detail="No existe el activo en su portfolio.")
        movements = PortfolioDataService().get_movements_by_asset_id(portfolio_id=portfolio_id, asset_id=asset_id, db=db)
        return movements

    def add_asset_to_portfolio(self, asset_id:int, quantity:float, portfolio_id:int, user_id:int, db:Session) -> PortfolioData:
        if not PortfolioService().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        asset_price = self.get_asset_price(asset_id=asset_id, db=db)
        new_portfolio_data = PortfolioDataService().add(portfolio_id=portfolio_id, asset_id=asset_id, price=asset_price, quantity=quantity, db=db, action='buy')
        return new_portfolio_data

    def add_asset_movement(self, asset_id:int, portfolio_id:int, quantity:float, user_id:int, action:str, db: Session) -> PortfolioData:
        if not PortfolioService().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data_item = PortfolioDataService().get_portfolio_data_item_by_asset_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
        if not portfolio_data_item:
            raise HTTPException(status_code=404, detail="No se encontro el activo en el portfolio.")
        if action == "sell":
            asset_actual_quantity = PortfolioDataService().get_asset_quantity_by_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
            if not asset_actual_quantity:
                raise HTTPException(status_code=401, detail="No puedes vender el activo ya que no lo posees.")
            elif quantity > asset_actual_quantity:
                raise HTTPException(status_code=401, detail=f"No puedes vender dicha cantidad del activo. Solo posees {asset_actual_quantity} unidades.")
        asset_price = self.get_asset_price(asset_id=asset_id, db=db)
        new_portfolio_data = PortfolioDataService().add(portfolio_id=portfolio_id, asset_id=asset_id, price=asset_price, quantity=quantity, db=db, action=action)
        return new_portfolio_data

    def delete(self, asset_id:int, portfolio_id:int, user_id:int, db: Session) -> bool:
        if not PortfolioService().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        assets_movements = PortfolioDataService().get_movements_by_asset_id(db=db, portfolio_id=portfolio_id, asset_id=asset_id)
        if not assets_movements:
            raise HTTPException(status_code=404, detail="No se encontro el activo en el portfolio.")
        PortfolioDataService().delete(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
        return True

#TODO:
'''
Arreglar metodos de todo el controlador, ya que se modificaron las columnas de purchase_price, purcharse_date y purchase_quantity por price, date y quantity respectivamente.
Modificar el get_portfolio_data para que ahora filte por accion (buy o sell)
'''

from fastapi import HTTPException
from sqlmodel import Session, select, desc
from app.controllers.assets_controller import AssetsController
from app.models import PortfolioData
from app.controllers.portfolio_controller import PortfolioController
import redis
from datetime import datetime, timedelta

r = redis.Redis(host='redis-container', port=6379, decode_responses=True)
class PortfolioDataController():

    def __init__(self):
        self.model = PortfolioData

    def get_portfolio_data_by_id(self, portfolio_id, db:Session):
        query = select(self.model).where(self.model.portfolio_id == portfolio_id, self.model.active == True).order_by(self.model.id, self.model.asset_id, self.model.action)
        portfolio_data = db.exec(query).all()
        a = self.get_asset_total_amount_and_average_purchase_price(assets=self.group_asset_of_portfolio_data(assets=portfolio_data, db=db), db=db)
        return a

    def get_simplify_movements_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session, user_id:int):
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        if not self.exist_asset_in_portfolio(portfolio_id=portfolio_id, asset_id=asset_id, db=db):
            raise HTTPException(status_code=404, detail="No existe el activo en su portfolio.")
        query = select(self.model.quantity, self.model.price, self.model.action).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True).order_by(self.model.date)
        movements = db.exec(query).all()
        return movements

    def get_movements_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session, user_id:int):
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        if not self.exist_asset_in_portfolio(portfolio_id=portfolio_id, asset_id=asset_id, db=db):
            raise HTTPException(status_code=404, detail="No existe el activo en su portfolio.")
        query = select(self.model).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True).order_by(desc(self.model.date))
        movements = db.exec(query).all()
        return movements

    def exist_asset_in_portfolio(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model.id).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True)
        asset_exist = db.exec(query).all()
        return True if asset_exist else False

    def get_assets_id_by_portfolio_id(self, portfolio_id:int, db:Session):
        query = select(self.model.asset_id).where(self.model.portfolio_id == portfolio_id, self.model.active == True).distinct()
        assets = db.exec(query).all()
        return assets

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

    def get_portfolio_simplify_info(self, portfolio_id:int, db:Session, user_id:int):
        portfolio_data = {}
        data = []
        assets_id = self.get_assets_id_by_portfolio_id(portfolio_id=portfolio_id, db=db)
        portfolio_current_value = 0
        portfolio_buy_value = 0
        for asset_id in assets_id:
            asset_data={}
            asset_movements = self.get_simplify_movements_by_asset_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db, user_id=user_id)
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
                'W/L percetage':self.get_difference_percentage(current_price=asset_current_price,purchase_price=asset_average_buy_price)
            }
            data.append(asset_data)
            portfolio_data['assets_data'] = data
            portfolio_data['id'] = portfolio_id
            portfolio_data['current_value'] = float("{:.4g}".format(portfolio_current_value))
            portfolio_data['buy_value'] = float("{:.4g}".format(portfolio_buy_value))
            portfolio_data['W/L percentage'] = self.get_difference_percentage(current_price=portfolio_data['current_value'], purchase_price=portfolio_data['buy_value'])

        return portfolio_data

    def get_total_portfolio_data(self, portfolio_id:int, user_id:int, db:Session):
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data = self.get_portfolio_simplify_info(portfolio_id=portfolio_id,db=db, user_id=user_id)
        for asset in portfolio_data['assets_data']:
            for asset_data in asset.values():
                asset_data['percentage'] = "{:.4g}".format((asset_data['current_value']/portfolio_data['current_value'])*100) + '%'
        return portfolio_data


    def group_asset_of_portfolio_data(self, assets:list, db:Session):
        portfolio_grouped = {}
        for portfolio_item in assets:
            asset_name = AssetsController().get_asset_name_by_id(asset_id=portfolio_item.asset_id, db=db)
            if asset_name not in portfolio_grouped:
                portfolio_grouped[asset_name] = {"id":portfolio_item.asset_id,"movements":[portfolio_item.serialize()]}
            else:
                portfolio_grouped[asset_name]["movements"].append(portfolio_item.serialize())
        return portfolio_grouped

    def get_asset_total_amount_and_average_purchase_price(self, assets:dict, db:Session):
        amounts = {}
        for asset_name, asset in assets.items():
            asset_amount = 0
            asset_by_purchase_price = 0
            total_bought = 0
            for movement in asset['movements']:
                if movement['action'] =='buy':
                    asset_amount += movement['quantity']
                    total_bought += movement['quantity']
                    asset_by_purchase_price += movement['quantity'] * movement['price']
                else:
                    asset_amount -= movement['quantity']
            asset['total_amount'] = float("{:.3g}".format(asset_amount))
            asset['average_purchase_price'] = round(asset_by_purchase_price / total_bought, 2)
            asset['current_price'] = AssetsController().get_asset_price_by_id(asset_id=asset['id'], db=db)
            amounts[asset_name]={"total": float("{:.3g}".format(asset['total_amount']*asset['current_price']))}
        current_portfolio_value = 0
        for amount in amounts.values():
            current_portfolio_value +=amount['total']
        for asset_name in amounts.keys():
            amounts[asset_name]['percentage'] = "{:.3g}%".format((amounts[asset_name]['total']/current_portfolio_value)*100)
        print(amounts)
        return assets

    def get_portfolio_data(self, portfolio_id:int, user_id:int, db:Session) -> dict:
        portfolio_information = {}
        all_assets_info = []
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data = self.get_portfolio_data_by_id(portfolio_id=portfolio_id, db=db)
        for portfolio_item in portfolio_data:
            asset_info = portfolio_item.serialize()
            asset_id = portfolio_item.asset_data.id
            asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
            asset_info['asset_name'] = AssetsController().get_asset_name_by_id(asset_id=asset_id, db=db)
            asset_info['current_price'] = asset_price
            asset_info['difference_percentage'] = self.get_difference_percentage(current_price=asset_price, purchase_price=portfolio_item.purchase_price)
            all_assets_info.append(asset_info)
        portfolio_information['assets_info'] = all_assets_info
        portfolio_information['total_purchase'] = self.get_total_purchase_of_portfolio(portfolio_id=portfolio_id, db=db)
        portfolio_information['current_value'] = self.get_current_portfolio_value(portfolio_id=portfolio_id, db=db)
        portfolio_information['total_difference_percentage'] = self.get_difference_percentage(purchase_price = portfolio_information['total_purchase'],
                                                                                              current_price = portfolio_information['current_value'])

        return portfolio_information

    def add_asset_to_portfolio(self, asset_id:int, quantity:float, portfolio_id:int, user_id:int, db:Session) -> PortfolioData:
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
        new_portfolio_data = PortfolioData(portfolio_id=portfolio_id, asset_id=asset_id, price=asset_price, quantity=quantity, action='buy')
        db.add(new_portfolio_data)
        db.commit()
        db.refresh(new_portfolio_data)
        return new_portfolio_data

    def get_total_purchase_of_portfolio(self, portfolio_id:int, db:Session) -> float:
        portfolio_data = self.get_portfolio_data_by_id(db=db, portfolio_id=portfolio_id)
        total = sum(asset.purchase_price for asset in portfolio_data)
        return total

    def get_current_portfolio_value(self, portfolio_id:int, db:Session) -> float:
        portfolio_data = self.get_portfolio_data_by_id(db=db, portfolio_id=portfolio_id)
        total = 0
        for portfolio_item in portfolio_data:
            asset_id = portfolio_item.asset_data.id
            asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
            total += asset_price
        return total

    def get_portfolio_data_item_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model).where(self.model.portfolio_id == portfolio_id, self.model.asset_id == asset_id, self.model.active == True)
        portfolio_data = db.exec(query).first()
        return portfolio_data

    def get_difference_percentage(self, purchase_price:float, current_price:float) -> str:
        percentage = ((current_price-purchase_price) / purchase_price) * 100
        final_percentage = "{:.3g}%".format(percentage)
        return final_percentage

    def get_asset_quantity_by_id(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model.quantity, self.model.action).where(self.model.portfolio_id == portfolio_id, self.model.asset_id == asset_id, self.model.active == True)
        asset_movements = db.exec(query).all()
        asset_quantity=0
        for movement in asset_movements:
            if movement[1] == "sell":
                asset_quantity -= movement[0]
            elif movement[1] == "buy":
                asset_quantity += movement[0]
        return float("{:.3g}".format(asset_quantity)) if asset_quantity > 0 else 0

    def add_asset_movement(self, asset_id:int, portfolio_id:int, new_quantity:float, user_id:int, action:str, db: Session) -> PortfolioData:
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data_item = self.get_portfolio_data_item_by_asset_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
        if not portfolio_data_item:
            raise HTTPException(status_code=404, detail="No se encontro el activo en el portfolio.")
        if action == "sell":
            asset_actual_quantity = self.get_asset_quantity_by_id(asset_id=asset_id, portfolio_id=portfolio_id, db=db)
            if not asset_actual_quantity:
                raise HTTPException(status_code=401, detail="No puedes vender el activo ya que no lo posees.")
            elif new_quantity > asset_actual_quantity:
                raise HTTPException(status_code=401, detail=f"No puedes vender dicha cantidad del activo. Solo posees {asset_actual_quantity} unidades.")
        asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
        new_portfolio_data = PortfolioData(portfolio_id=portfolio_id, asset_id=asset_id, price=asset_price, quantity=new_quantity, action=action)
        db.add(new_portfolio_data)
        db.commit()
        db.refresh(new_portfolio_data)
        return new_portfolio_data

    def delete(self, asset_id:int, portfolio_id:int, user_id:int, db: Session) -> bool:
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        assets_movements = self.get_movements_by_asset_id(db=db, user_id=user_id, portfolio_id=portfolio_id, asset_id=asset_id)
        if not assets_movements:
            raise HTTPException(status_code=404, detail="No se encontro el activo en el portfolio.")
        for movement in assets_movements:
            movement.active = False
        db.commit()
        return True
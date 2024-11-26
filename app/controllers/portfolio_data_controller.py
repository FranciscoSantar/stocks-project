from fastapi import HTTPException
from sqlmodel import Session, select
from app.controllers.assets_controller import AssetsController
from app.models import PortfolioData
from app.controllers.portfolio_controller import PortfolioController
class PortfolioDataController():

    def __init__(self):
        self.model = PortfolioData

    def get_portfolio_data_by_id(self, portfolio_id, db:Session):
        query = select(self.model).where(self.model.portfolio_id == portfolio_id)
        portfolio_data = db.exec(query).all()
        return portfolio_data

    def get_portfolio_data(self, portfolio_id:int, user_id:int, db:Session):
        portfolio_information = {}
        all_assets_info = []
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        portfolio_data = self.get_portfolio_data_by_id(portfolio_id=portfolio_id, db=db)
        for portfolio_item in portfolio_data:
            asset_info = portfolio_item.serialize()
            asset_id = portfolio_item.asset_data.id
            asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
            asset_info['current_price'] = asset_price
            asset_info['difference_percentage'] = self.get_difference_percentage(current_price=asset_price, purchase_price=portfolio_item.purchase_price)
            all_assets_info.append(asset_info)
        portfolio_information['assets_info'] = all_assets_info
        portfolio_information['total_purchase'] = self.get_total_purchase_of_portfolio(portfolio_id=portfolio_id, db=db)
        portfolio_information['current_value'] = self.get_current_portfolio_value(portfolio_id=portfolio_id, db=db)
        portfolio_information['total_difference_percentage'] = self.get_difference_percentage(purchase_price = portfolio_information['total_purchase'],
                                                                                              current_price = portfolio_information['current_value'])

        return portfolio_information

    def add_asset_to_portfolio(self, asset_id:int, quantity:float, portfolio_id:int, user_id:int, db:Session):
        if not PortfolioController().check_portfolio_owner(db=db, user_id=user_id, id=portfolio_id):
            raise HTTPException(status_code=401, detail="El portfolio no te pertenece.")
        asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
        new_portfolio_data = PortfolioData(portfolio_id=portfolio_id, asset_id=asset_id, purchase_price=asset_price, purchase_quantity=quantity)
        db.add(new_portfolio_data)
        db.commit()
        db.refresh(new_portfolio_data)
        return new_portfolio_data

    def get_total_purchase_of_portfolio(self, portfolio_id:int, db:Session):
        portfolio_data = self.get_portfolio_data_by_id(db=db, portfolio_id=portfolio_id)
        total = sum(asset.purchase_price for asset in portfolio_data)
        return total

    def get_current_portfolio_value(self, portfolio_id:int, db:Session):
        portfolio_data = self.get_portfolio_data_by_id(db=db, portfolio_id=portfolio_id)
        total = 0
        for portfolio_item in portfolio_data:
            asset_id = portfolio_item.asset_data.id
            asset_price = AssetsController().get_asset_price_by_id(asset_id=asset_id, db=db)
            total += asset_price
        return total

    def get_difference_percentage(self, purchase_price:float, current_price:float):
        aux_percentage = current_price / purchase_price
        percentage = abs(aux_percentage-1)*100
        final_percentage = "{:.2f}%".format(percentage) if aux_percentage >=1 else "-{:.2f}%".format(percentage)
        return final_percentage



from sqlmodel import Session, select, desc, func
from app.models import PortfolioData

class PortfolioDataService():

    def __init__(self):
        self.model = PortfolioData

    def get_assets_id_by_portfolio_id(self, portfolio_id:int, db:Session):
        query = select(self.model.asset_id).where(self.model.portfolio_id == portfolio_id, self.model.active == True).distinct()
        assets = db.exec(query).all()
        return assets

    def get_simplify_movements_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model.quantity, self.model.price, self.model.action).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True).order_by(self.model.date)
        movements = db.exec(query).all()
        return movements

    def exist_asset_in_portfolio(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model.id).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True)
        asset_exist = db.exec(query).all()
        return True if asset_exist else False

    def get_movements_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model).where(self.model.portfolio_id == portfolio_id, self.model.asset_id==asset_id, self.model.active == True).order_by(desc(self.model.date))
        movements = db.exec(query).all()
        return movements

    def get_portfolio_data_item_by_asset_id(self, portfolio_id:int, asset_id:int, db:Session):
        query = select(self.model).where(self.model.portfolio_id == portfolio_id, self.model.asset_id == asset_id, self.model.active == True)
        portfolio_data = db.exec(query).first()
        return portfolio_data

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

    def get_max_id(self, db:Session):
        query = select(func.max(self.model.id))
        max_id = db.exec(query).one_or_none()
        return max_id + 1 if max_id is not None else 1

    def add(self, portfolio_id:int, asset_id:int, price:float, quantity:float , db:Session, action:str) -> PortfolioData:
        new_portfolio_data = PortfolioData(id=self.get_max_id(db=db), portfolio_id=portfolio_id, asset_id=asset_id, price=price, quantity=quantity, action=action)
        db.add(new_portfolio_data)
        db.commit()
        db.refresh(new_portfolio_data)
        return new_portfolio_data

    def delete(self, asset_id:int, portfolio_id:int, db: Session) -> bool:
        assets_movements = self.get_movements_by_asset_id(db=db, portfolio_id=portfolio_id, asset_id=asset_id)
        for movement in assets_movements:
            movement.active = False
        db.commit()
        return True

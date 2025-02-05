from sqlmodel import Session, select, func
from app.models import Portfolios

class PortfolioService():

    def __init__(self):
        self.model = Portfolios

    def get_by_id(self, user_id:int, id:int, db:Session):
        query = select(self.model).where(self.model.owner_id == user_id, self.model.id == id, self.model.active==True)
        return db.exec(query).first()

    def check_portfolio_owner(self, user_id:int, id:int, db:Session):
        return True if self.get_by_id(user_id=user_id, id=id, db=db) else False
from fastapi import HTTPException
from sqlmodel import Session, select, func
from app.models import Portfolios
from app.check_models import PortfolioBody
from app.controllers.plans_controller import PlansController
class PortfolioController():

    def __init__(self):
        self.model = Portfolios
        pass

    def get_all(self, user_id:int, db:Session):
        query = select((self.model)).where(self.model.owner_id==user_id)
        return db.exec(query).all()

    def get_amount_portfolios_by_user_id(self, user_id:int, db:Session):
        query = select(func.count(self.model.id)).where(self.model.owner_id==user_id)
        return db.exec(query).first()

    def get_portfolio_by_name(self, user_id:int, name:str, db:Session):
        query = select(self.model).where(self.model.owner_id == user_id, self.model.name == name)
        return db.exec(query).first()


    def create(self, user:dict, portfolio_data:PortfolioBody, db:Session) ->Portfolios:
        portfolios_by_user = self.get_amount_portfolios_by_user_id(db=db, user_id=user['user_id'])
        plan = PlansController().get_by_id(db=db, id=user['plan_id'])
        max_portfolios_by_plan = plan.max_portfolios
        if portfolios_by_user >= max_portfolios_by_plan:
            raise HTTPException(status_code=400, detail=f"Alcanzaste al limite de portfolios en tu plan: {plan.name}")
        existing_portfolio_by_name = self.get_portfolio_by_name(user_id=user['user_id'], name=portfolio_data.name, db=db)
        if existing_portfolio_by_name:
            raise HTTPException(status_code=400, detail=f"Ya existe un portfolio con este nombre.")
        new_portfolio = Portfolios(name=portfolio_data.name, owner_id=user['user_id'])
        db.add(new_portfolio)
        db.commit()
        return new_portfolio

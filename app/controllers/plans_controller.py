from sqlmodel import Session, select, func
from app.models import Plans
class PlansController():

    def __init__(self):
        self.model = Plans

    def get_by_id(self, db:Session, id:int):
        query = select(self.model).where(self.model.id == id)
        plan_data = db.exec(query).first()
        return plan_data

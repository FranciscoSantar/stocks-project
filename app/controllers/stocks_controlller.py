from sqlmodel import Session, select
from app.models import Stocks
class StocksController():

    def __init__(self):
        pass

    def get_stocks(self, page_number:int, items_per_page:int, db_session:Session):
        stocks = db_session.exec(select(Stocks).offset((page_number - 1) * items_per_page).limit(items_per_page)).all()
        return stocks
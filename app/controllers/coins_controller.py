from sqlmodel import Session, select
from app.models import Coins
class CoinsController():

    def __init__(self):
        pass

    def get_coins(self, page_number:int, items_per_page:int, db_session:Session):
        coins = db_session.exec(select(Coins).offset((page_number - 1) * items_per_page).limit(items_per_page)).all()
        return coins
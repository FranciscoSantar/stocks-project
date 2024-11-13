from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.controllers.portfolio_controller import PortfolioController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
from app.check_models import PortfolioBody

portfolios_router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@portfolios_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_protfolios(db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    portfolios = PortfolioController().get_all(user_id=user['user_id'], db=db_session)
    return {"portfolios":portfolios}


@portfolios_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio_data:PortfolioBody, db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    new_portfolio = PortfolioController().create(db=db_session, user=user, portfolio_data=portfolio_data)
    return {"new_portfolio":new_portfolio}


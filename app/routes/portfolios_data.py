from fastapi import APIRouter, Depends, Path
from sqlmodel import Session
from app.controllers.portfolio_data_controller import PortfolioDataController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
from app.check_models import AssetBody

portfolios_data_router = APIRouter(prefix="/portfolio-data", tags=["portfolio-data"])

@portfolios_data_router.get("/{portfolio_id}", status_code=status.HTTP_200_OK)
async def get_portfolio_data(portfolio_id:int = Path(gt=0), db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    portfolio_data = PortfolioDataController().get_portfolio_data(db=db_session, portfolio_id=portfolio_id, user_id=user['id'])
    return portfolio_data

@portfolios_data_router.post("/{portfolio_id}", status_code=status.HTTP_201_CREATED)
async def add_asset_to_portfolio(asset:AssetBody, portfolio_id:int = Path(gt=0), db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    portfolios = PortfolioDataController().add_asset_to_portfolio(db=db_session, user_id=user['id'], asset_id=asset.id, quantity=asset.quantity, portfolio_id=portfolio_id)
    return {"portfolios":portfolios}



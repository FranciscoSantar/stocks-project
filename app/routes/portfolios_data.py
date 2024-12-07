from fastapi import APIRouter, Depends, Path
from sqlmodel import Session
from app.controllers.portfolio_data_controller import PortfolioDataController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
from app.check_models import AssetBody, AssetMovement

portfolios_data_router = APIRouter(prefix="/portfolio-data", tags=["portfolio-data"])

@portfolios_data_router.get("/{portfolio_id}", status_code=status.HTTP_200_OK)
async def get_portfolio_data(portfolio_id:int = Path(gt=0), db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    portfolio_data = PortfolioDataController().get_total_portfolio_data(db=db_session, portfolio_id=portfolio_id, user_id=user['id'])
    return portfolio_data

@portfolios_data_router.get("/{portfolio_id}/{asset_id}", status_code=status.HTTP_200_OK)
async def get_asset_data_in_portfolio(portfolio_id:int = Path(gt=0), asset_id:int = Path(gt=0), db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    asset_data = PortfolioDataController().get_movements_by_asset_id(db=db_session, portfolio_id=portfolio_id, user_id=user['id'], asset_id=asset_id)
    asset_data_array = [asset.serialize_simple() for asset in asset_data]
    return {"asset_movements":asset_data_array}


@portfolios_data_router.post("/{portfolio_id}", status_code=status.HTTP_201_CREATED)
async def add_asset_to_portfolio(asset:AssetBody, portfolio_id:int = Path(gt=0), db_session: Session = Depends(get_db),  user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    portfolios = PortfolioDataController().add_asset_to_portfolio(db=db_session, user_id=user['id'], asset_id=asset.id, quantity=asset.quantity, portfolio_id=portfolio_id)
    return {"portfolios":portfolios}

@portfolios_data_router.post("/{portfolio_id}/{asset_id}", status_code=status.HTTP_200_OK)
async def add_asset_movement(quantityAsset:AssetMovement, portfolio_id:int = Path(gt=0), asset_id:int = Path(gt=0), db_session: Session = Depends(get_db), user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    edited_portfolio_data_item = PortfolioDataController().add_asset_movement(asset_id=asset_id, portfolio_id=portfolio_id, new_quantity=quantityAsset.quantity, user_id=user['id'], action=quantityAsset.action, db=db_session)
    return edited_portfolio_data_item


@portfolios_data_router.delete("/{portfolio_id}/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(portfolio_id:int = Path(gt=0), asset_id:int = Path(gt=0), db_session: Session = Depends(get_db), user : dict = Depends(AuthController().get_current_user)): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    edited_portfolio_data_item = PortfolioDataController().delete(asset_id=asset_id, portfolio_id=portfolio_id,user_id=user['id'], db=db_session)
    return edited_portfolio_data_item


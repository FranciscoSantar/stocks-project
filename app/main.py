from fastapi import FastAPI
from app.routes.coins import coins_router
from app.routes.stocks import stocks_router
from app.routes.portfolios import portfolios_router
from app.routes.roles import roles_router
from app.routes.assets_types import assets_types_router
from app.routes.auth import auth_router
from app.routes.portfolios_data import portfolios_data_router
from app.routes.ping import ping_router
# models.Base.metadata.create_all(bind=engine) #Only runs if database doesnt exist.

app = FastAPI()
app.include_router(coins_router)
app.include_router(stocks_router)
app.include_router(portfolios_router)
app.include_router(portfolios_data_router)
app.include_router(roles_router)
app.include_router(assets_types_router)
app.include_router(auth_router)
app.include_router(ping_router)


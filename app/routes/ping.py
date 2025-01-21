from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.controllers.coins_controller import CoinsController
from app.database import get_db
from starlette import status
from app.controllers.auth_controller import AuthController
ping_router = APIRouter(prefix="/ping", tags=["ping"])

@ping_router.get("/", status_code=status.HTTP_200_OK)
async def ping(): #El depends indica una dependencia, que dice que se debe ejecutar la funcion get_db antes de la ruta.
    return {"ping": "pong"}

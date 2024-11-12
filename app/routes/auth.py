from fastapi import APIRouter, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from starlette import status
from app.controllers.auth_controller import AuthController
from app.check_models import userRequest, UserLogin

auth_router = APIRouter(prefix="/auth", tags=["auth"]) #El tag es para swagger
@auth_router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(user: userRequest, db: Session = Depends(get_db)):
    new_user = AuthController().signup(user=user, db=db)
    return {"todos": new_user}

@auth_router.post("/login/", status_code=status.HTTP_200_OK)
async def login(user_login_data: UserLogin, db: Session = Depends(get_db)):
    username = user_login_data.username
    password = user_login_data.password
    token = AuthController().login(username=username, password=password, db=db)
    return {"token": token}
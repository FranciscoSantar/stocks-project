from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from app.models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import os

ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login/")

class AuthController():


    def signup(self, user: User, db: Session) -> User:
        exising_user_by_email  = db.exec(select(User).filter(User.email == user.email)).first()
        if exising_user_by_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        exising_user_by_username  = db.exec(select(User).filter(User.username == user.username)).first()
        if exising_user_by_username:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = self.hash_password(user.password)
        user_model = User(username=user.username, email=user.email, phone=user.phone, name=user.name, password=hashed_password)
        db.add(user_model)
        db.commit()
        return user_model

    def login(self, username:str, password:str, db: Session):
        user = db.exec(select(User).filter(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=401, detail='Invalid username')
        if not self.verify_user(username=username, password=password, db=db):
            raise HTTPException(status_code=401, detail='Invalid password')
        expire_time = timedelta(minutes=60)
        token = self.create_access_token(username=username, user_id = user.id, role_id=user.role_id, plan_id=user.plan_id ,expires_delta = expire_time)
        return token

    def hash_password(self, password: str):
        return bcrypt_context.hash(password)

    def verify_user(self, username: str, password: str, db: Session):
        user = db.exec(select(User).filter(User.username == username)).first()
        if not user:
            return False
        verify_password = bcrypt_context.verify(password, user.password)
        if not verify_password:
            return False
        return True

    def create_access_token(self, username: str, user_id:int, role_id:int, plan_id:int, expires_delta: timedelta):
        encode = {'username': username, 'user_id': user_id, 'role_id':role_id, 'plan_id':plan_id}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({'exp': expires})
        jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
        return jwt.encode(encode, key=jwt_secret_key, algorithm=ALGORITHM)

    def change_password(self, username: str, new_password: str, db: Session):
        
        user = db.exec(select(User).filter(User.username == username)).first()
        if not user:
            return False
        user.password = bcrypt_context.hash(new_password)
        db.commit()
        return True

    async def get_current_user(self, token: str = Depends(oauth2_bearer)):
        try:
            jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
            payload = jwt.decode(jwt=token, key=jwt_secret_key, algorithms=[ALGORITHM])
            username: str = payload.get("username")
            user_id : int = payload.get("user_id")
            role_id :int = payload.get("role_id")
            plan_id :int = payload.get("plan_id")
            if username is None or user_id is None:
                raise HTTPException(status_code=401, detail="Could not validate user.")
            return {'username': username, 'user_id': user_id, 'role_id':role_id, 'plan_id':plan_id}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

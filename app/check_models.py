from pydantic import BaseModel, Field
from typing import Optional

class userRequest(BaseModel):
    username :str = Field(min_length=3)
    email :str = Field(min_length=3)
    phone :str | None = Field(default=None)
    name :str = Field(min_length=3)
    password :str | None = Field(min_length=3, default=None)

class UserLogin(BaseModel):
    username: str
    password: str

class PortfolioBody(BaseModel):
    id: int | None = None
    name: str = Field(min_length=2)

class AssetBody(BaseModel):
    id: int = Field()
    portfolio_id: int = Field()
    quantity:float = Field()

class AssetMovement(BaseModel):
    quantity:float = Field(ge=0)
    action:str = Field()
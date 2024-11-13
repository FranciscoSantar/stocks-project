from datetime import datetime
from sqlmodel import Field, SQLModel


class Assets(SQLModel, table=True):
    __tablename__ = "assets"
    id: int = Field(primary_key=True)
    type_id: int = Field(foreign_key="assets_type.id")

class AssetsType(SQLModel, table=True):
    __tablename__ = "assets_type"
    id: int = Field(primary_key=True)
    type: str = Field()

class Coins(SQLModel, table=True):
    __tablename__ = "coins"
    id: int = Field(primary_key=True)
    asset_id: int | None = Field(foreign_key="assets.id")
    name: str | None = Field()
    symbol: str | None = Field()
    description: str | None = Field()
    image: str | None = Field()
    website: str | None = Field()

class Stocks(SQLModel, table=True):
    __tablename__ = "stocks"
    id: int = Field(primary_key=True)
    asset_id: int | None = Field(foreign_key="assets.id")
    name: str | None = Field()
    symbol: str | None = Field()
    description: str | None = Field()
    image: str | None = Field()
    website: str | None = Field()
    country: str | None = Field()
    industry: str | None = Field()

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    name : str = Field()
    password: str = Field()
    role_id: int = Field(foreign_key="roles.id", default=1)
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = Field(default=True)
    plan_id:int = Field(foreign_key="plans.id", default=1)

class Plans(SQLModel, table=True):
    __tablename__ = "plans"
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    max_portfolios: int = Field()

class Roles(SQLModel, table=True):
    __tablename__ = "roles"
    id: int = Field(primary_key=True)
    name: str = Field()

class Portfolios(SQLModel, table=True):
    __tablename__ = "portfolios"
    id: int = Field(primary_key=True)
    name: str = Field()
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = Field(default=True)

class PortfolioData(SQLModel, table=True):
    __tablename__ = "portfolio_data"
    id: int = Field(primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")
    asset_id: int = Field(foreign_key="assets.id")
    purchase_date: datetime = Field(default_factory=datetime.now)
    purchase_price: float = Field()
    purchase_quantity: float = Field()
    active: bool = Field(default=True)

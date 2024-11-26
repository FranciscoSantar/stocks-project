from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


class Assets(SQLModel, table=True):
    __tablename__ = "assets"
    id: int = Field(primary_key=True)
    type_id: int = Field(foreign_key="assets_type.id")

    asset_type:"AssetsType" = Relationship(back_populates='assets')
    portfolio_items : list["PortfolioData"] = Relationship(back_populates='asset_data')

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}

class AssetsType(SQLModel, table=True):
    __tablename__ = "assets_type"
    id: int = Field(primary_key=True)
    type: str = Field()

    assets: list["Assets"] = Relationship(back_populates='asset_type')

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
class Coins(SQLModel, table=True):
    __tablename__ = "coins"
    id: int = Field(primary_key=True)
    asset_id: int | None = Field(foreign_key="assets.id")
    name: str | None = Field()
    symbol: str | None = Field()
    description: str | None = Field()
    image: str | None = Field()
    website: str | None = Field()

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
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

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
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

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
class Plans(SQLModel, table=True):
    __tablename__ = "plans"
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    max_portfolios: int = Field()

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
class Roles(SQLModel, table=True):
    __tablename__ = "roles"
    id: int = Field(primary_key=True)
    name: str = Field()

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
class Portfolios(SQLModel, table=True):
    __tablename__ = "portfolios"
    id: int = Field(primary_key=True)
    name: str = Field()
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = Field(default=True)

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}
class PortfolioData(SQLModel, table=True):
    __tablename__ = "portfolio_data"
    id: int = Field(primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")
    asset_id: int = Field(foreign_key="assets.id")
    purchase_date: datetime = Field(default_factory=datetime.now)
    purchase_price: float = Field()
    purchase_quantity: float = Field()
    active: bool = Field(default=True)

    asset_data:"Assets" = Relationship(back_populates='portfolio_items')

    def serialize(self):
        return {key: getattr(self, key) for key in self.__fields__.keys()}

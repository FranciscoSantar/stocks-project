from sqlmodel import Session, create_engine
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()


user = os.environ.get('PGUSER')
password = os.environ.get('PGPASSWORD')
dbname = os.environ.get('PGDATABASE')
host = os.environ.get('PGHOST')
port = '5432'

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(DATABASE_URL)
# SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as db:
        yield db  # Proporciona la sesión para ser usada en las rutas
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

config = Config('../.env')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
DB_TABLE = config('DB_NAME')

SQLALCHEMY_DB_URL = f'postgresql://{USER}:{PASSWORD}@localhost/{DB_TABLE}'
engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DB_TABLE = os.getenv('DB_NAME')

SQLALCHEMY_DB_URL = f'postgresql://{USER}:{PASSWORD}@localhost/{DB_TABLE}'
engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

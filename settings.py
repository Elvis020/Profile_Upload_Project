import os

from dotenv import load_dotenv

base_path = os.path.dirname(__file__)
env_path = os.path.abspath(os.path.join(base_path, '.env'))
load_dotenv(dotenv_path=env_path)

print(env_path)


class Settings:
    POSTGRES_USER= os.getenv("DB_USER")
    POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
    POSTGRES_DB = os.getenv("DB_NAME")
    POSTGRES_DB_TEST = os.getenv("TEST_DB_NAME")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
    TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB_TEST}"


settings = Settings()

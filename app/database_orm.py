from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import config
from urllib.parse import quote

SQLALCHEMY_DATABASE_URL = f"postgresql://{config.settings.DB_USERNAME}:%s@{config.settings.DATABASE_HOSTNAME}/{config.settings.DB_NAME}-orm"

engine = create_engine(SQLALCHEMY_DATABASE_URL % quote(config.settings.DB_PASSWORD))

# Each instance of the SessionLocal class will be a database session. The class itself is not a database session yet
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base() returns a class which will be used to create database models or classes (the ORM models)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
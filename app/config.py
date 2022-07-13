# This File Fetches and varifies Environment Variables that will imported in other scripts
#import os
from pydantic import BaseSettings
#from dotenv import load_dotenv


class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DB_NAME: str
    DB_NAME_TEST: str
    DB_PORT: str
    DB_USERNAME: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    #class Config:
    #    env_file = ".env"
#load_dotenv()
settings = Settings()
#settings = Settings(_env_file=".env")

#print(f"Loading Env Variables: {settings}") 
#print(f"One of the env Variable: {settings.DB_PORT}")
"""
from dotenv import dotenv_values, load_dotenv
from pathlib import Path
import os
config = dotenv_values()

env_file = ".env"
env_path = Path(env_file).expanduser()
if env_path.is_file():
    print(f"env file is valid")

print(f"Parsed Env Variables: {config.get('DATABASE_HOSTNAME')}")
"""
#load_dotenv()

#print (os.getenv("DATABASE_HOSTNAME"))
# This script takes User Data and generates JWT token with Expiration
# Library Used : python-jose 
# pip install "python-jose[cryptography]"
# It generates and verify JWT tokens in Python


from fastapi import Depends, HTTPException, status
from . import schemas, config, models
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from .database_orm import get_db
from sqlalchemy.orm import Session
#from . import database

# to get a string like SECRET_KEY run:
# openssl rand -hex 32
# Python code to generate SECRET_KEY
# from secrets import token_bytes
# from base64 import b64encode
# print(b64encode(token_bytes(32)).decode())

SECRET_KEY = config.settings.SECRET_KEY
ALGORITHM = config.settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2PasswordBearer looks in the request for Authorization header and check if the value is Bearer plus some token, 
# and will return the token as a str
# It will respond with a 401 status code error (UNAUTHORIZED) on meeting the above conditions.
# tokenUrl will be the one that the client should use to get the token. 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# payLoad will contain the User Data that will be encoded into the JWT token
# User Data can be anything like user_id or user_role, etc
def create_access_token(payLoad: dict):
    user_data = payLoad.copy()
    # Create Expiration
    expiration = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #print(f"UTCNOW - {expiration}")
    # Call datetime.datetime.isoformat() to convert datetime.datetime into a ISO date format, which is compatible with JSON
    #expiration = expiration.isoformat()
    # datetime.datetime.timestamp() converts datetime in epochtime
    expiration = expiration.timestamp()
    #print(f"UTCNOW ISO Format- {expiration}")
    # Add expiration to the payLoad(dictionary)
    user_data.update({"exp": expiration})

    encoded_token = jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)
    #print (f"Encoded token : {encoded_token}")
    return encoded_token

def verify_access_token(token: str, credentials_exception):
    # verify the token with try & except
    try:
        #print(f"Token for Verification : {token}")
        payLoad = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract the User ID from the token after it is decoded
        user_id = payLoad.get("user_id")
        # If user id not found then raise exception defined in [get_current_user] function
        if user_id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=user_id)
    except JWTError as jwt_error:
        print(f"Error Detected while decoding JWT Token : {jwt_error}")
        raise credentials_exception

    return token_data 

# Using oauth2_scheme = OAuth2PasswordBearer in Depends so that if our function is executed, it will extract the content(Bearer token) from the Authorization Header and make sure it is a str and assign it to our variable 'token'.
def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)

# Get current_user using current_user_id
def get_current_user(user_id, db: Session = Depends(get_db)):
    #print(f"LOOKATME - {user_id}")
    #record = database.cursor.execute(""" SELECT email FROM users WHERE id = %s """, (user_id,)).fetchone()
    record = db.query(models.User.email).filter(models.User.id == user_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error Fetching User Details")
    #print(f"Data Retrieved from DB: {record}")
    return record['email']


# Path Operations for Authorization

from fastapi import Depends, status, APIRouter, HTTPException
from .. import utils, schemas, oauth2, models
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database_orm import get_db
from sqlalchemy.orm import Session
#from .. import database

router = APIRouter(prefix="/login", tags=['Login ORM'])

@router.post("/", response_model=schemas.Token)
def verify_login(payLoad: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #record = database.cursor.execute(""" SELECT * FROM users WHERE email = %s """, (payLoad.username,)).fetchone()
    record = db.query(models.User).filter(models.User.email == payLoad.username).first()
    #print(f"User Details type: {type(record)} and User Details: {record}")
    
    if not record:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
        
    record = record.__dict__
    if not utils.verify_password(payLoad.password, record['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    # create a token with expiration time
    # below create_access_token() will take parameter as User Data which can be anything like user_id or user_role, etc
    #print(f"User Details type: {type(record)}\n User Details: {record['id']}")
    access_token  = oauth2.create_access_token(payLoad={"user_id": record['id']})

    #return generated token
    #return{"token": "API token"}
    return {"access_token": access_token, "token_type": "Bearer"}

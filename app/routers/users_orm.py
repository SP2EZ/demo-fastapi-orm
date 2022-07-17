# Path Operations for users

from fastapi import status, HTTPException, APIRouter, Depends
from .. import schemas, utils, models
from ..database_orm import get_db
from sqlalchemy.orm import Session
#from .. import database

router = APIRouter(prefix="/users", tags=['Users ORM'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(payLoad: schemas.UserRequest, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(payLoad.password)
    payLoad.password = hashed_password

    # SQL Equivalent
    # create_record = database.cursor.execute(""" INSERT INTO users (email, password) VALUES (%s, %s) RETURNING * """, (payLoad.email, payLoad.password)).fetchone()
    # database.conn.commit()
    old_record = db.query(models.User.email).filter(models.User.email == payLoad.email).first()
    if not old_record:
        create_record = models.User(**payLoad.dict())
        db.add(create_record)
        db.commit()
        # refresh will retrieves the newly created post and stores it back to variable new_posts
        db.refresh(create_record)
        return create_record
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User already exists !!!")

    

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    # SQL Equivalent
    # record = database.cursor.execute(""" SELECT * FROM users WHERE id = %s """, (id,)).fetchone()
    record = db.query(models.User.email, models.User.created_at).filter(models.User.id == id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Id: {id} not found")
    #print(f"Data Retrieved from DB: {record}")
    return record   


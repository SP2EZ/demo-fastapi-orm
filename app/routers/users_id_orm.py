# Path Operations for Getting User Id
# This Path is only allowed for Testing

from fastapi import status, HTTPException, APIRouter, Depends
from .. import schemas, models, config
from ..database_orm import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/usersid", tags=['Users Id'])

@router.post("/", response_model=schemas.UserId)
def get_user(payLoad: schemas.UserIdRequest, db: Session = Depends(get_db)):
    if not payLoad.adminToken == config.settings.ADMIN_TOKEN_FOR_SANITY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not allowed to use this EndPoint !!!")

    record = db.query(models.User.id).filter(models.User.email == payLoad.email).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email: {payLoad.email} not found")
    #print(f"Data Retrieved from DB: {record}")
    return record
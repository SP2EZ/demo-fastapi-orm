# Path Operations for collecting votes

from fastapi import Depends, status, HTTPException, APIRouter
from .. import schemas, oauth2, models
from ..database_orm import get_db
from sqlalchemy.orm import Session
#from .. import database

router = APIRouter(prefix="/votes", tags=['Votes ORM'])

@router.post("/")
def cast_vote(payLoad: schemas.VoteData, token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db)):
    # Check if post exists
    #existing_post_record = database.cursor.execute(""" SELECT * FROM posts where id = %s """, (payLoad.post_id,)).fetchone()
    existing_post_record = db.query(models.Post).filter(models.Post.id == payLoad.post_id).first()

    if not existing_post_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post: {payLoad.post_id} Not Found")
    # Checking if the Vote Request is new
    #existing_vote_record = database.cursor.execute(""" SELECT * FROM votes where post_id = %s AND user_id = %s """, (payLoad.post_id, token_data.id)).fetchone()
    existing_vote_record = db.query(models.Vote).filter(models.Vote.post_id == payLoad.post_id, models.Vote.user_id == token_data.id).first()
    if not existing_vote_record:
        # Casting New Up-Vote on a Post
        if payLoad.vote_dir:
            #database.cursor.execute(""" INSERT INTO votes (post_id, user_id) VALUES (%s, %s) RETURNING * """, (payLoad.post_id, token_data.id)).fetchone()
            #database.conn.commit()
            payload = payLoad.dict()
            payLoadCopy = payload.copy()
            payLoadCopy.update({"user_id": token_data.id})
            payLoadCopy.pop('vote_dir')
            new_posts = models.Vote(**payLoadCopy)
            db.add(new_posts)
            db.commit()           
            return {"message": "Post Voted"}
    # Else Removing Vote from Existing Post
    if not payLoad.vote_dir:
        # Deleting Entry from Votes Table
        #database.cursor.execute(""" DELETE FROM votes WHERE post_id = %s AND user_id = %s RETURNING * """, (payLoad.post_id, token_data.id)).fetchone()
        #database.conn.commit()
        posts = db.query(models.Vote).filter(models.Vote.post_id == payLoad.post_id, models.Vote.user_id == token_data.id)
        posts.delete(synchronize_session=False)
        db.commit()
        return {"message": "Post Un-Voted"}
    # On receiving duplicate vote request Raise HTTP_409_CONFLICT 
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Already Voted Post : {payLoad.post_id}")
    
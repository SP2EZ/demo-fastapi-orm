# Path Operations for posts

from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy import func
from .. import schemas, oauth2, models
from ..database_orm import get_db
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(prefix="/posts-orm", tags=['Posts ORM'])

# @router.get("/")
# def get_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all()
#     return {"data": posts}

@router.get("/{id}")
def get_posts(id: int, db: Session = Depends(get_db)):
    # record = database.cursor.execute(""" 
    # SELECT P.*, COUNT(V.post_id) likes FROM posts P LEFT JOIN votes V
    # ON P.id = V.post_id
    # WHERE P.id = %s AND P.user_id = %s
    # GROUP BY P.id 
    # """, (id, token_data.id)).fetchone()
    #posts = db.query(models.Post).filter(models.Post.id == id).first()
    posts = db.query(models.Post.id, models.Post.user_id, models.Post.title, models.Post.content, models.Post.published, models.Post.created_at, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).filter(models.Post.id == id, models.Post.user_id == 1).group_by(models.Post.id)
    print(posts)

    record = posts.first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    return record

#@router.get("/", response_model=List[schemas.PostResponseWithLikes])
@router.get("/", response_model=List[schemas.PostResponseWithLikes])
def get_posts( db: Session = Depends(get_db), limit: int = 5, skip: int = 0, search: str = ""):
    search = "%"+search+"%"

    # record = database.cursor.execute(""" 
    # SELECT P.*, COUNT(V.post_id) likes FROM posts P LEFT JOIN votes V 
    # ON P.id = V.post_id
    # WHERE P.user_id = %s AND P.title ILIKE %s
    # GROUP BY P.id
    # LIMIT %s OFFSET %s 
    # """, (token_data.id, search, limit, skip)).fetchall()

    # record = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id).filter(models.Post.user_id == 1, models.Post.title.ilike(search)).group_by(models.Post.id).limit(5).offset(0)
    record = db.query(models.Post.id, models.Post.user_id, models.Post.title, models.Post.content, models.Post.published, models.Post.created_at, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).filter(models.Post.user_id == 1, models.Post.title.ilike(search)).group_by(models.Post.id).limit(5).offset(0)
    print(record)
    db_record = record.all()
    #return {"data": "CHOAP !!!"}
    return db_record

@router.post("/")
def create_posts(payLoad: schemas.PostRequest, db: Session = Depends(get_db)):
    payload = payLoad.dict()
    payLoadCopy = payload.copy()
    payLoadCopy.update({"user_id": "1"})
    # new_posts = models.Post(title=payLoad.title, content=payLoad.content, published=payLoad.published)
    # new_posts = models.Post(**payLoad.dict()) is similar to above comment
    new_posts = models.Post(**payLoadCopy)
    db.add(new_posts)
    db.commit()
    # refresh will retrieves the newly created post and stores it back to variable new_posts
    db.refresh(new_posts)
    return {"post added": new_posts}

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.id == id)
    if not posts.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    posts.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_posts(payLoad: schemas.PostRequest, id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.id == id)
    if not posts.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    
    posts.update(payLoad.dict(), synchronize_session=False)
    db.commit()
    # refresh will retrieves the newly created post and stores it back to variable new_posts
    #db.refresh(posts)
    return {"post updated": posts.first()}
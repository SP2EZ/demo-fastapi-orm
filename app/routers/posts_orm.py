# Path Operations for posts

from fastapi import Depends, Response, status, HTTPException, APIRouter
from .. import schemas, oauth2, models
from typing import List
from ..database_orm import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
#from .. import database

router = APIRouter(prefix="/posts", tags=['Posts ORM'])

# By adding -> limit: int = 5 in our get_posts, we are setting up Query Paramater
# Anything after the question mark in the website "www.website.com/posts?limit=3" is key value pair that allows users to filter the results of a request
# In our case "limit", "skip" & "search" is the Query Paramater
# int = 5 means we setting default value of limit
@router.get("/", response_model=List[schemas.PostResponseWithLikes])
def get_posts(token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db), limit: int = 5, skip: int = 0, search: str = ""):
    search = "%"+search+"%"

    # SQL Equivalent
    # record = database.cursor.execute(""" 
    # SELECT P.*, COUNT(V.post_id) likes FROM posts P LEFT JOIN votes V 
    # ON P.id = V.post_id
    # WHERE P.user_id = %s AND P.title ILIKE %s
    # GROUP BY P.id
    # LIMIT %s OFFSET %s 
    # """, (token_data.id, search, limit, skip)).fetchall()
    
    record = db.query(models.Post.id, models.Post.user_id, models.Post.title, models.Post.content, models.Post.published, models.Post.created_at, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).filter(models.Post.user_id == token_data.id, models.Post.title.ilike(search)).group_by(models.Post.id).limit(5).offset(0)
    #print(record)
    orm_record = record.all()
    #print(f"Typeof Data Received {type(record)} \n Data Retrieved from DB: {record}")
    return orm_record

# Adding token_data: int = Depends(oauth2.get_current_user_id) in the below function forces user to provide Token so they are Authorized before they can create a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(payLoad: schemas.PostRequest, token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db)):
    # Getting Email using User ID from DB
    # current_user = oauth2.get_current_user(token_data.id)

    # SQL Equivalent
    # record = database.cursor.execute(""" INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING * """, (payLoad.title, payLoad.content, payLoad.published, token_data.id)).fetchone()
    # database.conn.commit()
    payload = payLoad.dict()
    payLoadCopy = payload.copy()
    payLoadCopy.update({"user_id": token_data.id})
    # new_posts = models.Post(title=payLoad.title, content=payLoad.content, published=payLoad.published)
    # new_posts = models.Post(**payLoad.dict()) is similar to above comment
    new_posts = models.Post(**payLoadCopy)
    db.add(new_posts)
    db.commit()
    # refresh will retrieves the newly created post and stores it back to variable new_posts
    db.refresh(new_posts)

    return new_posts

@router.get("/{id}", response_model=schemas.PostResponseWithLikes)
def get_post(id: int, token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db)):
    # SQL Equivalent
    # record = database.cursor.execute(""" 
    # SELECT P.*, COUNT(V.post_id) likes FROM posts P LEFT JOIN votes V
    # ON P.id = V.post_id
    # WHERE P.id = %s AND P.user_id = %s
    # GROUP BY P.id 
    # """, (id, token_data.id)).fetchone()

    posts = db.query(models.Post.id, models.Post.user_id, models.Post.title, models.Post.content, models.Post.published, models.Post.created_at, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).filter(models.Post.id == id, models.Post.user_id == token_data.id).group_by(models.Post.id)
    #print(posts)
    orm_record = posts.first()
    if not orm_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    #print(f"Data Retrieved from DB: {record}")
    return orm_record

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db)):
    # SQL Equivalent
    # delete_record = database.cursor.execute(""" DELETE FROM posts WHERE id = %s AND user_id = %s returning * """, (id, token_data.id)).fetchone()
    # # print(f"Post Deleted : {delete_record}")
    # database.conn.commit()

    posts = db.query(models.Post).filter(models.Post.id == id, models.Post.user_id == token_data.id)
    if not posts.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    posts.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, payLoad: schemas.PostRequest, token_data: int = Depends(oauth2.get_current_user_id), db: Session = Depends(get_db)):
    # SQL Equivalent
    # update_record = database.cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s AND user_id = %s RETURNING *""", (payLoad.title, payLoad.content, payLoad.published, id, token_data.id)).fetchone()
    # #print(f"Updated Post in DB : {update_record}")
    # database.conn.commit()

    posts = db.query(models.Post).filter(models.Post.id == id, models.Post.user_id == token_data.id)
    if not posts.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post id: {id} not found")
    
    posts.update(payLoad.dict(), synchronize_session=False)
    db.commit()
    # refresh will retrieves the newly created post and stores it back to variable new_posts
    #db.refresh(posts)
    return posts.first()
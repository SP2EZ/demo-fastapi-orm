# Schema is like a contract of what data should look like. Schema (Pydantic Models in this script) defines & validates the structure of a request & response.
# Below Class Defintions are schemas.

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PostRequest(BaseModel):
    title: str
    content: str
    published: bool = True

    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, otherwise if try to validate simple ORM(SQLAlchemy) model with pydantic then it will throw an error
    class Config:
        orm_mode = True

class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    class Config:
        orm_mode = True

class PostResponseWithLikes(PostResponse):
    likes: int
    class Config:
        orm_mode = True

class UserRequest(BaseModel):
    email: EmailStr
    password: str
    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    email: str
    created_at: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    class Config:
        orm_mode = True
    
class TokenData(BaseModel):
    id: Optional[str] = None
    class Config:
        orm_mode = True

class VoteData(BaseModel):
    post_id: int
    vote_dir: bool
    class Config:
        orm_mode = True
# schemas dictate data types for transmission (request and response)
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from pydantic.types import conint


# Pydantic data models used for requests and responses
# checks that the data passed matches the data fields and types (some datatype conversion will automatically be tried)

# <-- User Models -->


class UserCreate(BaseModel):
    # builtin email validation through pydantic library
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# <-- Post Models -->


class PostBase(BaseModel):
    title: str
    content: str
    # syntax for data with default value (use Optional typing and default value of None for truly optional data fields)
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserOut

    class Config:
        orm_mode = True
     # this allows the pydantic models to work properly with the sqlAlchemy models


class PostVotesResponse(BaseModel):
    Post: PostResponse
    votes: int
# <-- Token Models -->


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None

# <-- Vote Models -->


class Vote(BaseModel):
    post_id: int
    direction: conint(le=1)

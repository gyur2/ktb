# schemas.py
from typing import Optional, List
from pydantic import BaseModel


# ---------- 댓글 ----------
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    comment_id: int
    user_id: int

    class Config:
        orm_mode = True


# ---------- 게시글 ----------
class PostBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    post_id: int
    user_id: int
    like_count: int
    view_count: int

    class Config:
        orm_mode = True


class PostDetail(PostRead):
    comments: List[CommentRead] = []


# ---------- 유저 ----------
class UserBase(BaseModel):
    email: str
    nickname: str
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    user_id: int

    class Config:
        orm_mode = True

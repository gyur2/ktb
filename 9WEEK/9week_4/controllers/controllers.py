# controllers/controllers.py
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional

from models.models import (
    create_user, get_user_by_email, get_user_by_id, update_user_profile,
    update_user_password, create_post, get_post, list_posts, update_post,
    delete_post, create_comment, update_comment
)

class SignupRequest(BaseModel):
    email: str
    password: str
    nickname: str
    profile_image: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class CreatePostRequest(BaseModel):
    title: str
    content: str
    image: Optional[str] = None


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None


class CreateCommentRequest(BaseModel):
    content: str


class UpdateCommentRequest(BaseModel):
    content: str


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    profile_image: Optional[str] = None


class UpdatePasswordRequest(BaseModel):
    password: str


# 유저

def signup_controller(body: SignupRequest):
    if get_user_by_email(body.email):
        raise HTTPException(400, {"message": "email_duplicate", "data": None})

    user = create_user(body.email, body.password, body.nickname, body.profile_image)
    return {"message": "register_success", "data": {"user_id": user["user_id"]}}


def login_controller(body: LoginRequest):
    user = get_user_by_email(body.email)
    if user is None or user["password"] != body.password:
        raise HTTPException(401, {"message": "invalid_credentials", "data": None})

    return {
        "message": "login_success",
        "data": {"user_id": user["user_id"], "access_token": "dummy_token"}
    }


def get_profile_controller(user_id: int = 1):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(401, {"message": "unauthorized", "data": None})

    return {
        "message": "get_profile_success",
        "data": {
            "user_id": user["user_id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profile_image": user["profile_image"],
        }
    }


def update_profile_controller(body: UpdateProfileRequest, user_id: int = 1):
    updated = update_user_profile(user_id, body.nickname, body.profile_image)
    if updated is None:
        raise HTTPException(401, {"message": "unauthorized", "data": None})

    return {"message": "update_profile_success", "data": {"user_id": user_id}}


def update_password_controller(body: UpdatePasswordRequest, user_id: int = 1):
    updated = update_user_password(user_id, body.password)
    if updated is None:
        raise HTTPException(401, {"message": "unauthorized", "data": None})

    return {"message": "update_password_success", "data": {"user_id": user_id}}


# 게시글 

def create_post_controller(body: CreatePostRequest, user_id: int = 1):
    post = create_post(user_id, body.title, body.content, body.image)
    return {"message": "create_post_success", "data": {"post_id": post["post_id"]}}


def list_posts_controller(cursor: Optional[int], limit: int):
    posts = list_posts(cursor, limit)
    return {
        "message": "get_posts_success",
        "data": {"posts": posts, "has_next": False, "next_cursor": None}
    }


def post_detail_controller(post_id: int, current_user_id: int = 1):
    detail = get_post(post_id, current_user_id)

    if detail is None:
        raise HTTPException(404, {"message": "post_not_found", "data": None})

    return {
        "message": "get_post_detail_success",
        "data": detail
    }


def update_post_controller(post_id: int, body: UpdatePostRequest, user_id: int = 1):
    post = get_post(post_id)
    if post is None:
        raise HTTPException(404, {"message": "post_not_found", "data": None})

    if post["user_id"] != user_id:
        raise HTTPException(403, {"message": "forbidden", "data": None})

    update_post(post_id, body.title, body.content, body.image)
    return {"message": "update_post_success", "data": {"post_id": post_id}}


def delete_post_controller(post_id: int, user_id: int = 1):
    post = get_post(post_id)
    if post is None:
        raise HTTPException(404, {"message": "post_not_found", "data": None})
    if post["user_id"] != user_id:
        raise HTTPException(403, {"message": "forbidden", "data": None})

    delete_post(post_id)
    return {"message": "delete_post_success", "data": None}


# 댓글 
def create_comment_controller(post_id: int, body: CreateCommentRequest, user_id: int = 1):
    comment = create_comment(post_id, user_id, body.content)
    if comment is None:
        raise HTTPException(404, {"message": "post_not_found", "data": None})

    return {"message": "create_comment_success", "data": comment}


def update_comment_controller(post_id: int, comment_id: int, body: UpdateCommentRequest, user_id: int = 1):
    updated = update_comment(post_id, comment_id, body.content)
    if updated is None:
        raise HTTPException(404, {"message": "comment_not_found", "data": None})

    return {"message": "update_comment_success", "data": updated}

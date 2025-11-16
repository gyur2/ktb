# controllers/controllers.py
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional

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


def signup_controller(body: SignupRequest):
    return {
        "message": "register_success",
        "data": {"user_id": 1}
    }


def login_controller(body: LoginRequest):
    if not body.email or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "invalid_request", "data": None}
        )
    return {
        "message": "login_success",
        "data": {
            "user_id": 1,
            "access_token": "access_token_string"
        }
    }


def get_profile_controller():
    return {
        "message": "get_profile_success",
        "data": {
            "user_id": 1,
            "email": "test@startup.com",
            "nickname": "tester",
            "profile_image": "https://image.kr/img.jpg"
        }
    }


def update_profile_controller(body: UpdateProfileRequest):
    if body.nickname is None and body.profile_image is None:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )
    return {
        "message": "update_profile_success",
        "data": {"user_id": 1}
    }


def update_password_controller(body: UpdatePasswordRequest):
    if len(body.password) < 8:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )
    return {
        "message": "update_password_success",
        "data": {"user_id": 1}
    }


# ---- Posts ----

def get_posts_controller(cursor: Optional[str], limit: int):
    return {
        "message": "get_posts_success",
        "data": {
            "posts": [
                {
                    "post_id": 1,
                    "title": "첫 글",
                    "writer": "tester",
                    "like_count": 0,
                    "view_count": 0,
                    "comment_count": 0,
                    "created_at": "2021-01-01"
                }
            ],
            "next_cursor": "next_cursor_token",
            "has_next": True
        }
    }


def get_post_detail_controller(post_id: int):
    if post_id <= 0:
        raise HTTPException(
            status_code=404,
            detail={"message": "post_not_found", "data": None}
        )
    return {
        "message": "get_post_detail_success",
        "data": {
            "post": {
                "post_id": post_id,
                "title": "첫 글",
                "writer": "tester",
                "image": "https://image.kr/post.jpg",
                "writer_image": "https://image.kr/profile.jpg",
                "created_at": "2021-01-01",
                "content": "내용입니다",
                "like_count": 10,
                "view_count": 20,
                "comment_count": 1,
                "isowner": True
            },
            "comments": [
                {
                    "comment_id": 1,
                    "comments_writer": "tester",
                    "comments_writer_image": "https://image.kr/img2.jpg",
                    "comments_content": "댓글",
                    "comments_created_at": "2021-01-01",
                    "comments_isowner": True
                }
            ]
        }
    }


def create_post_controller(body: CreatePostRequest):
    if not body.title or not body.content:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )

    return {
        "message": "create_post_success",
        "data": {"post_id": 1}
    }


def update_post_controller(post_id: int, body: UpdatePostRequest):
    if body.title is None and body.content is None and body.image is None:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )

    return {
        "message": "update_post_success",
        "data": {"post_id": post_id}
    }


def delete_post_controller(post_id: int):
    if post_id == 0:
        raise HTTPException(
            status_code=404,
            detail={"message": "post_not_found", "data": None}
        )
    return {
        "message": "delete_post_success",
        "data": None
    }


def toggle_like_controller(post_id: int):
    return {
        "message": "toggle_like_success",
        "data": {
            "post_id": post_id,
            "is_liked": True,
            "like_count": 11
        }
    }


def create_comment_controller(post_id: int, body: CreateCommentRequest):
    if not body.content:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )

    return {
        "message": "create_comment_success",
        "data": {"comment_id": 10, "post_id": post_id}
    }


def update_comment_controller(post_id: int, comment_id: int, body: UpdateCommentRequest):
    if not body.content:
        raise HTTPException(
            status_code=400,
            detail={"message": "invalid_request", "data": None}
        )
    return {
        "message": "update_comment_success",
        "data": {"comment_id": comment_id}
    }

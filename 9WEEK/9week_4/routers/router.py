# routers/router.py
from fastapi import APIRouter, Query

from controllers.controllers import (
    SignupRequest, LoginRequest, CreatePostRequest, UpdatePostRequest,
    CreateCommentRequest, UpdateCommentRequest, UpdateProfileRequest, UpdatePasswordRequest,
    signup_controller, login_controller, get_profile_controller, update_profile_controller,
    update_password_controller, create_post_controller, list_posts_controller,
    post_detail_controller, update_post_controller, delete_post_controller,
    create_comment_controller, update_comment_controller
)

router = APIRouter()


# 유저
@router.post("/users/signup")
def signup(body: SignupRequest):
    return signup_controller(body)


@router.post("/users/login")
def login(body: LoginRequest):
    return login_controller(body)


@router.get("/users/me")
def get_profile():
    return get_profile_controller()


@router.patch("/users/me")
def update_profile(body: UpdateProfileRequest):
    return update_profile_controller(body)


@router.patch("/users/me/password")
def update_password(body: UpdatePasswordRequest):
    return update_password_controller(body)


# 게시글
@router.post("/posts")
def create_post(body: CreatePostRequest):
    return create_post_controller(body)


@router.get("/posts")
def list_posts(cursor: int | None = Query(default=None), limit: int = 10):
    return list_posts_controller(cursor, limit)


@router.get("/posts/{post_id:int}")
def post_detail(post_id: int):
    return post_detail_controller(post_id)


@router.patch("/posts/{post_id:int}")
def update_post(post_id: int, body: UpdatePostRequest):
    return update_post_controller(post_id, body)


@router.delete("/posts/{post_id:int}")
def delete_post(post_id: int):
    return delete_post_controller(post_id)

# 댓글
@router.post("/posts/{post_id:int}/comments")
def create_comment(post_id: int, body: CreateCommentRequest):
    return create_comment_controller(post_id, body)


@router.patch("/posts/{post_id:int}/comments/{comment_id:int}")
def update_comment(post_id: int, comment_id: int, body: UpdateCommentRequest):
    return update_comment_controller(post_id, comment_id, body)

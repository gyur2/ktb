# routers/router.py
from fastapi import APIRouter, Query, status
from controllers.controllers import (
    # user DTO + controller
    SignupRequest, LoginRequest, UpdateProfileRequest, UpdatePasswordRequest,
    signup_controller, login_controller, get_profile_controller,
    update_profile_controller, update_password_controller,

    # post DTO + controller
    CreatePostRequest, UpdatePostRequest, CreateCommentRequest, UpdateCommentRequest,
    get_posts_controller, get_post_detail_controller, create_post_controller,
    update_post_controller, delete_post_controller, toggle_like_controller,
    create_comment_controller, update_comment_controller
)


router = APIRouter()


# 유저 

@router.post("/users/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest):
    return signup_controller(body)


@router.post("/users/login")
async def login(body: LoginRequest):
    return login_controller(body)


@router.get("/users/me")
async def get_profile():
    return get_profile_controller()


@router.patch("/users/me")
async def update_profile(body: UpdateProfileRequest):
    return update_profile_controller(body)


@router.patch("/users/me/password")
async def update_password(body: UpdatePasswordRequest):
    return update_password_controller(body)


# 게시글 

@router.get("/posts")
async def get_posts(cursor: str | None = Query(default=None),
                    limit: int = Query(default=10, ge=1, le=50)):
    return get_posts_controller(cursor, limit)


@router.get("/posts/{post_id}")
async def get_post_detail(post_id: int):
    return get_post_detail_controller(post_id)


@router.post("/posts")
async def create_post(body: CreatePostRequest):
    return create_post_controller(body)


@router.patch("/posts/{post_id}")
async def update_post(post_id: int, body: UpdatePostRequest):
    return update_post_controller(post_id, body)


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    return delete_post_controller(post_id)


@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: int):
    return toggle_like_controller(post_id)


@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, body: CreateCommentRequest):
    return create_comment_controller(post_id, body)


@router.patch("/posts/{post_id}/comments/{comment_id}")
async def update_comment(post_id: int, comment_id: int, body: UpdateCommentRequest):
    return update_comment_controller(post_id, comment_id, body)

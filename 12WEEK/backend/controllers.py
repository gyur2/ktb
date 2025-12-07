# controllers.py
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth import create_access_token
from models import User, Post, Comment


# ---------- 요청 바디용 Pydantic ----------

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
    
class ToggleLikeRequest(BaseModel):
    is_like: bool

# ========== 유저 ==========

def signup_controller(db: Session, body: SignupRequest):
    # 이메일 중복
    existing_email = db.query(User).filter(User.email == body.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="email_duplicate")

    # 닉네임 중복
    existing_nickname = db.query(User).filter(User.nickname == body.nickname).first()
    if existing_nickname:
        raise HTTPException(status_code=400, detail="nickname_duplicate")

    user = User(
        email=body.email,
        password=body.password,  # 실제 서비스라면 해시 필요
        nickname=body.nickname,
        profile_image=body.profile_image,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "register_success", "data": {"user_id": user.user_id}}

def login_controller(db, body: LoginRequest):
    user = db.query(User).filter(User.email == body.email).first()

    if user is None or user.password != body.password:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    access_token = create_access_token({"user_id": user.user_id})

    return {
        "message": "login_success",
        "data": {
            "user_id": user.user_id,
            "access_token": access_token,
        },
    }

def get_profile_controller(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    return {
        "message": "get_profile_success",
        "data": {
            "user_id": user.user_id,
            "email": user.email,
            "nickname": user.nickname,
            "profile_image": user.profile_image,
        },
    }


def update_profile_controller(db: Session, body: UpdateProfileRequest, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    if body.nickname is not None:
        # 닉네임 중복 체크
        exists = (
            db.query(User)
            .filter(User.nickname == body.nickname, User.user_id != user_id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="nickname_duplicate")
        user.nickname = body.nickname

    if body.profile_image is not None:
        user.profile_image = body.profile_image

    db.commit()
    db.refresh(user)

    return {"message": "update_profile_success", "data": {"user_id": user.user_id}}


def update_password_controller(db: Session, body: UpdatePasswordRequest, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    user.password = body.password  # 실제 서비스라면 해시 필요
    db.commit()

    return {"message": "update_password_success", "data": {"user_id": user.user_id}}


# ========== 게시글 ==========

def create_post_controller(db: Session, body: CreatePostRequest, user_id: int):
    post = Post(
        user_id=user_id,
        title=body.title,
        content=body.content,
        image=body.image,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"message": "create_post_success", "data": {"post_id": post.post_id}}



def list_posts_controller(db: Session, cursor: Optional[int], limit: int):
    # Post + User 조인
    q = (
        db.query(Post, User)
        .join(User, Post.user_id == User.user_id)
        .order_by(Post.post_id.desc())
    )

    if cursor is not None:
        q = q.filter(Post.post_id < cursor)

    rows = q.limit(limit).all()   # rows: [(Post, User), (Post, User), ...]

    has_next = False
    next_cursor = None
    if len(rows) == limit:
        has_next = True
        next_cursor = rows[-1][0].post_id   # 마지막 Post의 id

    post_dicts = []
    for post, user in rows:
        post_dicts.append(
            {
                "post_id": post.post_id,
                "user_id": post.user_id,
                "user_nickname": user.nickname,
                "title": post.title,
                "content": post.content,
                "image": post.image,
                "like_count": post.like_count,
                "view_count": post.view_count,
            }
        )

    return {
        "message": "get_posts_success",
        "data": {
            "posts": post_dicts,
            "has_next": has_next,
            "next_cursor": next_cursor,
        },
    }



def post_detail_controller(db: Session, post_id: int):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post_not_found")

    # [수정] 개발 환경 무한 새로고침 방지를 위해 조회수 증가 로직 주석 처리
    # post.view_count = (post.view_count or 0) + 1
    # db.commit()
    # db.refresh(post)

    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.comment_id.asc())
        .all()
    )

    comment_dicts = [
        {
            "comment_id": c.comment_id,
            "user_id": c.user_id,
            "content": c.content,
        }
        for c in comments
    ]

    detail = {
        "post_id": post.post_id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "image": post.image,
        "like_count": post.like_count,
        "view_count": post.view_count,
        "comments": comment_dicts,
    }

    return {"message": "get_post_detail_success", "data": detail}


def update_post_controller(db: Session, post_id: int, body: UpdatePostRequest, user_id: int):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post_not_found")

    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    if body.title is not None:
        post.title = body.title
    if body.content is not None:
        post.content = body.content
    if body.image is not None:
        post.image = body.image

    db.commit()
    db.refresh(post)

    return {"message": "update_post_success", "data": {"post_id": post.post_id}}


def delete_post_controller(db: Session, post_id: int, user_id: int):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post_not_found")

    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    db.delete(post)
    db.commit()

    return {"message": "delete_post_success", "data": None}

def toggle_like_controller(db: Session, post_id: int, is_like: bool):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post_not_found")

    delta = 1 if is_like else -1
    new_count = (post.like_count or 0) + delta
    if new_count < 0:
        new_count = 0

    post.like_count = new_count
    db.commit()
    db.refresh(post)

    return {
        "message": "toggle_like_success",
        "data": {
            "post_id": post.post_id,
            "like_count": post.like_count,
        },
    }

# ========== 댓글 ==========

def create_comment_controller(db: Session, post_id: int, body: CreateCommentRequest, user_id: int):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post_not_found")

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "message": "create_comment_success",
        "data": {
            "comment_id": comment.comment_id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
        },
    }


def update_comment_controller(db: Session, post_id: int, comment_id: int, body: UpdateCommentRequest, user_id: int):
    comment = (
        db.query(Comment)
        .filter(Comment.comment_id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if comment is None:
        raise HTTPException(status_code=404, detail="comment_not_found")

    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    comment.content = body.content
    db.commit()
    db.refresh(comment)

    return {
        "message": "update_comment_success",
        "data": {
            "comment_id": comment.comment_id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
        },
    }
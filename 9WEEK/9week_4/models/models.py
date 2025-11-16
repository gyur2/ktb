# models/models.py
from typing import Dict, Optional
from users_dict import users, next_user_id #더미데이터
from posts_dict import posts, next_post_id #더미데이터 
from comments_dict import comments, next_comment_id #더미데이터


# 유저 

def create_user(email: str, password: str, nickname: str, profile_image: Optional[str]):
    global next_user_id
    user = {
        "user_id": next_user_id,
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image": profile_image
    }
    users[next_user_id] = user
    next_user_id += 1
    return user


def get_user_by_email(email: str):
    for user in users.values():
        if user["email"] == email:
            return user
    return None


def get_user_by_id(user_id: int):
    return users.get(user_id)


def update_user_profile(user_id: int, nickname: Optional[str], profile_image: Optional[str]):
    user = users.get(user_id)
    if user is None:
        return None
    if nickname is not None:
        user["nickname"] = nickname
    if profile_image is not None:
        user["profile_image"] = profile_image
    return user


def update_user_password(user_id: int, new_password: str):
    user = users.get(user_id)
    if user is None:
        return None
    user["password"] = new_password
    return user


# 게시글

def create_post(user_id: int, title: str, content: str, image: Optional[str]):
    global next_post_id
    post = {
        "post_id": next_post_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "image": image,
        "like_count": 0,
        "view_count": 0,
        "comments": [],
    }
    posts[next_post_id] = post
    next_post_id += 1
    return post


def list_posts(cursor: Optional[int], limit: int):
    sorted_posts = sorted(posts.values(), key=lambda x: x["post_id"])
    return sorted_posts[:limit]


def update_post(post_id: int, title: Optional[str], content: Optional[str], image: Optional[str]):
    post = posts.get(post_id)
    if post is None:
        return None

    if title is not None:
        post["title"] = title
    if content is not None:
        post["content"] = content
    if image is not None:
        post["image"] = image
    return post

def get_post(post_id: int, current_user_id: int = 1):
    post = posts.get(post_id)
    if post is None:
        return None

    writer = users.get(post["user_id"])

    detail = {
        "post_id": post["post_id"],
        "user_id": post["user_id"],
        "title": post["title"],
        "content": post["content"],
        "image": post["image"],
        "like_count": post.get("like_count", 0),
        "view_count": post.get("view_count", 0),
        "comments": []
    }
    for c in comments.values():
        if c["post_id"] == post_id:
            detail["comments"].append({
                "comment_id": c["comment_id"],
                "user_id": c["user_id"],
                "content": c["content"]
            })

    return detail

def delete_post(post_id: int):
    return posts.pop(post_id, None)


# 댓글

def create_comment(post_id: int, user_id: int, content: str):
    global next_comment_id

    if post_id not in posts:
        return None

    comment = {
        "comment_id": next_comment_id,
        "post_id": post_id,
        "user_id": user_id,
        "content": content,
    }

    comments[next_comment_id] = comment
    posts[post_id]["comments"].append(comment)

    next_comment_id += 1
    return comment


def update_comment(post_id: int, comment_id: int, content: str):
    comment = comments.get(comment_id)
    if comment is None or comment["post_id"] != post_id:
        return None

    comment["content"] = content
    return comment

from fastapi import APIRouter, Query, Response, status

from app.modules.auth.dependencies import CurrentUser, DatabaseSession
from app.modules.posts.schemas import (
    CommentCreate,
    CommentUpdate,
    EngagementRead,
    PostCreate,
    PostRead,
    PostUpdate,
)
from app.modules.posts.service import (
    create_comment,
    create_post,
    delete_comment,
    delete_post,
    feed,
    read_post,
    set_like,
    set_share,
    update_comment,
    update_post,
    user_posts,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/feed", response_model=list[PostRead])
def read_feed(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return feed(db, current_user, limit, offset)


@router.get("/users/{username}", response_model=list[PostRead])
def read_user_posts(username: str, db: DatabaseSession, current_user: CurrentUser):
    return user_posts(db, current_user, username)


@router.post("", response_model=PostRead, status_code=201)
def publish_post(data: PostCreate, db: DatabaseSession, current_user: CurrentUser):
    return create_post(db, current_user, data)


@router.get("/{post_id}", response_model=PostRead)
def read_single_post(post_id: int, db: DatabaseSession, current_user: CurrentUser):
    return read_post(db, current_user, post_id)


@router.patch("/{post_id}", response_model=PostRead)
def edit_post(post_id: int, data: PostUpdate, db: DatabaseSession, current_user: CurrentUser):
    return update_post(db, current_user, post_id, data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_post(post_id: int, db: DatabaseSession, current_user: CurrentUser) -> Response:
    delete_post(db, current_user, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}/like", response_model=EngagementRead)
def like_post(post_id: int, db: DatabaseSession, current_user: CurrentUser):
    active, count = set_like(db, current_user, post_id, True)
    return EngagementRead(active=active, count=count)


@router.delete("/{post_id}/like", response_model=EngagementRead)
def unlike_post(post_id: int, db: DatabaseSession, current_user: CurrentUser):
    active, count = set_like(db, current_user, post_id, False)
    return EngagementRead(active=active, count=count)


@router.put("/{post_id}/share", response_model=EngagementRead)
def share_post(post_id: int, db: DatabaseSession, current_user: CurrentUser):
    active, count = set_share(db, current_user, post_id, True)
    return EngagementRead(active=active, count=count)


@router.delete("/{post_id}/share", response_model=EngagementRead)
def unshare_post(post_id: int, db: DatabaseSession, current_user: CurrentUser):
    active, count = set_share(db, current_user, post_id, False)
    return EngagementRead(active=active, count=count)


@router.post("/{post_id}/comments", response_model=PostRead, status_code=201)
def add_comment(post_id: int, data: CommentCreate, db: DatabaseSession, current_user: CurrentUser):
    return create_comment(db, current_user, post_id, data)


@router.patch("/comments/{comment_id}", response_model=PostRead)
def edit_comment(
    comment_id: int,
    data: CommentUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    return update_comment(db, current_user, comment_id, data.content)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(comment_id: int, db: DatabaseSession, current_user: CurrentUser) -> Response:
    delete_comment(db, current_user, comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

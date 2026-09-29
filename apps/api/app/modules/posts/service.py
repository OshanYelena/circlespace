from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.friendships.models import Friendship
from app.modules.posts.models import Comment, Like, Post, Share
from app.modules.posts.schemas import CommentCreate, CommentRead, PostCreate, PostRead, PostUpdate
from app.modules.users.models import User
from app.modules.users.schemas import PublicUserRead
from app.modules.users.service import get_user_by_username


def _post_query():
    return select(Post).options(
        selectinload(Post.author).selectinload(User.profile),
        selectinload(Post.comments).selectinload(Comment.author).selectinload(User.profile),
        selectinload(Post.likes),
        selectinload(Post.shares),
    )


def _get_post(db: Session, post_id: int) -> Post:
    post = db.scalar(_post_query().where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def serialize_post(post: Post, viewer_id: int) -> PostRead:
    return PostRead(
        id=post.id,
        author=PublicUserRead.model_validate(post.author),
        content=post.content,
        image_url=post.image_url,
        created_at=post.created_at,
        updated_at=post.updated_at,
        comments=[
            CommentRead(
                id=comment.id,
                author=PublicUserRead.model_validate(comment.author),
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment in post.comments
        ],
        like_count=len(post.likes),
        share_count=len(post.shares),
        viewer_liked=any(like.user_id == viewer_id for like in post.likes),
        viewer_shared=any(share.user_id == viewer_id for share in post.shares),
    )


def create_post(db: Session, user: User, data: PostCreate) -> PostRead:
    post = Post(
        author_id=user.id,
        title=data.content.strip().splitlines()[0][:200],
        content=data.content,
        image_url=str(data.image_url) if data.image_url else None,
    )
    db.add(post)
    db.commit()
    return serialize_post(_get_post(db, post.id), user.id)


def read_post(db: Session, user: User, post_id: int) -> PostRead:
    return serialize_post(_get_post(db, post_id), user.id)


def update_post(db: Session, user: User, post_id: int, data: PostUpdate) -> PostRead:
    post = _get_post(db, post_id)
    if post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(post, field, str(value) if field == "image_url" and value else value)
    db.commit()
    return serialize_post(_get_post(db, post_id), user.id)


def delete_post(db: Session, user: User, post_id: int) -> None:
    post = _get_post(db, post_id)
    if post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    db.delete(post)
    db.commit()


def feed(db: Session, user: User, limit: int, offset: int) -> list[PostRead]:
    friendships = db.scalars(
        select(Friendship).where(
            or_(Friendship.user_low_id == user.id, Friendship.user_high_id == user.id)
        )
    )
    visible_ids = {user.id}
    for friendship in friendships:
        visible_ids.add(
            friendship.user_high_id if friendship.user_low_id == user.id else friendship.user_low_id
        )
    posts = db.scalars(
        _post_query()
        .where(Post.author_id.in_(visible_ids))
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return [serialize_post(post, user.id) for post in posts]


def user_posts(db: Session, viewer: User, username: str) -> list[PostRead]:
    author = get_user_by_username(db, username)
    posts = db.scalars(
        _post_query()
        .where(Post.author_id == author.id)
        .order_by(Post.created_at.desc(), Post.id.desc())
    )
    return [serialize_post(post, viewer.id) for post in posts]


def set_like(db: Session, user: User, post_id: int, active: bool) -> tuple[bool, int]:
    post = _get_post(db, post_id)
    like = db.scalar(select(Like).where(Like.post_id == post_id, Like.user_id == user.id))
    if active and not like:
        db.add(Like(post_id=post_id, user_id=user.id))
    elif not active and like:
        db.delete(like)
    db.commit()
    count = db.scalar(select(func.count()).select_from(Like).where(Like.post_id == post.id)) or 0
    return active, count


def set_share(db: Session, user: User, post_id: int, active: bool) -> tuple[bool, int]:
    post = _get_post(db, post_id)
    share = db.scalar(select(Share).where(Share.post_id == post_id, Share.user_id == user.id))
    if active and not share:
        db.add(Share(post_id=post_id, user_id=user.id))
    elif not active and share:
        db.delete(share)
    db.commit()
    count = db.scalar(select(func.count()).select_from(Share).where(Share.post_id == post.id)) or 0
    return active, count


def create_comment(db: Session, user: User, post_id: int, data: CommentCreate) -> PostRead:
    _get_post(db, post_id)
    db.add(Comment(post_id=post_id, author_id=user.id, content=data.content))
    db.commit()
    return serialize_post(_get_post(db, post_id), user.id)


def update_comment(db: Session, user: User, comment_id: int, content: str) -> PostRead:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    comment.content = content
    db.commit()
    return serialize_post(_get_post(db, comment.post_id), user.id)


def delete_comment(db: Session, user: User, comment_id: int) -> None:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    db.delete(comment)
    db.commit()

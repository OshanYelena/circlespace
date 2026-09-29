from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.modules.articles.models import Notification
from app.modules.articles.schemas import ArticleCreate, ArticleRead
from app.modules.posts.models import Comment, Like, Post
from app.modules.users.models import User
from app.modules.users.schemas import PublicUserRead


def _article_query():
    return select(Post).options(
        selectinload(Post.author).selectinload(User.profile),
        selectinload(Post.likes),
        selectinload(Post.comments),
    )


def _get_article(db: Session, article_id: int) -> Post:
    article = db.scalar(_article_query().where(Post.id == article_id))
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


def _serialize(article: Post) -> ArticleRead:
    return ArticleRead(
        id=article.id,
        author=PublicUserRead.model_validate(article.author),
        title=article.title,
        content=article.content,
        view_count=article.view_count,
        like_count=len(article.likes),
        comment_count=len(article.comments),
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def create_article(db: Session, user: User, data: ArticleCreate) -> ArticleRead:
    article = Post(author_id=user.id, title=data.title, content=data.content)
    db.add(article)
    db.commit()
    return _serialize(_get_article(db, article.id))


def read_article(db: Session, article_id: int) -> ArticleRead:
    return _serialize(_get_article(db, article_id))


def list_feed(db: Session, limit: int, offset: int) -> list[ArticleRead]:
    articles = db.scalars(
        _article_query()
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_serialize(article) for article in articles]


def search_articles(db: Session, query: str, limit: int) -> list[ArticleRead]:
    pattern = f"%{query}%"
    articles = db.scalars(
        _article_query()
        .where((Post.title.ilike(pattern)) | (Post.content.ilike(pattern)))
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(limit)
    )
    return [_serialize(article) for article in articles]


def increment_view(db: Session, article_id: int) -> int:
    count = db.scalar(
        update(Post)
        .where(Post.id == article_id)
        .values(view_count=Post.view_count + 1)
        .returning(Post.view_count)
    )
    if count is None:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    db.commit()
    return count


def like_article(db: Session, user: User, article_id: int) -> tuple[int, bool]:
    article = _get_article(db, article_id)
    existing = db.scalar(select(Like).where(Like.post_id == article_id, Like.user_id == user.id))
    created = existing is None
    if created:
        db.add(Like(post_id=article_id, user_id=user.id))
        if article.author_id != user.id:
            db.add(
                Notification(
                    user_id=article.author_id,
                    type="article_liked",
                    reference_id=article_id,
                )
            )
        db.commit()
    count = db.scalar(select(func.count()).select_from(Like).where(Like.post_id == article_id)) or 0
    return count, created


def comment_on_article(db: Session, user: User, article_id: int, content: str) -> int:
    article = _get_article(db, article_id)
    comment = Comment(post_id=article_id, author_id=user.id, content=content)
    db.add(comment)
    if article.author_id != user.id:
        db.add(
            Notification(
                user_id=article.author_id,
                type="article_commented",
                reference_id=article_id,
            )
        )
    db.commit()
    return (
        db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id == article_id))
        or 0
    )


def list_notifications(db: Session, user: User, limit: int) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
        )
    )

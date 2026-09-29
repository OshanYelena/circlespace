from fastapi import APIRouter, Query

from app.modules.articles.schemas import (
    ArticleCommentCreate,
    ArticleCreate,
    ArticleInteractionRead,
    ArticleRead,
    NotificationRead,
)
from app.modules.articles.service import (
    comment_on_article,
    create_article,
    increment_view,
    like_article,
    list_feed,
    list_notifications,
    read_article,
    search_articles,
)
from app.modules.auth.dependencies import CurrentUser, DatabaseSession

router = APIRouter(tags=["scaling-lab"])


@router.post("/articles", response_model=ArticleRead, status_code=201)
def publish_article(data: ArticleCreate, db: DatabaseSession, current_user: CurrentUser):
    return create_article(db, current_user, data)


@router.get("/articles/search", response_model=list[ArticleRead])
def search(
    db: DatabaseSession,
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
):
    return search_articles(db, q, limit)


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, db: DatabaseSession):
    return read_article(db, article_id)


@router.get("/feed", response_model=list[ArticleRead])
def get_feed(
    db: DatabaseSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return list_feed(db, limit, offset)


@router.post("/articles/{article_id}/view", response_model=ArticleInteractionRead)
def record_view(article_id: int, db: DatabaseSession):
    return ArticleInteractionRead(article_id=article_id, count=increment_view(db, article_id))


@router.post("/articles/{article_id}/like", response_model=ArticleInteractionRead)
def record_like(article_id: int, db: DatabaseSession, current_user: CurrentUser):
    count, created = like_article(db, current_user, article_id)
    return ArticleInteractionRead(article_id=article_id, count=count, created=created)


@router.post("/articles/{article_id}/comments", response_model=ArticleInteractionRead)
def add_article_comment(
    article_id: int,
    data: ArticleCommentCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    count = comment_on_article(db, current_user, article_id, data.content)
    return ArticleInteractionRead(article_id=article_id, count=count)


@router.get("/notifications", response_model=list[NotificationRead])
def get_notifications(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_notifications(db, current_user, limit)

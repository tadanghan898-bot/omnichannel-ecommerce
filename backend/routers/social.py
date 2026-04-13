"""Social Commerce Router - Posts, Livestream, Influencers"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List

from backend.database import get_db
from backend.models.social import Post, Comment, PostLike, Livestream, Influencer, InfluencerCommission
from backend.core.auth import get_current_user, get_current_user_required, require_role
from backend.core.config import is_module_active

router = APIRouter(prefix="/api/social", tags=["Social Commerce"])


class PostCreate(BaseModel):
    content: str
    media: List[dict] = []
    product_ids: List[int] = []
    hashtags: List[str] = []


@router.get("/posts", response_model=List[dict])
async def list_posts(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    posts = db.execute(
        select(Post).where(Post.is_published == True).order_by(Post.created_at.desc()).offset((page-1)*page_size).limit(page_size)
    ).scalars().all()
    return [{"id": p.id, "content": p.content, "author_id": p.author_id, "like_count": p.like_count, "comment_count": p.comment_count, "created_at": p.created_at.isoformat()} for p in posts]


@router.post("/posts", response_model=dict)
async def create_post(data: PostCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    if not is_module_active("social"):
        raise HTTPException(status_code=403, detail="Social module not active")
    post = Post(author_id=user["id"], **data.model_dump())
    db.add(post)
    db.commit()
    return {"id": post.id, "message": "Post created"}


@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.execute(select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user["id"])).scalar_one_or_none()
    if existing:
        db.delete(existing)
        post.like_count = max(0, post.like_count - 1)
    else:
        like = PostLike(post_id=post_id, user_id=user["id"])
        db.add(like)
        post.like_count += 1
    db.commit()
    return {"likes": post.like_count}


@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, content: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(post_id=post_id, user_id=user["id"], content=content)
    db.add(comment)
    post.comment_count += 1
    db.commit()
    return {"id": comment.id, "message": "Comment added"}


# Livestreams
@router.get("/livestreams", response_model=List[dict])
async def list_livestreams(db: Session = Depends(get_db)):
    streams = db.execute(
        select(Livestream).where(Livestream.status.in_(["scheduled", "live"])).order_by(Livestream.scheduled_at.asc()).limit(20)
    ).scalars().all()
    return [{"id": s.id, "title": s.title, "status": s.status, "viewer_count": s.viewer_count, "host_id": s.host_id} for s in streams]


@router.post("/livestreams", response_model=dict)
async def create_livestream(title: str, description: str = "", scheduled_at=None, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    if not is_module_active("social"):
        raise HTTPException(status_code=403, detail="Social module not active")
    stream = Livestream(host_id=user["id"], title=title, description=description, scheduled_at=scheduled_at, status="scheduled")
    db.add(stream)
    db.commit()
    return {"id": stream.id, "message": "Livestream scheduled"}

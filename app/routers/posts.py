from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse
)


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"]
)
@router.post(
    "",
    response_model=PostResponse
)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db)
):

    new_post = Post(
        title=post.title,
        content=post.content,
        password=post.password
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post
@router.get(
    "",
    response_model=list[PostResponse]
)
def get_posts(
    db: Session = Depends(get_db)
):

    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .all()
    )

    return posts
@router.get(
    "/{post_id}",
    response_model=PostResponse
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )


    if not post:
        raise HTTPException(
            status_code=404,
            detail="게시글 없음"
        )


    post.view_count += 1

    db.commit()
    db.refresh(post)

    return post
@router.put(
    "/{post_id}",
    response_model=PostResponse
)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db)
):

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )


    if not post:
        raise HTTPException(
            status_code=404,
            detail="게시글 없음"
        )


    if post.password != request.password:
        raise HTTPException(
            status_code=400,
            detail="비밀번호 불일치"
        )


    post.title = request.title
    post.content = request.content


    db.commit()
    db.refresh(post)


    return post
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    password: str,
    db: Session = Depends(get_db)
):

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )


    if not post:
        raise HTTPException(
            status_code=404,
            detail="게시글 없음"
        )


    if post.password != password:
        raise HTTPException(
            status_code=400,
            detail="비밀번호 불일치"
        )


    db.delete(post)
    db.commit()


    return {
        "message":"삭제 완료"
    }
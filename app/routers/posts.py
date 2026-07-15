from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.schemas.post import (
    MessageResponse,
    PasswordVerifyResponse,
    PostCreate,
    PostListResponse,
    PostPasswordRequest,
    PostUpdate,
    PostResponse
)


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"]
)
@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
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
    response_model=PostListResponse
)
def get_posts(
    search_type: Literal["title", "content", "title_content"] = "title_content",
    keyword: str | None = Query(default=None, max_length=100),
    sort: Literal["latest", "views"] = "latest",
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=10, le=10),
    db: Session = Depends(get_db)
):
    query = db.query(Post)

    # 검색어의 앞뒤 공백을 제거하고, 빈 문자열은 검색하지 않는다.
    normalized_keyword = keyword.strip() if keyword else None

    if normalized_keyword:
        if search_type == "title":
            query = query.filter(
                Post.title.contains(normalized_keyword)
            )
        elif search_type == "content":
            query = query.filter(
                Post.content.contains(normalized_keyword)
            )
        else:
            query = query.filter(
                or_(
                    Post.title.contains(normalized_keyword),
                    Post.content.contains(normalized_keyword)
                )
            )

    # 검색 조건을 적용한 전체 게시글 수와 전체 페이지 수
    total = query.count()
    total_pages = (total + size - 1) // size

    if sort == "views":
        query = query.order_by(
            Post.view_count.desc(),
            Post.created_at.desc(),
            Post.id.desc()
        )
    else:
        query = query.order_by(
            Post.created_at.desc(),
            Post.id.desc()
        )

    posts = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages,
        "items": posts
    }
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
            detail="게시글을 찾을 수 없습니다."
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
            detail="게시글을 찾을 수 없습니다."
        )


    if post.password != request.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다."
        )


    post.title = request.title
    post.content = request.content


    db.commit()
    db.refresh(post)


    return post


@router.post(
    "/{post_id}/verify-password",
    response_model=PasswordVerifyResponse
)
def verify_post_password(
    post_id: int,
    request: PostPasswordRequest,
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
            detail="게시글을 찾을 수 없습니다."
        )

    if post.password != request.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다."
        )

    return {"verified": True}


@router.delete(
    "/{post_id}",
    response_model=MessageResponse
)
def delete_post(
    post_id: int,
    request: PostPasswordRequest,
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
            detail="게시글을 찾을 수 없습니다."
        )


    if post.password != request.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다."
        )


    db.delete(post)
    db.commit()


    return {
        "message": "게시글이 삭제되었습니다."
    }

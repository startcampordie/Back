from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models import (
    ChatMessage,
    ChatSession,
    Post,
    RegionalContent,
)
from app.routers import chat, contents, home, posts, search


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LocalHub API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ronamdo.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(posts.router)
app.include_router(contents.router)
app.include_router(home.router)
app.include_router(search.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "LocalHub API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
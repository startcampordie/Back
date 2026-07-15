from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contents
from app.routers import posts
from app.core.database import Base, engine
from app.models import Post, RegionalContent
from app.routers import chat
from app.models import ChatSession, ChatMessage

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LocalHub API",
    version="1.0.0",
)
app.include_router(posts.router)
app.include_router(contents.router)
app.include_router(chat.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "LocalHub API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
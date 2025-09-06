from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import timedelta

from database import get_db, engine, Base
from models import User, Post
from schemas import (
    UserCreate, User as UserSchema, UserUpdate,
    PostCreate, Post as PostSchema,
    Token, FollowCreate, FollowResponse
)
from auth import authenticate_user, create_access_token, get_current_user
from crud import (
    create_user, get_user, get_user_by_username, get_user_by_email,
    create_post, get_posts_by_user, get_feed_posts, get_post,
    follow_user, unfollow_user, is_following, get_followers, get_following,
    like_post, unlike_post, get_likes_count, update_user
)
from config import settings

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not create database tables: {e}")
    print("This might be normal if the database is not yet available")

app = FastAPI(title="Chili API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Chili API is running"}

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Chili API is starting up...")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"🔗 Database URL: {settings.DATABASE_URL[:20]}...")
    print(f"🔑 Secret key set: {'Yes' if settings.SECRET_KEY != 'your-secret-key-change-this-in-production' else 'No (using default)'}")
    print("✅ Startup complete!")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Chili API", "docs": "/docs"}

@app.post("/auth/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return create_user(db=db, user=user)

@app.post("/auth/login", response_model=Token)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=UserSchema)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_user(db=db, user_id=current_user.id, user_update=user_update.dict())

@app.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/posts", response_model=PostSchema)
def create_new_post(
    caption: Optional[str] = Form(None),
    media: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Determine media type
    media_type = "image" if media.content_type.startswith("image/") else "video"
    
    # Generate unique filename
    file_extension = os.path.splitext(media.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = media.file.read()
        buffer.write(content)
    
    # Create post
    post_data = PostCreate(caption=caption, media_type=media_type)
    post = create_post(db=db, post=post_data, author_id=current_user.id, media_url=f"/uploads/{unique_filename}")
    
    # Add likes count
    post.likes_count = get_likes_count(db, post.id)
    return post

@app.get("/posts/feed", response_model=List[PostSchema])
def get_user_feed(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    posts = get_feed_posts(db, user_id=current_user.id, skip=skip, limit=limit)
    
    # Add likes count to each post
    for post in posts:
        post.likes_count = get_likes_count(db, post.id)
    
    return posts

@app.get("/posts/{post_id}", response_model=PostSchema)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count = get_likes_count(db, post.id)
    return post

@app.get("/users/{user_id}/posts", response_model=List[PostSchema])
def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    posts = get_posts_by_user(db, user_id=user_id, skip=skip, limit=limit)
    
    # Add likes count to each post
    for post in posts:
        post.likes_count = get_likes_count(db, post.id)
    
    return posts

@app.post("/users/{user_id}/follow", response_model=FollowResponse)
def follow_user_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    follow = follow_user(db, follower_id=current_user.id, following_id=user_id)
    if follow is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    return follow

@app.delete("/users/{user_id}/follow")
def unfollow_user_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = unfollow_user(db, follower_id=current_user.id, following_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    return {"message": "Successfully unfollowed"}

@app.get("/users/{user_id}/followers", response_model=List[UserSchema])
def get_user_followers(user_id: int, db: Session = Depends(get_db)):
    return get_followers(db, user_id=user_id)

@app.get("/users/{user_id}/following", response_model=List[UserSchema])
def get_user_following(user_id: int, db: Session = Depends(get_db)):
    return get_following(db, user_id=user_id)

@app.post("/posts/{post_id}/like")
def like_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    like = like_post(db, user_id=current_user.id, post_id=post_id)
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this post"
        )
    return {"message": "Post liked successfully"}

@app.delete("/posts/{post_id}/like")
def unlike_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = unlike_post(db, user_id=current_user.id, post_id=post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not liked this post"
        )
    return {"message": "Post unliked successfully"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Chili API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

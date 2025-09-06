from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from .models import User, Post, Follow, Like
from .schemas import UserCreate, PostCreate, FollowCreate
from .auth import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user_update.items():
            if value is not None:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Post CRUD operations
def create_post(db: Session, post: PostCreate, author_id: int, media_url: str) -> Post:
    db_post = Post(
        caption=post.caption,
        media_url=media_url,
        media_type=post.media_type,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    return db.query(Post).filter(Post.author_id == user_id).offset(skip).limit(limit).all()

def get_feed_posts(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    # Get posts from users that the current user follows
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == user_id).subquery()
    return db.query(Post).filter(Post.author_id.in_(following_ids)).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

# Follow CRUD operations
def follow_user(db: Session, follower_id: int, following_id: int) -> Optional[Follow]:
    # Check if already following
    existing_follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.following_id == following_id)
    ).first()
    
    if existing_follow:
        return None
    
    db_follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow

def unfollow_user(db: Session, follower_id: int, following_id: int) -> bool:
    follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.following_id == following_id)
    ).first()
    
    if follow:
        db.delete(follow)
        db.commit()
        return True
    return False

def is_following(db: Session, follower_id: int, following_id: int) -> bool:
    follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.following_id == following_id)
    ).first()
    return follow is not None

def get_followers(db: Session, user_id: int) -> List[User]:
    return db.query(User).join(Follow, User.id == Follow.follower_id).filter(Follow.following_id == user_id).all()

def get_following(db: Session, user_id: int) -> List[User]:
    return db.query(User).join(Follow, User.id == Follow.following_id).filter(Follow.follower_id == user_id).all()

# Like CRUD operations
def like_post(db: Session, user_id: int, post_id: int) -> Optional[Like]:
    # Check if already liked
    existing_like = db.query(Like).filter(
        and_(Like.user_id == user_id, Like.post_id == post_id)
    ).first()
    
    if existing_like:
        return None
    
    db_like = Like(user_id=user_id, post_id=post_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

def unlike_post(db: Session, user_id: int, post_id: int) -> bool:
    like = db.query(Like).filter(
        and_(Like.user_id == user_id, Like.post_id == post_id)
    ).first()
    
    if like:
        db.delete(like)
        db.commit()
        return True
    return False

def get_likes_count(db: Session, post_id: int) -> int:
    return db.query(Like).filter(Like.post_id == post_id).count()

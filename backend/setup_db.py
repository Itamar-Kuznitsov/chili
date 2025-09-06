#!/usr/bin/env python3
"""
Database setup script for Chili
"""
import os
import sys
from sqlalchemy import create_engine, text
from config import settings

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to PostgreSQL server (not to the specific database)
    server_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    engine = create_engine(server_url)
    
    # Get database name from the full URL
    db_name = settings.DATABASE_URL.rsplit('/', 1)[1]
    
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": db_name})
            
            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))  # End any transaction
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully!")
            else:
                print(f"✅ Database '{db_name}' already exists!")
                
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def create_tables():
    """Create all tables"""
    from database import engine, Base
    from models import User, Post, Follow, Like
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Setting up Chili database...")
    create_database()
    create_tables()
    print("🎉 Database setup complete!")

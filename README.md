# Chili - Social Media App for Fashion

A cross-platform social media app focused on sharing clothing photos and videos, built with FastAPI and React Native.

## Features

- 📱 Cross-platform (iOS, Android, Web)
- 👤 User authentication and profiles
- 📸 Photo and video sharing
- 🏠 Feed with posts from followed users
- 👥 Follow/unfollow system
- ❤️ Like posts
- 🏷️ Clothing-focused social network

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React Native with Expo
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **File Storage**: Local storage (MVP)

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Expo CLI (`npm install -g @expo/cli`)

## Setup Instructions

### 1. Database Setup

First, create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE chili_db;

# Create user (optional)
CREATE USER chili_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chili_db TO chili_user;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your database credentials

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

This will open the Expo development tools. You can:
- Press `i` to run on iOS simulator
- Press `a` to run on Android emulator
- Press `w` to run in web browser
- Scan the QR code with Expo Go app on your phone

## Project Structure

```
chili/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application file
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # Authentication logic
│   ├── database.py      # Database configuration
│   ├── config.py        # App configuration
│   └── requirements.txt # Python dependencies
├── frontend/            # React Native/Expo frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── screens/     # App screens
│   │   ├── services/    # API services
│   │   ├── contexts/    # React contexts
│   │   └── utils/       # Utility functions
│   ├── App.js          # Main app component
│   └── package.json    # Node dependencies
└── README.md
```

## API Documentation

### Authentication Endpoints

- `POST /auth/register` - Register new user
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "full_name": "string" (optional)
  }
  ```

- `POST /auth/login` - Login user
  ```
  Form data: username, password
  Returns: { "access_token": "string", "token_type": "bearer" }
  ```

### User Endpoints

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/{user_id}` - Get user profile by ID
- `POST /users/{user_id}/follow` - Follow a user
- `DELETE /users/{user_id}/follow` - Unfollow a user
- `GET /users/{user_id}/followers` - Get user's followers
- `GET /users/{user_id}/following` - Get users that user follows

### Post Endpoints

- `POST /posts` - Create new post
  ```
  Form data: caption (optional), media (file)
  ```

- `GET /posts/feed` - Get user's feed (posts from followed users)
- `GET /posts/{post_id}` - Get specific post
- `GET /users/{user_id}/posts` - Get user's posts
- `POST /posts/{post_id}/like` - Like a post
- `DELETE /posts/{post_id}/like` - Unlike a post

## Usage

1. **Register/Login**: Create an account or sign in
2. **Create Posts**: Tap the + button to add photos with captions
3. **Browse Feed**: See posts from users you follow
4. **Interact**: Like posts, follow users
5. **Profile**: View your posts and profile information

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Development

The frontend uses React Native with Expo for cross-platform development. Key features:
- Hot reloading for fast development
- Cross-platform compatibility
- Easy deployment to app stores

## Deployment

### Backend Deployment

For production deployment:
1. Set up a PostgreSQL database
2. Configure environment variables
3. Use a production WSGI server like Gunicorn
4. Set up file storage (AWS S3 recommended)

### Frontend Deployment

For app store deployment:
1. Build the app: `expo build:android` or `expo build:ios`
2. Submit to respective app stores

For web deployment:
1. Build for web: `expo build:web`
2. Deploy to your hosting service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

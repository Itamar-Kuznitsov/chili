# 🚀 Chili App Deployment Guide

## Quick Deploy with Railway (Recommended)

### Prerequisites
- GitHub account
- Railway account (free at railway.app)

### Step 1: Deploy Backend to Railway

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your Chili repository

3. **Configure Backend Service**
   - Railway will detect the Dockerfile in `/backend`
   - Add environment variables:
     - `SECRET_KEY`: Generate a strong secret key
     - `DATABASE_URL`: Railway will provide this automatically
   - Railway will automatically create a PostgreSQL database

4. **Deploy**
   - Railway will build and deploy automatically
   - Note the generated URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Frontend

#### Option A: Expo EAS Build (Mobile Apps)
```bash
cd frontend
npm install -g @expo/cli eas-cli
eas login
eas build:configure
eas build --platform all
```

#### Option B: Web Version (Vercel/Netlify)
```bash
cd frontend
# Build for web
npx expo export --platform web

# Deploy to Vercel
npx vercel --prod
```

### Step 3: Update Frontend API URL

1. **For Web Deployment:**
   ```bash
   # In frontend directory
   echo "EXPO_PUBLIC_API_URL=https://your-app.railway.app" > .env.local
   ```

2. **For Mobile Apps:**
   - Update the API URL in your app configuration
   - Rebuild and redeploy

## Alternative: Docker Compose (Local/Server)

### For VPS/Server Deployment

1. **Create docker-compose.yml:**
   ```yaml
   version: '3.8'
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: chili_db
         POSTGRES_USER: chili_user
         POSTGRES_PASSWORD: your_password
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
   
     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         DATABASE_URL: postgresql://chili_user:your_password@db:5432/chili_db
         SECRET_KEY: your-secret-key
       depends_on:
         - db
   
   volumes:
     postgres_data:
   ```

2. **Deploy:**
   ```bash
   docker-compose up -d
   ```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
```

### Frontend (.env.local)
```env
EXPO_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## Monitoring & Maintenance

- **Railway Dashboard**: Monitor logs, metrics, and deployments
- **Database Backups**: Railway provides automatic backups
- **SSL Certificates**: Automatically handled by Railway
- **Scaling**: Railway can auto-scale based on traffic

## Cost Estimation

- **Railway**: Free tier includes 500 hours/month
- **Vercel**: Free tier for frontend hosting
- **Total**: ~$0-20/month for small to medium apps

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Monitor logs for errors
- [ ] Use environment variables for secrets

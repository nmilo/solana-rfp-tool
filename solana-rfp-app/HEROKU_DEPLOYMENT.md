# Heroku Deployment Guide

## Prerequisites
1. Heroku CLI installed
2. Git repository set up
3. Heroku account

## Deployment Steps

### 1. Create Heroku App
```bash
heroku create your-app-name
```

### 2. Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:mini
```

### 3. Set Environment Variables
```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key
heroku config:set SECRET_KEY=your_secret_key_here
heroku config:set BACKEND_CORS_ORIGINS=https://your-app-name.herokuapp.com
```

### 4. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 5. Scale the App
```bash
heroku ps:scale web=1
```

### 6. Check Logs
```bash
heroku logs --tail
```

## Environment Variables Required
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Secret key for JWT tokens (auto-generated if not set)
- `DATABASE_URL`: Automatically set by Heroku Postgres addon
- `BACKEND_CORS_ORIGINS`: CORS origins (comma-separated)

## Troubleshooting

### H81 "Blank app" Error
- Ensure Procfile exists and is in the root directory
- Check that the Procfile has the correct web process command

### H14 "No web processes running" Error
- Run `heroku ps:scale web=1` to start a web dyno
- Check that your app starts successfully with `heroku logs --tail`

### Build Failures
- Check that all dependencies are in requirements.txt
- Ensure runtime.txt specifies a supported Python version
- Check build logs with `heroku logs --tail`

## API Endpoints
Once deployed, your API will be available at:
- Base URL: `https://your-app-name.herokuapp.com`
- Health Check: `https://your-app-name.herokuapp.com/health`
- API Docs: `https://your-app-name.herokuapp.com/docs`

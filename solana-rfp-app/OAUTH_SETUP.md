# OAuth2 Setup Guide

This guide will help you set up OAuth2 authentication for the Solana RFP Database application.

## Google OAuth2 Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API

### 2. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: "Solana RFP Database"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes:
   - `email`
   - `profile`
   - `openid`
5. Add test users (your email and any @solana.org emails)

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:3000` (for development)
   - `https://yourdomain.com` (for production)
5. Copy the Client ID and Client Secret

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

Create a `.env` file in the frontend directory:

```bash
# Google OAuth2
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

## Microsoft OAuth2 Setup (Optional)

### 1. Register Application in Azure

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Fill in:
   - Name: "Solana RFP Database"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:3000` (for development)

### 2. Configure API Permissions

1. Go to "API permissions"
2. Add permissions:
   - Microsoft Graph > User.Read
3. Grant admin consent

### 3. Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Copy the secret value

### 4. Update Environment Variables

Add to backend `.env`:

```bash
# Microsoft OAuth2
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

Add to frontend `.env`:

```bash
# Microsoft OAuth2
REACT_APP_MICROSOFT_CLIENT_ID=your-microsoft-client-id
```

## Frontend OAuth2 Libraries

Install the required OAuth2 libraries:

```bash
cd frontend
npm install @azure/msal-browser
```

Add Google OAuth2 script to `public/index.html`:

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

## Security Notes

1. **Never commit `.env` files** to version control
2. **Use HTTPS in production** for OAuth2 redirects
3. **Validate email domains** on the backend
4. **Use strong JWT secrets** in production
5. **Regularly rotate OAuth2 secrets**

## Testing

1. Start the backend: `cd backend && python -m uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm start`
3. Visit `http://localhost:3000`
4. Click "Continue with Google" or "Continue with Microsoft"
5. Complete the OAuth2 flow
6. Verify you're logged in with the correct email

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**: Check that the redirect URI in OAuth2 config matches your app URL
2. **"Email domain not allowed"**: Ensure the email is in the allowed domains list
3. **"OAuth2 token verification failed"**: Check that the OAuth2 credentials are correct

### Debug Mode

Enable debug logging by setting:

```bash
# Backend
DEBUG=true

# Frontend
REACT_APP_DEBUG=true
```

## Production Deployment

1. Update OAuth2 redirect URIs to production URLs
2. Use environment variables for all secrets
3. Enable HTTPS
4. Configure proper CORS settings
5. Set up monitoring and logging

import os
import requests
from typing import Optional, Dict, Any
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.core.config import settings

class OAuthService:
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.google_client_secret = settings.GOOGLE_CLIENT_SECRET
        
    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth2 token and return user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Extract user information
            user_info = {
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False),
                'provider': 'google'
            }
            
            return user_info
            
        except ValueError as e:
            print(f"Google token verification failed: {e}")
            return None
    
    def verify_microsoft_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Microsoft OAuth2 token and return user info"""
        try:
            # Microsoft Graph API endpoint
            graph_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(graph_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                    'name': user_data.get('displayName'),
                    'picture': None,  # Microsoft Graph doesn't provide profile picture in basic endpoint
                    'email_verified': True,  # Assume verified if we can access the data
                    'provider': 'microsoft'
                }
            else:
                print(f"Microsoft token verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Microsoft token verification error: {e}")
            return None
    
    def verify_email_domain(self, email: str) -> bool:
        """Verify if email domain is allowed"""
        if not email:
            return False
            
        # Your developer email
        if email.lower() == "mandicnikola1989@gmail.com":
            return True
            
        # Solana Foundation emails
        if email.lower().endswith("@solana.org"):
            return True
            
        return False
    
    def verify_organization_membership(self, email: str, provider: str) -> bool:
        """Verify if user is part of the authorized organization"""
        if not self.verify_email_domain(email):
            return False
            
        # For @solana.org emails, we can add additional verification
        if email.lower().endswith("@solana.org"):
            # Here you could add additional checks like:
            # - Verify against Google Workspace directory
            # - Check against internal employee database
            # - Verify through Microsoft 365 directory
            return True
            
        return True  # For your developer email
    
    def authenticate_user(self, token: str, provider: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with OAuth2 token"""
        user_info = None
        
        if provider == "google":
            user_info = self.verify_google_token(token)
        elif provider == "microsoft":
            user_info = self.verify_microsoft_token(token)
        else:
            return None
            
        if not user_info:
            return None
            
        # Verify email domain and organization membership
        if not self.verify_organization_membership(user_info['email'], provider):
            return None
            
        return user_info

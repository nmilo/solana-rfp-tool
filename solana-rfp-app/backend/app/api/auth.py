from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, OAuthLoginRequest, LoginResponse, UserResponse

router = APIRouter()
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current authenticated user"""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with email"""
    try:
        # Authenticate user
        user = auth_service.authenticate_user(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email domain not allowed"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@router.post("/google-login", response_model=LoginResponse)
async def google_login(
    request: dict,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with Google ID token (simplified)"""
    try:
        # Extract email from Google ID token
        email = request.get("email")
        name = request.get("name", "")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Validate email domain
        if not auth_service.is_allowed_email(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email domain not allowed. Only @solana.org emails and mandicnikola1989@gmail.com are permitted."
            )
        
        # Get or create user
        user = auth_service.get_user_by_email(email)
        if not user:
            # Create new user
            user = auth_service.create_user(email, name)
        
        # Update login statistics
        user.last_login = datetime.utcnow()
        user.login_count = str(int(user.login_count or "0") + 1)
        auth_service.db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google login failed: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"message": "Successfully logged out"}

@router.get("/verify-email/{email}")
async def verify_email_domain(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Check if email domain is allowed"""
    is_allowed = auth_service.is_allowed_email(email)
    return {
        "email": email,
        "is_allowed": is_allowed,
        "message": "Email domain allowed" if is_allowed else "Email domain not allowed"
    }

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from api.config import settings
from api.db.session import get_db, get_redis
from api.models.user import TokenData
from api.services.publisher_management import get_publisher_by_id

# Security scheme for Bearer token authentication
security = HTTPBearer()

async def get_token_header(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify the token from the authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "authentication_failed",
            "message": "Could not validate credentials",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        publisher_id: str = payload.get("sub")
        if publisher_id is None:
            raise credentials_exception
        
        token_data = TokenData(publisher_id=publisher_id)
        
    except JWTError:
        raise credentials_exception
    
    # Verify that the publisher exists
    publisher = await get_publisher_by_id(db, token_data.publisher_id)
    if publisher is None:
        raise credentials_exception
    
    return {
        "publisher_id": publisher_id,
        "is_admin": payload.get("is_admin", False),
        "permissions": payload.get("permissions", []),
    }

async def get_sdk_auth(
    request: Request,
    x_publisher_id: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
) -> Dict[str, Any]:
    """
    Verify SDK authentication using publisher ID and session token.
    """
    if not x_publisher_id or not x_session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "authentication_failed",
                "message": "Publisher ID and session token are required",
            }
        )
    
    # Verify that the session exists in Redis
    session_key = f"session:{x_publisher_id}:{x_session_token}"
    session_data = await redis.get(session_key)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "authentication_failed",
                "message": "Invalid or expired session",
            }
        )
    
    # Verify that the publisher exists
    publisher = await get_publisher_by_id(db, x_publisher_id)
    if publisher is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "authentication_failed",
                "message": "Invalid publisher ID",
            }
        )
    
    return {
        "publisher_id": x_publisher_id,
        "session_id": x_session_token,
    }

async def get_optional_sdk_auth(
    request: Request,
    x_publisher_id: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
) -> Optional[Dict[str, Any]]:
    """
    Optional SDK authentication - doesn't raise an exception if auth fails.
    """
    if not x_publisher_id or not x_session_token:
        return None
    
    try:
        return await get_sdk_auth(request, x_publisher_id, x_session_token, db, redis)
    except HTTPException:
        return None
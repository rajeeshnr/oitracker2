"""
Authentication endpoints handler.
Single Responsibility: Handle all authentication-related API operations.
Dependency Inversion: Depends on AuthenticationService abstraction.
"""
from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger
from ..auth.auth_service import AuthenticationService


class AuthEndpointsHandler:
    """Handles authentication API endpoints."""
    
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status."""
        try:
            status = self.auth_service.get_auth_status()
            return {"success": True, **status}
        except Exception as e:
            logger.error(f"Failed to get auth status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def login(self, request_token: str) -> Dict[str, Any]:
        """Authenticate and get access token."""
        try:
            access_token = await self.auth_service.interactive_auth()
            if access_token:
                return {
                    "success": True,
                    "access_token": access_token,
                    "message": "Authentication successful"
                }
            else:
                return {
                    "success": False,
                    "error": "AUTH_FAILED",
                    "message": "Authentication failed"
                }
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def logout(self) -> Dict[str, Any]:
        """Logout and invalidate token."""
        try:
            # TODO: Implement logout logic in auth_service
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

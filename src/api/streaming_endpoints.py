"""
Streaming endpoints handler.
Single Responsibility: Handle all streaming-related API operations.
Dependency Inversion: Depends on OptionChainService abstraction.
"""
from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger
from ..services.option_chain_service import OptionChainService
from ..auth.auth_service import AuthenticationService
from .models import StreamRequest


class StreamingEndpointsHandler:
    """Handles streaming API endpoints."""
    
    def __init__(self, option_chain_service: OptionChainService, auth_service: AuthenticationService):
        self.option_chain_service = option_chain_service
        self.auth_service = auth_service
    
    async def start_streaming(self, request: StreamRequest) -> Dict[str, Any]:
        """Start live data streaming."""
        try:
            if not self.auth_service.is_authenticated:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            success = await self.option_chain_service.start_live_streaming(
                request.index_name,
                request.expiry_date
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Streaming started successfully",
                    "index_name": request.index_name
                }
            else:
                return {
                    "success": False,
                    "error": "STREAM_ERROR",
                    "message": "Failed to start streaming"
                }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def stop_streaming(self) -> Dict[str, Any]:
        """Stop live data streaming."""
        try:
            await self.option_chain_service.stop_live_streaming()
            return {"success": True, "message": "Streaming stopped successfully"}
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_stream_status(self) -> Dict[str, Any]:
        """Get streaming status."""
        try:
            status = self.option_chain_service.websocket_service.get_connection_status()
            return {"success": True, **status}
        except Exception as e:
            logger.error(f"Failed to get stream status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

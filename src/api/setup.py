"""
API application setup.
Single Responsibility: Configure and wire up the FastAPI application.
Dependency Inversion: Provides dependency injection container.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.auth.auth_service import AuthenticationService
from src.services.option_chain_service import OptionChainService
from src.config import get_config

from .auth_endpoints import AuthEndpointsHandler
from .option_chain_endpoints import OptionChainEndpointsHandler
from .streaming_endpoints import StreamingEndpointsHandler
from .websocket_manager import WebSocketManager


class APISetup:
    """Manages API application setup and dependency injection."""
    
    def __init__(self):
        self.config = get_config()
        self.auth_service = AuthenticationService()
        self.option_chain_service = OptionChainService(self.auth_service)
        
        # Initialize endpoint handlers with dependency injection
        self.auth_handler = AuthEndpointsHandler(self.auth_service)
        self.option_chain_handler = OptionChainEndpointsHandler(self.option_chain_service)
        self.streaming_handler = StreamingEndpointsHandler(self.option_chain_service, self.auth_service)
        self.websocket_manager = WebSocketManager(self.auth_service)
        
        # Create FastAPI app
        self.app = self._create_app()
        self._setup_cors()
        self._setup_routes()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application instance."""
        return FastAPI(
            title="Option Chain Live Data Service API",
            description="REST API for Option Chain Live Data Service",
            version="1.0.0"
        )
    
    def _setup_cors(self):
        """Configure CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Register all API routes."""
        
        # Health check
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": "Option Chain Live Data Service API",
                "version": "1.0.0"
            }
        
        # Authentication routes
        @self.app.get("/api/auth/status")
        async def get_auth_status():
            return await self.auth_handler.get_auth_status()
        
        @self.app.post("/api/auth/login")
        async def login(request: dict):
            return await self.auth_handler.login(request.get("request_token", ""))
        
        @self.app.post("/api/auth/logout")
        async def logout():
            return await self.auth_handler.logout()
        
        # Option chain routes
        @self.app.get("/api/option-chain/{index_name}/expiries")
        async def get_expiries(index_name: str):
            return await self.option_chain_handler.get_expiries(index_name)
        
        @self.app.get("/api/option-chain/{index_name}/summary")
        async def get_summary(index_name: str, expiry: str = None):
            return await self.option_chain_handler.get_summary(index_name, expiry)
        
        # Streaming routes
        @self.app.post("/api/stream/start")
        async def start_streaming(request: dict):
            from .models import StreamRequest
            stream_request = StreamRequest(**request)
            return await self.streaming_handler.start_streaming(stream_request)
        
        @self.app.post("/api/stream/stop")
        async def stop_streaming():
            return await self.streaming_handler.stop_streaming()
        
        @self.app.get("/api/stream/status")
        async def get_stream_status():
            return await self.streaming_handler.get_stream_status()
        
        # WebSocket route
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await self.websocket_manager.handle_connection(websocket)
    
    def get_app(self) -> FastAPI:
        """Get the configured FastAPI application."""
        return self.app

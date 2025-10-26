"""
Option Chain Live Data Service - API Server

Main entry point for the Option Chain Live Data Service API.
Provides REST API and WebSocket streaming for option chain data.

Usage:
    python api_server.py

The server will start on http://localhost:8000
API documentation is available at http://localhost:8000/docs
"""
import sys
import uvicorn
from loguru import logger
from src.api.setup import APISetup


def create_app():
    """Create and configure the FastAPI application."""
    try:
        setup = APISetup()
        return setup.get_app()
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


app = create_app()


if __name__ == "__main__":
    import os
    
    try:
        logger.info("=" * 60)
        logger.info("Option Chain Live Data Service - API Server")
        logger.info("=" * 60)
        logger.info("Starting server on http://localhost:8000")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("WebSocket Endpoint: ws://localhost:8000/ws")
        logger.info("=" * 60)
        logger.info("Note: Authentication can be done via API endpoints")
        logger.info("Run: python scripts/auth_standalone.py to get access token")
        logger.info("=" * 60)
        
        # Use reload only if explicitly enabled via environment variable
        # Disable reload by default to avoid issues in debuggers/IDEs
        reload = os.getenv("AUTO_RELOAD", "false").lower() == "true"
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""
WebSocket service for real-time data streaming using KiteTicker.
Follows SOLID principles with dependency injection.
"""
import asyncio
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
from kiteconnect import KiteTicker
from loguru import logger
from ..config import get_config
from ..auth.auth_service import AuthenticationService


class WebSocketService:
    """
    Single Responsibility: Handles only WebSocket operations
    Open/Closed: Can be extended for additional WebSocket features
    Liskov Substitution: Can be replaced with other WebSocket implementations
    Interface Segregation: Clean interface focused on WebSocket operations
    Dependency Inversion: Depends on AuthenticationService abstraction
    """
    
    def __init__(self, auth_service: Optional[AuthenticationService] = None):
        self.config = get_config()
        self.auth_service = auth_service or AuthenticationService()
        self.kws = None
        self.is_connected = False
        self.is_subscribed = False
        self.subscribed_tokens = set()
        self.tick_callbacks = []
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = self.config.max_reconnect_attempts
        
    def set_auth_service(self, auth_service: AuthenticationService):
        """Set authentication service (dependency injection)."""
        self.auth_service = auth_service
        
    async def initialize(self) -> bool:
        """Initialize the WebSocket connection."""
        try:
            if not self.auth_service.is_authenticated:
                logger.error("Authentication required for WebSocket connection")
                return False
            
            access_token = self.auth_service.get_access_token()
            if not access_token:
                logger.error("Access token not available for WebSocket connection")
                return False
            
            self.kws = KiteTicker(
                api_key=self.config.api_key,
                access_token=access_token
            )
            
            # Set up event handlers
            self.kws.on_ticks = self._on_ticks
            self.kws.on_connect = self._on_connect
            self.kws.on_close = self._on_close
            self.kws.on_error = self._on_error
            self.kws.on_reconnect = self._on_reconnect
            self.kws.on_noreconnect = self._on_noreconnect
            
            logger.info("WebSocket service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket service: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to the WebSocket."""
        try:
            if not self.kws:
                await self.initialize()
            
            logger.info("Connecting to WebSocket...")
            self.kws.connect()
            
            # Wait for connection to be established
            await asyncio.sleep(2)
            
            if self.is_connected:
                logger.info("WebSocket connected successfully")
                return True
            else:
                logger.error("Failed to establish WebSocket connection")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            return False
    
    async def subscribe(self, instrument_tokens: List[int]) -> bool:
        """Subscribe to instrument tokens for real-time data."""
        try:
            if not self.is_connected:
                logger.error("WebSocket not connected. Cannot subscribe.")
                return False
            
            if not instrument_tokens:
                logger.warning("No instrument tokens provided for subscription")
                return False
            
            # Convert to set to avoid duplicates
            tokens_to_subscribe = set(instrument_tokens)
            
            logger.info(f"Subscribing to {len(tokens_to_subscribe)} instruments")
            
            # Subscribe to tokens
            self.kws.subscribe(list(tokens_to_subscribe))
            
            # Set mode (full, quote, or ltp)
            mode_map = {
                "full": self.kws.MODE_FULL,
                "quote": self.kws.MODE_QUOTE,
                "ltp": self.kws.MODE_LTP
            }
            
            mode = mode_map.get(self.config.ws_mode, self.kws.MODE_FULL)
            self.kws.set_mode(mode, list(tokens_to_subscribe))
            
            # Update subscribed tokens
            self.subscribed_tokens.update(tokens_to_subscribe)
            self.is_subscribed = True
            
            logger.info(f"Successfully subscribed to {len(tokens_to_subscribe)} instruments in {self.config.ws_mode} mode")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to instruments: {e}")
            return False
    
    async def unsubscribe(self, instrument_tokens: List[int]) -> bool:
        """Unsubscribe from instrument tokens."""
        try:
            if not self.is_connected:
                logger.error("WebSocket not connected. Cannot unsubscribe.")
                return False
            
            if not instrument_tokens:
                logger.warning("No instrument tokens provided for unsubscription")
                return False
            
            logger.info(f"Unsubscribing from {len(instrument_tokens)} instruments")
            
            # Unsubscribe from tokens
            self.kws.unsubscribe(instrument_tokens)
            
            # Update subscribed tokens
            self.subscribed_tokens -= set(instrument_tokens)
            
            if not self.subscribed_tokens:
                self.is_subscribed = False
            
            logger.info(f"Successfully unsubscribed from {len(instrument_tokens)} instruments")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from instruments: {e}")
            return False
    
    def add_tick_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback function to be called when tick data is received."""
        self.tick_callbacks.append(callback)
        logger.info(f"Added tick callback. Total callbacks: {len(self.tick_callbacks)}")
    
    def remove_tick_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove a tick callback function."""
        if callback in self.tick_callbacks:
            self.tick_callbacks.remove(callback)
            logger.info(f"Removed tick callback. Total callbacks: {len(self.tick_callbacks)}")
    
    def _on_ticks(self, ws, ticks):
        """Handle incoming tick data."""
        try:
            timestamp = datetime.now().isoformat()
            
            for tick in ticks:
                # Add timestamp to tick data
                tick['timestamp'] = timestamp
                
                # Call all registered callbacks
                for callback in self.tick_callbacks:
                    try:
                        callback(tick)
                    except Exception as e:
                        logger.error(f"Error in tick callback: {e}")
            
            logger.debug(f"Processed {len(ticks)} ticks")
            
        except Exception as e:
            logger.error(f"Error processing ticks: {e}")
    
    def _on_connect(self, ws, response):
        """Handle WebSocket connection."""
        self.is_connected = True
        self.reconnect_attempts = 0
        logger.info("WebSocket connected successfully")
    
    def _on_close(self, ws, code, reason):
        """Handle WebSocket close."""
        self.is_connected = False
        self.is_subscribed = False
        
        # Provide specific error messages for common issues
        if code == 1006 and "403" in str(reason):
            logger.error(f"WebSocket closed. Code: {code}, Reason: {reason}")
            logger.error("🔐 Authentication Error: 403 Forbidden")
            logger.error("   This usually means your access token has expired or is invalid.")
            logger.error("   Please run 'python troubleshoot_auth.py' to fix this issue.")
        elif code == 1006 and "401" in str(reason):
            logger.error(f"WebSocket closed. Code: {code}, Reason: {reason}")
            logger.error("🔐 Authentication Error: 401 Unauthorized")
            logger.error("   This usually means your API credentials are invalid.")
            logger.error("   Please check your API key and secret in the .env file.")
        else:
            logger.warning(f"WebSocket closed. Code: {code}, Reason: {reason}")
    
    def _on_error(self, ws, code, reason):
        """Handle WebSocket error."""
        logger.error(f"WebSocket error. Code: {code}, Reason: {reason}")
        
        # Provide specific troubleshooting advice
        if code == 403 or "403" in str(reason):
            logger.error("🔐 Authentication Error: 403 Forbidden")
            logger.error("   Troubleshooting steps:")
            logger.error("   1. Check if your access token has expired")
            logger.error("   2. Generate a new access token using the login flow")
            logger.error("   3. Run 'python troubleshoot_auth.py' for help")
        elif code == 401 or "401" in str(reason):
            logger.error("🔐 Authentication Error: 401 Unauthorized")
            logger.error("   Troubleshooting steps:")
            logger.error("   1. Verify your API key and secret are correct")
            logger.error("   2. Check your .env file configuration")
            logger.error("   3. Run 'python troubleshoot_auth.py' for help")
    
    def _on_reconnect(self, ws, attempts_count):
        """Handle WebSocket reconnection."""
        self.reconnect_attempts = attempts_count
        logger.info(f"WebSocket reconnecting... Attempt {attempts_count}")
    
    def _on_noreconnect(self, ws):
        """Handle WebSocket reconnection failure."""
        logger.error("WebSocket reconnection failed. Maximum attempts reached.")
        self.is_connected = False
        self.is_subscribed = False
    
    async def disconnect(self):
        """Disconnect from the WebSocket."""
        try:
            if self.kws and self.is_connected:
                logger.info("Disconnecting WebSocket...")
                self.kws.close()
                self.is_connected = False
                self.is_subscribed = False
                self.subscribed_tokens.clear()
                logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            "is_connected": self.is_connected,
            "is_subscribed": self.is_subscribed,
            "subscribed_tokens_count": len(self.subscribed_tokens),
            "reconnect_attempts": self.reconnect_attempts,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "mode": self.config.ws_mode
        }
    
    async def keep_alive(self):
        """Keep the WebSocket connection alive."""
        while self.is_connected:
            try:
                await asyncio.sleep(30)  # Send keep-alive every 30 seconds
                if not self.is_connected:
                    break
            except Exception as e:
                logger.error(f"Error in keep-alive: {e}")
                break

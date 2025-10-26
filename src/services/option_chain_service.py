"""
Option Chain service for managing and filtering option contracts.
Follows SOLID principles with dependency injection.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd
from loguru import logger
from .kite_service import KiteService
from .websocket_service import WebSocketService
from ..auth.auth_service import AuthenticationService
from ..config import get_config, OptionChainConfig


class OptionChainService:
    """
    Single Responsibility: Manages option chain data and streaming
    Open/Closed: Can be extended for additional option chain features
    Liskov Substitution: Can be replaced with other option chain implementations
    Interface Segregation: Clean interface focused on option chain operations
    Dependency Inversion: Depends on service abstractions, not concrete implementations
    """
    
    def __init__(self, auth_service: Optional[AuthenticationService] = None):
        self.config = get_config()
        self.auth_service = auth_service or AuthenticationService()
        self.kite_service = KiteService(self.auth_service)
        self.websocket_service = WebSocketService(self.auth_service)
        self.current_data = {}
        self.instruments_map = {}
        self.last_update = None
        
    def set_auth_service(self, auth_service: AuthenticationService):
        """Set authentication service (dependency injection)."""
        self.auth_service = auth_service
        self.kite_service.set_auth_service(auth_service)
        self.websocket_service.set_auth_service(auth_service)
        
    def get_auth_service(self) -> AuthenticationService:
        """Get the authentication service."""
        return self.auth_service
    
    def is_authenticated(self) -> bool:
        """Check if the service is authenticated."""
        return self.auth_service.is_authenticated
    
    async def load_option_chain(self, index_name: str, expiry_date: Optional[str] = None) -> Dict[str, Any]:
        """Load option chain for a specific index."""
        try:
            if index_name not in OptionChainConfig.SUPPORTED_INDICES:
                raise ValueError(f"Unsupported index: {index_name}")
            
            logger.info(f"Loading option chain for {index_name}")
            
            # Get option instruments
            if expiry_date:
                instruments = await self.kite_service.get_option_chain_by_expiry(index_name, expiry_date)
            else:
                instruments = await self.kite_service.get_option_chain_instruments(index_name)
            
            if not instruments:
                return {"error": f"No option instruments found for {index_name}"}
            
            # Create instruments map for quick lookup
            self.instruments_map = {
                inst['instrument_token']: inst for inst in instruments
            }
            
            # Initialize data structure
            self.current_data = {
                "index_name": index_name,
                "expiry_date": expiry_date,
                "instruments": instruments,
                "live_data": {},
                "last_update": None,
                "total_instruments": len(instruments)
            }
            
            logger.info(f"Loaded {len(instruments)} option instruments for {index_name}")
            return self.current_data
            
        except Exception as e:
            logger.error(f"Failed to load option chain for {index_name}: {e}")
            raise
    
    async def start_live_streaming(self, index_name: str, expiry_date: Optional[str] = None) -> bool:
        """Start live streaming for option chain."""
        try:
            if not self.is_authenticated():
                logger.error("Authentication required for live streaming. Please authenticate first.")
                return False
            
            # Load option chain first
            await self.load_option_chain(index_name, expiry_date)
            
            if not self.current_data:
                logger.error("No option chain data loaded")
                return False
            
            # Get instrument tokens
            instrument_tokens = self.kite_service.get_instrument_tokens(
                self.current_data["instruments"]
            )
            
            if not instrument_tokens:
                logger.error("No instrument tokens found")
                return False
            
            # Initialize WebSocket service
            ws_initialized = await self.websocket_service.initialize()
            if not ws_initialized:
                logger.error("Failed to initialize WebSocket service")
                return False
            
            # Connect to WebSocket
            connected = await self.websocket_service.connect()
            if not connected:
                logger.error("Failed to connect to WebSocket")
                return False
            
            # Add tick callback
            self.websocket_service.add_tick_callback(self._handle_tick_data)
            
            # Subscribe to instruments
            subscribed = await self.websocket_service.subscribe(instrument_tokens)
            if not subscribed:
                logger.error("Failed to subscribe to instruments")
                return False
            
            logger.info(f"Started live streaming for {len(instrument_tokens)} instruments")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start live streaming: {e}")
            return False
    
    def _handle_tick_data(self, tick_data: Dict[str, Any]):
        """Handle incoming tick data."""
        try:
            instrument_token = tick_data.get('instrument_token')
            
            if instrument_token not in self.instruments_map:
                return
            
            # Extract relevant data
            live_data = {
                "instrument_token": instrument_token,
                "last_price": tick_data.get('last_price', 0),
                "open_interest": tick_data.get('oi', 0),
                "volume": tick_data.get('volume', 0),
                "bid_price": tick_data.get('depth', {}).get('buy', [{}])[0].get('price', 0),
                "ask_price": tick_data.get('depth', {}).get('sell', [{}])[0].get('price', 0),
                "bid_quantity": tick_data.get('depth', {}).get('buy', [{}])[0].get('quantity', 0),
                "ask_quantity": tick_data.get('depth', {}).get('sell', [{}])[0].get('quantity', 0),
                "timestamp": tick_data.get('timestamp', datetime.now().isoformat())
            }
            
            # Update current data
            self.current_data["live_data"][instrument_token] = live_data
            self.current_data["last_update"] = datetime.now().isoformat()
            self.last_update = datetime.now()
            
            logger.debug(f"Updated data for instrument {instrument_token}")
            
        except Exception as e:
            logger.error(f"Error handling tick data: {e}")
    
    def get_option_chain_data(self) -> Dict[str, Any]:
        """Get current option chain data."""
        return self.current_data.copy()
    
    def get_option_chain_summary(self) -> Dict[str, Any]:
        """Get a summary of the current option chain."""
        try:
            if not self.current_data:
                return {"error": "No option chain data available"}
            
            instruments = self.current_data["instruments"]
            live_data = self.current_data["live_data"]
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(instruments)
            
            # Add live data
            live_df = pd.DataFrame([
                {
                    "instrument_token": token,
                    "last_price": data["last_price"],
                    "open_interest": data["open_interest"],
                    "volume": data["volume"]
                }
                for token, data in live_data.items()
            ])
            
            if not live_df.empty:
                df = df.merge(live_df, on="instrument_token", how="left")
            
            # Group by strike and instrument type
            summary = {}
            
            for strike in sorted(df['strike_price'].unique()):
                strike_data = df[df['strike_price'] == strike]
                
                ce_data = strike_data[strike_data['instrument_type'] == 'CE']
                pe_data = strike_data[strike_data['instrument_type'] == 'PE']
                
                summary[strike] = {
                    "CE": {
                        "instrument_token": ce_data['instrument_token'].iloc[0] if not ce_data.empty else None,
                        "last_price": ce_data['last_price'].iloc[0] if not ce_data.empty else 0,
                        "open_interest": ce_data['open_interest'].iloc[0] if not ce_data.empty else 0,
                        "volume": ce_data['volume'].iloc[0] if not ce_data.empty else 0
                    },
                    "PE": {
                        "instrument_token": pe_data['instrument_token'].iloc[0] if not pe_data.empty else None,
                        "last_price": pe_data['last_price'].iloc[0] if not pe_data.empty else 0,
                        "open_interest": pe_data['open_interest'].iloc[0] if not pe_data.empty else 0,
                        "volume": pe_data['volume'].iloc[0] if not pe_data.empty else 0
                    }
                }
            
            return {
                "index_name": self.current_data["index_name"],
                "expiry_date": self.current_data["expiry_date"],
                "total_instruments": self.current_data["total_instruments"],
                "live_data_count": len(live_data),
                "last_update": self.current_data["last_update"],
                "strike_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error generating option chain summary: {e}")
            return {"error": str(e)}
    
    def get_strike_data(self, strike_price: float) -> Dict[str, Any]:
        """Get data for a specific strike price."""
        try:
            if not self.current_data:
                return {"error": "No option chain data available"}
            
            instruments = self.current_data["instruments"]
            live_data = self.current_data["live_data"]
            
            # Find instruments for this strike
            strike_instruments = [
                inst for inst in instruments 
                if inst['strike_price'] == strike_price
            ]
            
            if not strike_instruments:
                return {"error": f"No instruments found for strike {strike_price}"}
            
            result = {"strike_price": strike_price}
            
            for inst in strike_instruments:
                token = inst['instrument_token']
                inst_type = inst['instrument_type']
                
                result[inst_type] = {
                    "instrument_token": token,
                    "trading_symbol": inst['trading_symbol'],
                    "expiry": inst['expiry'].strftime('%Y-%m-%d'),
                    "last_price": live_data.get(token, {}).get('last_price', 0),
                    "open_interest": live_data.get(token, {}).get('open_interest', 0),
                    "volume": live_data.get(token, {}).get('volume', 0),
                    "bid_price": live_data.get(token, {}).get('bid_price', 0),
                    "ask_price": live_data.get(token, {}).get('ask_price', 0)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting strike data: {e}")
            return {"error": str(e)}
    
    async def stop_live_streaming(self):
        """Stop live streaming."""
        try:
            await self.websocket_service.disconnect()
            logger.info("Stopped live streaming")
        except Exception as e:
            logger.error(f"Error stopping live streaming: {e}")
    
    async def close(self):
        """Close the service and cleanup resources."""
        try:
            await self.stop_live_streaming()
            logger.info("Option Chain Service closed")
        except Exception as e:
            logger.error(f"Error closing service: {e}")

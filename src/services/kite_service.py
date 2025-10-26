"""
Kite Connect API service for instrument data fetching.
Follows SOLID principles with dependency injection.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import pandas as pd
from kiteconnect import KiteConnect
from loguru import logger
from ..config import get_config, OptionChainConfig
from ..auth.auth_service import AuthenticationService


class KiteService:
    """
    Single Responsibility: Handles only instrument data operations
    Open/Closed: Can be extended for additional data operations
    Liskov Substitution: Can be replaced with other data service implementations
    Interface Segregation: Clean interface focused on data operations
    Dependency Inversion: Depends on AuthenticationService abstraction
    """
    
    def __init__(self, auth_service: Optional[AuthenticationService] = None):
        self.config = get_config()
        self.auth_service = auth_service or AuthenticationService()
        
    def set_auth_service(self, auth_service: AuthenticationService):
        """Set authentication service (dependency injection)."""
        self.auth_service = auth_service
    
    def get_kite_instance(self) -> Optional[KiteConnect]:
        """Get authenticated Kite Connect instance."""
        if not self.auth_service.is_authenticated:
            logger.warning("Not authenticated. Please authenticate first.")
            return None
        return self.auth_service.get_kite_instance()
    
    def get_basic_kite_instance(self) -> KiteConnect:
        """Get basic Kite Connect instance for public data (no auth required)."""
        return KiteConnect(api_key=self.config.api_key)
    
    async def get_instruments(self, exchange: str = "NFO") -> List[Dict[str, Any]]:
        """Fetch instruments from the specified exchange."""
        try:
            # Use basic instance for public instrument data
            kite = self.get_basic_kite_instance()
            
            logger.info(f"Fetching instruments from {exchange}")
            instruments = kite.instruments(exchange)
            
            logger.info(f"Fetched {len(instruments)} instruments from {exchange}")
            return instruments
                
        except Exception as e:
            logger.error(f"Failed to fetch instruments from {exchange}: {e}")
            raise
    
    async def get_option_chain_instruments(self, index_name: str) -> List[Dict[str, Any]]:
        """Get option chain instruments for a specific index."""
        try:
            if index_name not in OptionChainConfig.SUPPORTED_INDICES:
                raise ValueError(f"Unsupported index: {index_name}")
            
            instruments = await self.get_instruments("NFO")
            
            # Filter for the specific index options
            option_instruments = [
                inst for inst in instruments
                if (inst['name'] == index_name and 
                    inst['segment'] == OptionChainConfig.SEGMENT_MAPPING[index_name] and
                    inst['instrument_type'] in OptionChainConfig.INSTRUMENT_TYPES.values())
            ]
            
            logger.info(f"Found {len(option_instruments)} option instruments for {index_name}")
            return option_instruments
            
        except Exception as e:
            logger.error(f"Failed to get option chain instruments for {index_name}: {e}")
            raise
    
    def _parse_expiry_date(self, expiry_date_str: str) -> date:
        """Parse expiry date from various formats."""
        try:
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',      # 2025-10-28
                '%d-%m-%Y',      # 28-10-2025
                '%d-%b-%Y',      # 28-Oct-2025
                '%d-%B-%Y',      # 28-October-2025
                '%d/%m/%Y',      # 28/10/2025
                '%d/%b/%Y',      # 28/Oct/2025
                '%d/%B/%Y',      # 28/October/2025
                '%m/%d/%Y',      # 10/28/2025
                '%b %d, %Y',     # Oct 28, 2025
                '%B %d, %Y',     # October 28, 2025
                '%d %b %Y',      # 28 Oct 2025
                '%d %B %Y',      # 28 October 2025
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(expiry_date_str.strip(), fmt).date()
                    logger.debug(f"Successfully parsed date '{expiry_date_str}' as {parsed_date}")
                    return parsed_date
                except ValueError:
                    continue
            
            # If no format matches, raise error
            raise ValueError(f"Unable to parse date: {expiry_date_str}")
            
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            raise
    
    async def get_option_chain_by_expiry(self, index_name: str, expiry_date: str) -> List[Dict[str, Any]]:
        """Get option chain instruments for a specific index and expiry."""
        try:
            all_options = await self.get_option_chain_instruments(index_name)
            
            # Parse the expiry date
            target_expiry = self._parse_expiry_date(expiry_date)
            
            # Filter by expiry date
            expiry_options = [
                inst for inst in all_options
                if inst['expiry'] == target_expiry
            ]
            
            logger.info(f"Found {len(expiry_options)} options for {index_name} expiring on {target_expiry}")
            return expiry_options
            
        except Exception as e:
            logger.error(f"Failed to get option chain by expiry: {e}")
            raise
    
    async def get_option_chain_summary(self, index_name: str) -> Dict[str, Any]:
        """Get a summary of the option chain for an index."""
        try:
            instruments = await self.get_option_chain_instruments(index_name)
            
            if not instruments:
                return {"error": f"No option instruments found for {index_name}"}
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(instruments)
            
            # Group by expiry
            expiry_summary = df.groupby('expiry').agg({
                'instrument_token': 'count',
                'strike_price': ['min', 'max'],
                'instrument_type': lambda x: list(set(x))
            }).round(2)
            
            # Get unique expiries
            expiries = sorted(df['expiry'].unique())
            
            # Get strike price range
            min_strike = df['strike_price'].min()
            max_strike = df['strike_price'].max()
            
            summary = {
                "index_name": index_name,
                "total_instruments": len(instruments),
                "expiries": [exp.strftime('%Y-%m-%d') for exp in expiries],
                "expiries_formatted": [exp.strftime('%d-%b-%Y') for exp in expiries],
                "strike_range": {
                    "min": min_strike,
                    "max": max_strike
                },
                "expiry_summary": expiry_summary.to_dict(),
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"Generated option chain summary for {index_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get option chain summary: {e}")
            raise
    
    async def get_available_expiries(self, index_name: str) -> List[str]:
        """Get list of available expiry dates for an index."""
        try:
            instruments = await self.get_option_chain_instruments(index_name)
            
            if not instruments:
                return []
            
            # Get unique expiries
            expiries = sorted(set(inst['expiry'] for inst in instruments))
            
            # Return in multiple formats
            expiry_formats = []
            for expiry in expiries:
                expiry_formats.append({
                    "date": expiry.strftime('%Y-%m-%d'),
                    "formatted": expiry.strftime('%d-%b-%Y'),
                    "readable": expiry.strftime('%d %B %Y')
                })
            
            logger.info(f"Found {len(expiries)} expiry dates for {index_name}")
            return expiry_formats
            
        except Exception as e:
            logger.error(f"Failed to get available expiries: {e}")
            raise
    
    async def get_quote(self, instrument_tokens: List[int]) -> Dict[str, Any]:
        """Get quotes for specific instrument tokens."""
        try:
            kite = self.get_kite_instance()
            if not kite:
                raise ValueError("Not authenticated. Please authenticate first.")
            
            quotes = kite.quote(instrument_tokens)
            logger.debug(f"Fetched quotes for {len(instrument_tokens)} instruments")
            return quotes
        except Exception as e:
            logger.error(f"Failed to get quotes: {e}")
            raise
    
    async def get_ltp(self, instrument_tokens: List[int]) -> Dict[str, Any]:
        """Get Last Traded Price for specific instrument tokens."""
        try:
            kite = self.get_kite_instance()
            if not kite:
                raise ValueError("Not authenticated. Please authenticate first.")
            
            ltp_data = kite.ltp(instrument_tokens)
            logger.debug(f"Fetched LTP for {len(instrument_tokens)} instruments")
            return ltp_data
        except Exception as e:
            logger.error(f"Failed to get LTP: {e}")
            raise
    
    def get_instrument_tokens(self, instruments: List[Dict[str, Any]]) -> List[int]:
        """Extract instrument tokens from instruments list."""
        return [inst['instrument_token'] for inst in instruments]

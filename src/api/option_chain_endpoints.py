"""
Option chain endpoints handler.
Single Responsibility: Handle all option chain-related API operations.
Dependency Inversion: Depends on OptionChainService abstraction.
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger
from ..services.option_chain_service import OptionChainService


class OptionChainEndpointsHandler:
    """Handles option chain API endpoints."""
    
    def __init__(self, option_chain_service: OptionChainService):
        self.option_chain_service = option_chain_service
    
    async def get_expiries(self, index_name: str) -> Dict[str, Any]:
        """Get available expiry dates for an index."""
        try:
            expiries = await self.option_chain_service.kite_service.get_available_expiries(index_name)
            return {
                "success": True,
                "index_name": index_name,
                "expiries": expiries,
                "count": len(expiries)
            }
        except Exception as e:
            logger.error(f"Failed to get expiries for {index_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_summary(self, index_name: str, expiry: Optional[str] = None) -> Dict[str, Any]:
        """Get option chain summary."""
        try:
            if expiry:
                # Load chain with specific expiry
                await self.option_chain_service.load_option_chain(index_name, expiry)
            else:
                # Load all expiries
                await self.option_chain_service.load_option_chain(index_name)
            
            summary = self.option_chain_service.get_option_chain_summary()
            return {"success": True, **summary}
        except Exception as e:
            logger.error(f"Failed to get summary for {index_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_strike_data(self, index_name: str, strike_price: float) -> Dict[str, Any]:
        """Get data for specific strike price."""
        try:
            strike_data = self.option_chain_service.get_strike_data(strike_price)
            return {"success": True, "strike_price": strike_price, **strike_data}
        except Exception as e:
            logger.error(f"Failed to get strike data for {strike_price}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

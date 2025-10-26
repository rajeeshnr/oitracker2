"""
Data storage service for persisting option chain data.
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiofiles
from loguru import logger
from ..config import get_config


class DataStorageService:
    """Service for persisting option chain data."""
    
    def __init__(self):
        self.config = get_config()
        
    async def store_historical_data(self, index_name: str, data: List[Dict[str, Any]]) -> bool:
        """Store historical data for analysis."""
        try:
            timestamp = datetime.now()
            filename = f"data/historical_{index_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            # Ensure data directory exists
            import os
            os.makedirs("data", exist_ok=True)
            
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
            
            logger.info(f"Stored historical data for {index_name} in {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store historical data: {e}")
            return False
    
    async def load_historical_data(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """Load historical data from file."""
        try:
            async with aiofiles.open(filename, 'r') as f:
                content = await f.read()
                data = json.loads(content)
            
            logger.info(f"Loaded historical data from {filename}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return None
    
    async def export_data(self, index_name: str, data: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """Export current data to JSON file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"data/export_{index_name}_{timestamp}.json"
            
            # Ensure data directory exists
            import os
            os.makedirs("data", exist_ok=True)
            
            export_data = {
                "index_name": index_name,
                "export_timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(export_data, indent=2, default=str))
            
            logger.info(f"Exported data for {index_name} to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False

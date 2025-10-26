"""
Configuration management for Kite Connect API service.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class KiteConfig(BaseSettings):
    """Configuration settings for Kite Connect API."""
    
    # API Credentials
    api_key: str = Field(..., env="API_KEY")
    api_secret: str = Field(..., env="API_SECRET")
    
    # WebSocket Configuration
    ws_mode: str = Field("full", env="WS_MODE")  # full, quote, ltp
    reconnect_interval: int = Field(5, env="RECONNECT_INTERVAL")
    max_reconnect_attempts: int = Field(10, env="MAX_RECONNECT_ATTEMPTS")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/kite_service.log", env="LOG_FILE")
    
    # Option Chain Configuration
    default_index: str = Field("NIFTY", env="DEFAULT_INDEX")
    expiry_filter_days: int = Field(30, env="EXPIRY_FILTER_DAYS")
    max_strike_range: int = Field(20, env="MAX_STRIKE_RANGE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class OptionChainConfig:
    """Configuration for option chain filtering."""
    
    # Supported indices
    SUPPORTED_INDICES = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
    
    # Segment mapping
    SEGMENT_MAPPING = {
        "NIFTY": "NFO-OPT",
        "BANKNIFTY": "NFO-OPT", 
        "FINNIFTY": "NFO-OPT",
        "MIDCPNIFTY": "NFO-OPT"
    }
    
    # Instrument type mapping
    INSTRUMENT_TYPES = {
        "CE": "CE",  # Call European
        "PE": "PE"   # Put European
    }


# Global configuration instance
config = KiteConfig()


def get_config() -> KiteConfig:
    """Get the global configuration instance."""
    return config


def validate_config() -> bool:
    """Validate the configuration settings."""
    if not config.api_key or config.api_key == "your_api_key_here":
        raise ValueError("API_KEY is not set or is using default value")
    
    if not config.api_secret or config.api_secret == "your_api_secret_here":
        raise ValueError("API_SECRET is not set or is using default value")
    
    if config.ws_mode not in ["full", "quote", "ltp"]:
        raise ValueError("WS_MODE must be one of: full, quote, ltp")
    
    if config.default_index not in OptionChainConfig.SUPPORTED_INDICES:
        raise ValueError(f"Default index must be one of: {OptionChainConfig.SUPPORTED_INDICES}")
    
    return True

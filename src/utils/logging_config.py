"""
Improved logging configuration for Windows compatibility.
"""
import os
import sys
from datetime import datetime
from loguru import logger


def setup_logging(log_level: str = "INFO", log_file: str = "logs/kite_service.log"):
    """Setup logging with Windows compatibility."""
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler with Windows-specific improvements
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Use timestamp-based filename to avoid rotation issues
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(log_file)[0]
        ext = os.path.splitext(log_file)[1]
        timestamped_log_file = f"{base_name}_{timestamp}{ext}"
        
        logger.add(
            timestamped_log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,  # Use queue to avoid file locking issues
            backtrace=True,
            diagnose=True,
            catch=True  # Catch exceptions in logging
        )
        
        logger.info(f"File logging configured: {timestamped_log_file}")
        
    except Exception as e:
        # If file logging fails, continue with console only
        logger.warning(f"Failed to setup file logging: {e}")
        logger.info("Continuing with console logging only")


def setup_simple_logging(log_level: str = "INFO"):
    """Setup simple logging without file rotation to avoid Windows issues."""
    logger.remove()  # Remove default handler
    
    # Add console handler only
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.info("Simple console logging configured")


def cleanup_logging():
    """Cleanup logging handlers."""
    try:
        logger.remove()
        logger.info("Logging cleanup completed")
    except Exception as e:
        print(f"Warning: Logging cleanup failed: {e}")

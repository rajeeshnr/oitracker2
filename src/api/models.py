"""
API Models for request/response validation.
Single Responsibility: Define data structures only.
"""
from pydantic import BaseModel
from typing import Optional, List


class LoginRequest(BaseModel):
    """Login request model."""
    request_token: str


class StreamRequest(BaseModel):
    """Stream request model."""
    index_name: str
    expiry_date: Optional[str] = None


class QuotesRequest(BaseModel):
    """Quotes request model."""
    instrument_tokens: List[int]


class LTPRequest(BaseModel):
    """Last Traded Price request model."""
    instrument_tokens: List[int]

# Usage Guide - Option Chain Live Data Service API

Complete guide for using the Option Chain Live Data Service REST API and WebSocket streaming.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Authentication](#authentication)
5. [REST API](#rest-api)
6. [WebSocket Streaming](#websocket-streaming)
7. [Example Usage](#example-usage)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Start the API Server

```bash
python api_server.py
```

The server will start on:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

---

## Installation

### 1. Prerequisites

- Python 3.8 or higher
- Kite Connect API credentials

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy configuration template
cp config.env.example .env

# Edit .env file with your credentials
```

Edit `.env` file:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
DEFAULT_INDEX=NIFTY
LOG_LEVEL=INFO
```

---

## Configuration

### Environment Variables

```env
# Kite Connect API Credentials
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Default Settings
DEFAULT_INDEX=NIFTY
LOG_LEVEL=INFO
LOG_FILE=logs/kite_service.log
WS_MODE=full

# Streaming Settings
MAX_RECONNECT_ATTEMPTS=5
MAX_STRIKE_RANGE=50
```

### Supported Indices

- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY

---

## Authentication

### Interactive Authentication

```bash
# Run standalone authentication
python scripts/auth_standalone.py

# Follow the prompts:
# 1. Choose "Interactive Authentication"
# 2. Browser opens for login
# 3. Paste the request_token from redirect URL
```

### Load Saved Token

```bash
# Run standalone authentication
python scripts/auth_standalone.py

# Choose "Load Saved Token"
# Token is automatically loaded from .access_token file
```

### Authentication Flow

1. User clicks login URL
2. User logs in at Kite Connect
3. User gets redirected with request_token
4. Request token exchanged for access_token
5. Access token saved to `.access_token` file

---

## REST API

### Base URL

```
http://localhost:8000/api
```

### 1. Authentication Endpoints

#### GET `/api/auth/status`

Get authentication status.

**Response:**

```json
{
  "success": true,
  "is_authenticated": true,
  "has_access_token": true,
  "connection_valid": true
}
```

**Example:**

```bash
curl http://localhost:8000/api/auth/status
```

#### POST `/api/auth/login`

Authenticate and get access token.

**Request:**

```json
{
  "request_token": "request_token_from_redirect_url"
}
```

**Response:**

```json
{
  "success": true,
  "access_token": "access_token_value",
  "message": "Authentication successful"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"request_token": "your_request_token"}'
```

### 2. Option Chain Data Endpoints

#### GET `/api/option-chain/{index}/expiries`

Get available expiry dates for an index.

**Path Parameters:**

- `index` - Index name (NIFTY, BANKNIFTY, etc.)

**Response:**

```json
{
  "success": true,
  "index_name": "NIFTY",
  "expiries": [
    {
      "date": "2025-10-28",
      "formatted": "28-Oct-2025",
      "readable": "28 October 2025"
    }
  ],
  "count": 18
}
```

**Example:**

```bash
curl http://localhost:8000/api/option-chain/NIFTY/expiries
```

#### GET `/api/option-chain/{index}/summary`

Get option chain summary.

**Path Parameters:**

- `index` - Index name

**Query Parameters:**

- `expiry` - Expiry date (optional)

**Response:**

```json
{
  "success": true,
  "index_name": "NIFTY",
  "total_instruments": 1616,
  "live_data_count": 1616,
  "expiry_date": "2025-10-28",
  "strike_summary": {
    "22700": {
      "CE": {
        "last_price": 120.5,
        "open_interest": 12345,
        "volume": 1234
      },
      "PE": {
        "last_price": 115.75,
        "open_interest": 23456,
        "volume": 2345
      }
    }
  }
}
```

**Example:**

```bash
# Get all expiries
curl http://localhost:8000/api/option-chain/NIFTY/summary

# Get specific expiry
curl http://localhost:8000/api/option-chain/NIFTY/summary?expiry=2025-10-28
```

### 3. Streaming Control Endpoints

#### POST `/api/stream/start`

Start live data streaming.

**Request:**

```json
{
  "index_name": "NIFTY",
  "expiry_date": "2025-10-28"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Streaming started successfully",
  "index_name": "NIFTY"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/stream/start \
  -H "Content-Type: application/json" \
  -d '{"index_name": "NIFTY", "expiry_date": "2025-10-28"}'
```

#### POST `/api/stream/stop`

Stop live data streaming.

**Response:**

```json
{
  "success": true,
  "message": "Streaming stopped successfully"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/stream/stop
```

#### GET `/api/stream/status`

Get streaming status.

**Response:**

```json
{
  "success": true,
  "is_connected": true,
  "is_subscribed": true,
  "subscribed_tokens_count": 1616,
  "mode": "full"
}
```

**Example:**

```bash
curl http://localhost:8000/api/stream/status
```

### 4. Health Check

#### GET `/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "Option Chain Live Data Service API",
  "version": "1.0.0"
}
```

**Example:**

```bash
curl http://localhost:8000/health
```

---

## WebSocket Streaming

### Connection

**Endpoint:** `ws://localhost:8000/ws`

**Connection Requirements:**

- Access token must be valid
- User must be authenticated

### Message Format

**Tick Data:**

```json
{
  "type": "tick",
  "data": {
    "instrument_token": 408065,
    "last_price": 120.5,
    "open_interest": 12345,
    "volume": 1234,
    "timestamp": 1698288000
  }
}
```

**Message Types:**

1. `tick` - Individual tick data
2. `summary` - Periodic summary update
3. `error` - Error message
4. `status` - Connection status update

### Example Usage

#### JavaScript

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => {
  console.log("Connected to WebSocket");

  // Subscribe to instruments
  ws.send(
    JSON.stringify({
      action: "subscribe",
      instrument_tokens: [408065, 408577, 409089],
    })
  );
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);

  if (message.type === "tick") {
    updateUI(message.data);
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected from WebSocket");
};
```

#### Python

```python
import asyncio
import websockets
import json

async def stream_data():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe
        await websocket.send(json.dumps({
            "action": "subscribe",
            "instrument_tokens": [408065, 408577]
        }))

        # Listen for ticks
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("type") == "tick":
                print("Tick:", data["data"])

# Run
asyncio.run(stream_data())
```

---

## Example Usage

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Check authentication status
response = requests.get(f"{BASE_URL}/auth/status")
print("Auth Status:", response.json())

# 2. Get available expiries
response = requests.get(f"{BASE_URL}/option-chain/NIFTY/expiries")
expiries = response.json()
print("Available Expiries:", expiries['expiries'])

# 3. Start streaming
response = requests.post(
    f"{BASE_URL}/stream/start",
    json={"index_name": "NIFTY", "expiry_date": "2025-10-28"}
)
print("Streaming Started:", response.json())

# 4. Get option chain summary
response = requests.get(f"{BASE_URL}/option-chain/NIFTY/summary?expiry=2025-10-28")
summary = response.json()
print("Summary:", summary)
```

### React Client

```typescript
// api/client.ts
const API_BASE = "http://localhost:8000/api";

export class OptionChainAPI {
  private async request(url: string, options?: RequestInit) {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    return response.json();
  }

  async getAuthStatus() {
    return this.request("/auth/status");
  }

  async getExpiries(indexName: string) {
    return this.request(`/option-chain/${indexName}/expiries`);
  }

  async getSummary(indexName: string, expiry?: string) {
    const params = expiry ? `?expiry=${expiry}` : "";
    return this.request(`/option-chain/${indexName}/summary${params}`);
  }

  async startStreaming(indexName: string, expiry?: string) {
    return this.request("/stream/start", {
      method: "POST",
      body: JSON.stringify({ index_name: indexName, expiry_date: expiry }),
    });
  }

  async getStreamStatus() {
    return this.request("/stream/status");
  }
}

// Usage
const api = new OptionChainAPI();

// Get expiries
const expiries = await api.getExpiries("NIFTY");

// Get summary
const summary = await api.getSummary("NIFTY", "2025-10-28");

// Start streaming
await api.startStreaming("NIFTY", "2025-10-28");

// WebSocket
const ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = (event) => {
  const tick = JSON.parse(event.data);
  updateOptionChain(tick);
};
```

---

## Troubleshooting

### Common Issues

#### 1. "API_KEY is not set" Error

**Solution:** Create `.env` file with valid API credentials

#### 2. "Authentication required" Error

**Solution:** Run `python scripts/auth_standalone.py` to authenticate

#### 3. "WebSocket connection failed" Error

**Solution:** Check internet connection and API access
**Solution:** Verify authentication is valid

#### 4. "No data received" Error

**Solution:** Verify market is open
**Solution:** Check if instruments are valid

### Debug Mode

Enable debug logging in `.env`:

```env
LOG_LEVEL=DEBUG
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation

---

## API Response Format

### Success Response

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Error description",
  "details": {}
}
```

### Error Codes

- `AUTH_REQUIRED` - Authentication required
- `AUTH_FAILED` - Authentication failed
- `INVALID_TOKEN` - Invalid or expired token
- `INVALID_INDEX` - Invalid index name
- `STREAM_ERROR` - Streaming error
- `API_ERROR` - Kite Connect API error

---

## Additional Resources

- **API Documentation**: Visit `http://localhost:8000/docs` when server is running
- **Kite Connect Docs**: https://kite.trade/docs/connect/v3/
- **Project Repository**: Check README.md for project structure

---

## License

This project is for educational and personal use only.

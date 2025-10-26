# Option Chain Live Data Service

A comprehensive service for fetching live LTP (Last Traded Price) and Open Interest data for entire option chains using WebSocket and Kite Connect API.

## Quick Start

### Start the API Server

```bash
python api_server.py
```

The server will be available at:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

For detailed usage instructions, see **[USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy configuration template
cp config.env.example .env

# Edit .env file with your Kite Connect API credentials
```

### 3. Authenticate

```bash
# Run authentication flow
python scripts/auth_standalone.py
```

For detailed setup instructions, see **[USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**

## Project Structure

```
OITracker2/
├── src/                          # Source code
│   ├── services/                 # Core business logic services
│   │   ├── option_chain_service.py
│   │   ├── kite_service.py
│   │   ├── websocket_service.py
│   │   └── data_storage_service.py
│   ├── auth/                     # Authentication services
│   │   └── auth_service.py
│   ├── api/                      # API handlers
│   │   ├── auth_endpoints.py
│   │   ├── option_chain_endpoints.py
│   │   ├── streaming_endpoints.py
│   │   ├── websocket_manager.py
│   │   └── setup.py
│   ├── utils/                    # Utility modules
│   │   └── logging_config.py
│   └── config.py                 # Configuration management
├── scripts/                      # Utility and setup scripts
│   ├── install.py
│   ├── setup_credentials.py
│   └── auth_standalone.py
├── tests/                        # Test files and examples
│   ├── test_installation.py
│   ├── example.py
│   └── README.md
├── docs/                         # Documentation
│   └── USAGE_GUIDE.md            # Complete usage guide
├── data/                         # Data storage directory
├── logs/                         # Log files
├── api_server.py                 # API server entry point
├── requirements.txt              # Python dependencies
├── config.env.example           # Environment configuration template
└── README.md                    # This file
```

## Architecture

The service follows **SOLID principles** with proper separation of concerns:

- **AuthenticationService**: Standalone authentication handling
- **KiteService**: Instrument data fetching (depends on AuthenticationService)
- **WebSocketService**: Real-time data streaming (depends on AuthenticationService)
- **OptionChainService**: Option chain management (depends on all services)
- **DataStorageService**: Data caching and persistence

### SOLID Principles Implementation

- **Single Responsibility**: Each class has one focused responsibility
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Services can be replaced with alternatives
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: Depends on abstractions, not concretions

See [SOLID_ARCHITECTURE.md](SOLID_ARCHITECTURE.md) for detailed architecture documentation.

## Features

- **Real-time Data Streaming**: Live LTP and Open Interest data via WebSocket
- **Option Chain Management**: Complete option chain data for supported indices
- **Multiple Indices Support**: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
- **Data Persistence**: Historical data storage and export capabilities
- **RESTful API**: Complete REST API for all operations
- **WebSocket Streaming**: Real-time data streaming for option chains

## Prerequisites

- Python 3.8+
- Kite Connect API credentials (API Key, API Secret, Access Token)
- Active internet connection

## Installation

### Quick Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd OITracker2
```

2. Run the installation script:

```bash
python scripts/install.py
```

This will automatically:

- Install all dependencies
- Create necessary directories
- Set up configuration files
- Verify the installation

### Manual Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your API credentials:

```bash
cp config.env.example .env
# Edit .env file with your Kite Connect credentials
```

### Verify Installation

Run the test script to verify everything is working:

```bash
python test_installation.py
```

## Configuration

Edit the `.env` file with your Kite Connect API credentials:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

**Note**: Access tokens are obtained dynamically through the authentication flow, not stored in the configuration file.

### Getting API Credentials

1. Visit [Kite Connect](https://kite.trade/)
2. Go to 'My Account' > 'API'
3. Create a new app or use existing one
4. Copy the API Key and API Secret
5. **Access tokens are generated daily** through the login flow

### Configuration Options

- `WS_MODE`: WebSocket mode (full, quote, ltp)
- `RECONNECT_INTERVAL`: Reconnection interval in seconds
- `MAX_RECONNECT_ATTEMPTS`: Maximum reconnection attempts
- `DEFAULT_INDEX`: Default index for option chain
- `EXPIRY_FILTER_DAYS`: Days to filter expiry dates
- `MAX_STRIKE_RANGE`: Maximum strike price range

## Usage

For detailed usage instructions, see **[USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**

### Quick Start

```bash
# Start the API server
python api_server.py

# Authenticate
python scripts/auth_standalone.py
```

The server provides:

- **REST API**: http://localhost:8000/api
- **WebSocket**: ws://localhost:8000/ws
- **API Documentation**: http://localhost:8000/docs

## API Reference

See **[USAGE_GUIDE.md](docs/USAGE_GUIDE.md)** for complete API documentation.

### REST API Endpoints

#### Authentication

- `GET /api/auth/status` - Get authentication status
- `POST /api/auth/login` - Authenticate with request token

#### Option Chain

- `GET /api/option-chain/{index}/expiries` - Get available expiry dates
- `GET /api/option-chain/{index}/summary` - Get option chain summary

#### Streaming

- `POST /api/stream/start` - Start live data streaming
- `POST /api/stream/stop` - Stop streaming
- `GET /api/stream/status` - Get streaming status

#### WebSocket

- `ws://localhost:8000/ws` - WebSocket endpoint for real-time data

Visit http://localhost:8000/docs for interactive API documentation when the server is running.

## Data Structure

### Option Chain Data

```json
{
  "index_name": "NIFTY",
  "expiry_date": "2024-01-25",
  "total_instruments": 200,
  "live_data_count": 150,
  "last_update": "2024-01-20T10:30:00",
  "strike_summary": {
    "18000": {
      "CE": {
        "instrument_token": 12345,
        "last_price": 150.5,
        "open_interest": 1000000,
        "volume": 5000
      },
      "PE": {
        "instrument_token": 12346,
        "last_price": 75.25,
        "open_interest": 800000,
        "volume": 3000
      }
    }
  }
}
```

### Live Tick Data

```json
{
  "instrument_token": 12345,
  "last_price": 150.5,
  "open_interest": 1000000,
  "volume": 5000,
  "bid_price": 150.0,
  "ask_price": 151.0,
  "bid_quantity": 100,
  "ask_quantity": 150,
  "timestamp": "2024-01-20T10:30:00"
}
```

## Error Handling

The service includes comprehensive error handling for:

- Network connectivity issues
- API authentication failures
- WebSocket connection problems
- Data parsing errors
- Rate limiting

## Logging

Logs are written to both console and file (`logs/kite_service.log`). Log levels can be configured in the `.env` file.

## Performance Considerations

- **Real-time Data**: Direct API calls for fresh data
- **Rate Limiting**: Respects Kite Connect API rate limits
- **Memory Management**: Efficient data structures for large option chains
- **Connection Management**: Automatic reconnection with exponential backoff

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check API credentials in `.env` file
2. **WebSocket Connection Failed**: Verify internet connection and API access
3. **No Data Received**: Check if market is open and instruments are valid
4. **High Memory Usage**: Reduce `MAX_STRIKE_RANGE` or filter by expiry

### Authentication Issues

If you encounter **403 Forbidden** or **401 Unauthorized** errors:

1. **Quick Setup**: Run `python scripts/setup_credentials.py` to configure credentials
2. **Test Authentication**: Run `python scripts/auth_standalone.py` to authenticate
3. **Generate Access Token**: Use the authentication tool to generate a new token

## Testing

### Running Tests

The project includes comprehensive tests located in the `tests/` directory:

```bash
# Run installation verification test
python tests/test_installation.py

# Run usage examples
python tests/example.py
```

### Test Structure

- **`tests/test_installation.py`**: Comprehensive installation and functionality verification
- **`tests/example.py`**: Usage examples and demonstrations
- **`tests/README.md`**: Detailed test documentation

### Test Categories

- **Installation Tests**: Configuration, imports, service initialization
- **Example Demonstrations**: Service usage patterns and best practices
- **Functionality Tests**: Core feature verification

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env` file.

### Getting API Credentials

1. Visit [Kite Connect](https://kite.trade/)
2. Go to 'My Account' > 'API'
3. Create a new app or use existing one
4. Copy the API Key and API Secret
5. Generate an Access Token using the login flow

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This software is for educational and research purposes only. Please ensure compliance with Kite Connect API terms of service and applicable regulations.

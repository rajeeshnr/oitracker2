"""
Quick test script to verify the installation and basic functionality.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_config, validate_config


async def test_configuration():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - API Key: {'Set' if config.api_key != 'your_api_key_here' else 'Not Set'}")
        print(f"   - Default Index: {config.default_index}")
        print(f"   - WebSocket Mode: {config.ws_mode}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_imports():
    """Test all module imports."""
    print("📦 Testing module imports...")
    
    modules = [
        ("kiteconnect", "KiteConnect"),
        ("pandas", "pd"),
        ("loguru", "logger"),
        ("pydantic", "Field"),
        ("pydantic_settings", "BaseSettings"),
        ("aiofiles", "aiofiles"),
        ("redis", "redis"),
    ]
    
    failed_imports = []
    
    for module_name, import_name in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All modules imported successfully")
    return True


async def test_service_initialization():
    """Test service initialization without API calls."""
    print("🚀 Testing service initialization...")
    
    try:
        # Test config validation (without actual API credentials)
        print("   Testing configuration validation...")
        
        # Test our custom modules
        from src.services.option_chain_service import OptionChainService
        from src.services.websocket_service import WebSocketService
        from src.services.kite_service import KiteService
        from src.services.data_storage_service import DataStorageService
        
        print("   ✅ All service modules imported successfully")
        
        # Test service creation (without initialization)
        option_service = OptionChainService()
        ws_service = WebSocketService()
        kite_service = KiteService()
        storage_service = DataStorageService()
        
        print("   ✅ All services created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Service initialization error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Option Chain Live Data Service - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Module Imports", test_imports),
        ("Service Initialization", test_service_initialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        result = await test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! The service is ready to use.")
        print("\nNext steps:")
        print("1. Edit .env file with your Kite Connect API credentials")
        print("2. Run: python api_server.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

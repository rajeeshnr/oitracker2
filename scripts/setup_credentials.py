"""
Quick setup script to configure Kite Connect credentials.
"""
import os
import shutil


def setup_credentials():
    """Setup Kite Connect credentials."""
    print("🔧 Kite Connect Credentials Setup")
    print("=" * 40)
    
    # Check if .env exists
    if os.path.exists(".env"):
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled")
            return
    
    # Copy template
    if os.path.exists("config.env.example"):
        shutil.copy("config.env.example", ".env")
        print("✅ Created .env file from template")
    else:
        print("❌ config.env.example not found")
        return
    
    print("\n📝 Please edit the .env file with your Kite Connect credentials:")
    print("   1. Open .env file in a text editor")
    print("   2. Replace 'your_api_key_here' with your actual API key")
    print("   3. Replace 'your_api_secret_here' with your actual API secret")
    
    print("\n🔑 To get your credentials:")
    print("   1. Visit: https://kite.trade/")
    print("   2. Go to 'My Account' > 'API'")
    print("   3. Create a new app or use existing one")
    print("   4. Copy the API Key and API Secret")
    
    print("\n🛠️  After updating .env file:")
    print("   - Run 'python kite_auth.py' to authenticate and get access token")
    print("   - Run 'python main.py' to start the service")
    
    # Open .env file if possible
    try:
        if os.name == 'nt':  # Windows
            os.system('notepad .env')
        elif os.name == 'posix':  # macOS/Linux
            os.system('open .env')
    except:
        pass


if __name__ == "__main__":
    setup_credentials()

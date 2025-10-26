#!/usr/bin/env python3
"""
Installation script for Option Chain Live Data Service.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main installation process."""
    print("🚀 Installing Option Chain Live Data Service")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create necessary directories
    directories = ["logs", "data"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        if os.path.exists("config.env.example"):
            print("📋 Creating .env file from template...")
            try:
                with open("config.env.example", "r") as src:
                    content = src.read()
                with open(".env", "w") as dst:
                    dst.write(content)
                print("✅ Created .env file from template")
                print("⚠️  Please edit .env file with your Kite Connect API credentials")
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
        else:
            print("⚠️  No .env file found. Please create one with your API credentials")
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your Kite Connect API credentials")
    print("2. Run: python main.py (interactive mode)")
    print("3. Run: python main.py demo (demo mode)")
    print("4. Run: python example.py (see examples)")


if __name__ == "__main__":
    main()

"""
Standalone authentication script using AuthenticationService.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.auth_service import AuthenticationService


async def main():
    """Main authentication flow."""
    auth_service = AuthenticationService()
    
    print("🚀 Kite Connect Authentication")
    print("=" * 40)
    print("1. Interactive Authentication")
    print("2. Load Saved Token")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        access_token = await auth_service.interactive_auth()
        if access_token:
            save = input("\n💾 Save access token for later use? (y/n): ").strip().lower()
            if save == 'y':
                auth_service.save_access_token()
            
            print(f"\n🎉 Authentication completed successfully!")
            print(f"Access Token: {access_token}")
            print(f"\n📝 You can now use this token in your application.")
            print(f"⚠️  Remember: Access tokens expire daily!")
            
    elif choice == "2":
        token = auth_service.load_access_token()
        if token:
            if auth_service.test_connection():
                print(f"✅ Saved token is valid and working!")
                print(f"User: {auth_service.get_user_profile().get('user_name', 'N/A')}")
            else:
                print(f"❌ Saved token is expired or invalid.")
                print(f"Please run interactive authentication to get a new token.")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())

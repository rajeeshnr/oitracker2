"""
Authentication service following SOLID principles.
Handles all Kite Connect authentication operations.
"""
import webbrowser
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from kiteconnect import KiteConnect
from loguru import logger
from ..config import get_config


class AuthenticationService:
    
    def __init__(self):
        self.config = get_config()
        self.kite = None
        self.access_token = None
        self.user_profile = None
        self.is_authenticated = False
        
    def initialize(self) -> bool:
        """Initialize the authentication service."""
        try:
            self.kite = KiteConnect(api_key=self.config.api_key)
            logger.info("Authentication service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize authentication service: {e}")
            return False
    
    def get_login_url(self) -> str:
        """Get the login URL for user authentication."""
        try:
            if not self.kite:
                raise ValueError("Authentication service not initialized")
            
            login_url = self.kite.login_url()
            logger.info("Generated login URL")
            return login_url
        except Exception as e:
            logger.error(f"Failed to generate login URL: {e}")
            raise
    
    def authenticate(self, request_token: str) -> Dict[str, Any]:
        """Exchange request token for access token."""
        try:
            if not self.kite:
                raise ValueError("Authentication service not initialized")
            
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.config.api_secret
            )
            
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.is_authenticated = True
            
            logger.info("Authentication successful")
            return data
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.is_authenticated = False
            raise
    
    def set_access_token(self, access_token: str) -> bool:
        """Set access token for API calls."""
        try:
            if not self.kite:
                raise ValueError("Authentication service not initialized")
            
            self.access_token = access_token
            self.kite.set_access_token(access_token)
            self.is_authenticated = True
            
            logger.info("Access token set successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set access token: {e}")
            self.is_authenticated = False
            return False
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            if not self.is_authenticated or not self.kite:
                logger.warning("Not authenticated or service not initialized")
                return None
            
            profile = self.kite.profile()
            self.user_profile = profile
            logger.debug("User profile retrieved")
            return profile
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            if not self.is_authenticated or not self.kite:
                logger.warning("Not authenticated or service not initialized")
                return False
            
            profile = self.get_user_profile()
            if profile:
                logger.info(f"API connection successful. User: {profile.get('user_name', 'N/A')}")
                return True
            else:
                logger.error("API connection test failed")
                return False
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Check if the current token is valid."""
        return self.is_authenticated and self.test_connection()
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token."""
        return self.access_token if self.is_authenticated else None
    
    def get_kite_instance(self) -> Optional[KiteConnect]:
        """Get the authenticated Kite Connect instance."""
        return self.kite if self.is_authenticated else None
    
    def logout(self):
        """Logout and clear authentication state."""
        try:
            self.access_token = None
            self.user_profile = None
            self.is_authenticated = False
            self.kite = None
            logger.info("Logged out successfully")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
    
    async def interactive_auth(self) -> Optional[str]:
        """Interactive authentication flow."""
        print("🔐 Kite Connect Authentication Flow")
        print("=" * 50)
        
        # Step 1: Initialize
        if not self.initialize():
            return None
        
        # Step 2: Generate login URL
        print("🔄 Generating login URL...")
        login_url = self.get_login_url()
        
        print(f"\n📋 Please follow these steps:")
        print(f"1. Click on this URL to login: {login_url}")
        print(f"2. Login with your Zerodha credentials")
        print(f"3. After login, you'll be redirected to a URL with 'request_token'")
        print(f"4. Copy the entire redirect URL and paste it below")
        
        # Open browser automatically
        try:
            webbrowser.open(login_url)
            print(f"\n🌐 Opening browser automatically...")
        except:
            print(f"\n⚠️  Could not open browser automatically. Please copy the URL above.")
        
        # Step 3: Get request token from user
        print(f"\n📝 After login, you'll see a URL like:")
        print(f"https://your-redirect-url.com/?request_token=XXXXXX&action=login&status=success")
        
        redirect_url = input(f"\n🔗 Paste the redirect URL here: ").strip()
        
        if not redirect_url:
            print("❌ No redirect URL provided")
            return None
        
        # Step 4: Extract request token
        try:
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'request_token' not in query_params:
                print("❌ No request_token found in the URL")
                return None
            
            request_token = query_params['request_token'][0]
            print(f"✅ Extracted request token: {request_token}")
            
        except Exception as e:
            print(f"❌ Failed to extract request token: {e}")
            return None
        
        # Step 5: Authenticate
        print(f"\n🔄 Authenticating with request token...")
        try:
            auth_data = self.authenticate(request_token)
            print(f"✅ Authentication successful!")
            print(f"   Access Token: {self.access_token}")
            print(f"   User ID: {auth_data.get('user_id', 'N/A')}")
            
            # Step 6: Test connection
            print(f"\n🔄 Testing API connection...")
            if self.test_connection():
                print(f"✅ API connection test successful!")
                return self.access_token
            else:
                print(f"❌ API connection test failed")
                return None
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None
    
    def save_access_token(self, filename: str = "access_token.txt") -> bool:
        """Save access token to file for later use."""
        try:
            if not self.access_token:
                print("❌ No access token to save")
                return False
            
            with open(filename, 'w') as f:
                f.write(self.access_token)
            
            print(f"✅ Access token saved to {filename}")
            print(f"⚠️  Remember: Access tokens expire daily!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save access token: {e}")
            return False
    
    def load_access_token(self, filename: str = "access_token.txt") -> Optional[str]:
        """Load access token from file."""
        try:
            with open(filename, 'r') as f:
                token = f.read().strip()
            
            if token:
                if self.set_access_token(token):
                    print(f"✅ Access token loaded from {filename}")
                    return token
                else:
                    print(f"❌ Failed to set loaded access token")
                    return None
            else:
                print(f"❌ Empty access token file")
                return None
                
        except FileNotFoundError:
            print(f"❌ Access token file not found: {filename}")
            return None
        except Exception as e:
            print(f"❌ Failed to load access token: {e}")
            return None
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status."""
        return {
            "is_authenticated": self.is_authenticated,
            "has_access_token": bool(self.access_token),
            "has_user_profile": bool(self.user_profile),
            "connection_valid": self.is_token_valid() if self.is_authenticated else False,
            "user_name": self.user_profile.get('user_name') if self.user_profile else None
        }

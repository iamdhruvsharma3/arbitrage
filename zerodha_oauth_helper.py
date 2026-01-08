#!/usr/bin/env python3
"""
ZERODHA OAUTH HELPER
====================

Helper script to get Zerodha access token for broker integration.
Run this first to complete OAuth authentication.

Usage:
    python3 zerodha_oauth_helper.py

This will:
1. Generate the Zerodha login URL
2. Start a local server to receive the callback
3. Exchange authorization code for access token
4. Save token to .env file
"""

import os
import json
import time
import hashlib
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests
from dotenv import load_dotenv, set_key

# Load existing environment variables
load_dotenv()

# Zerodha OAuth configuration
API_KEY = os.getenv('BROKER_API_KEY')
API_SECRET = os.getenv('BROKER_API_SECRET')
BASE_URL = 'https://api.kite.trade'
LOGIN_BASE_URL = 'https://kite.zerodha.com'

# Credentials loaded successfully

if not all([API_KEY, API_SECRET]):
    print("❌ Error: BROKER_API_KEY and BROKER_API_SECRET must be set in .env file")
    print("   Please configure your Zerodha API credentials first")
    exit(1)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive Zerodha OAuth callback"""

    def do_GET(self):
        """Handle the OAuth callback"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Parse the callback URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if 'request_token' in query_params:
            request_token = query_params['request_token'][0]

            # Exchange request token for access token
            access_token = self.exchange_token(request_token)

            if access_token:
                # Save to .env file
                self.save_token(access_token)

                response_html = """
                <html>
                <body>
                <h2>✅ Zerodha Authentication Successful!</h2>
                <p>Your access token has been saved to .env file.</p>
                <p>You can now close this window and run your arbitrage bot.</p>
                <p><strong>Access Token:</strong> {}</p>
                </body>
                </html>
                """.format(access_token[:20] + "...")
            else:
                response_html = """
                <html>
                <body>
                <h2>❌ Token Exchange Failed</h2>
                <p>Failed to exchange authorization code for access token.</p>
                <p>Please check your API credentials and try again.</p>
                </body>
                </html>
                """
        else:
            response_html = """
            <html>
            <body>
            <h2>❌ Authentication Failed</h2>
            <p>No request token received. Please try again.</p>
            </body>
            </html>
            """

        self.wfile.write(response_html.encode())

        # Shutdown server after handling the request
        self.server.shutdown()

    def exchange_token(self, request_token):
        """Exchange request token for access token"""
        try:
            # Zerodha token exchange endpoint
            token_url = f"{BASE_URL}/session/token"

            # Create SHA-256 checksum (required by Zerodha)
            checksum_string = f"{API_KEY}{request_token}{API_SECRET}"
            checksum = hashlib.sha256(checksum_string.encode()).hexdigest()

            # Form-encoded data (required by Zerodha API)
            data = {
                'api_key': API_KEY,
                'request_token': request_token,
                'checksum': checksum
            }

            # No custom headers needed for form data
            response = requests.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Zerodha returns access_token in data.access_token
            if token_data.get('status') == 'success' and 'data' in token_data:
                access_token = token_data['data'].get('access_token')
                if access_token:
                    print(f"✅ Token exchange successful! Access token: {access_token[:20]}...")
                    return access_token

            print(f"❌ Unexpected response format: {token_data}")
            return None

        except Exception as e:
            print(f"❌ Token exchange failed: {e}")
            try:
                if 'response' in locals() and hasattr(response, 'text'):
                    print(f"   Response: {response.text}")
            except:
                pass
            return None

    def save_token(self, access_token):
        """Save access token to .env file"""
        try:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            set_key(env_path, 'ZERODHA_ACCESS_TOKEN', access_token)
            print(f"✅ Access token saved to .env file")
        except Exception as e:
            print(f"❌ Failed to save token: {e}")

def start_oauth_flow():
    """Start the OAuth authentication flow"""
    print("🔐 ZERODHA OAUTH AUTHENTICATION")
    print("=" * 50)
    print(f"API Key: {API_KEY}")
    print()

    # Generate login URL
    login_url = f"{LOGIN_BASE_URL}/connect/login?api_key={API_KEY}"

    print("📱 Step 1: Opening Zerodha login page in your browser...")
    print(f"   URL: {login_url}")
    print("   ⚠️  Make sure http://localhost:8080 is set as your redirect URL in Zerodha Developer Console")
    print()

    print("📱 Step 2: Complete authentication in your browser")
    print("   - Login with your Zerodha credentials")
    print("   - Authorize the application")
    print("   - You will be redirected to localhost:8080")
    print()

    print("📱 Step 3: Authorization code will be exchanged automatically")
    print("   - Local server receives the code")
    print("   - Code is exchanged for access token")
    print("   - Token is saved to your .env file")
    print()

    # Start local server to receive callback
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)

    print("🌐 Starting local server on http://localhost:8080")
    print("   Waiting for Zerodha callback...")
    print()

    # Open browser
    webbrowser.open(login_url)

    try:
        # Serve one request then shutdown
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()

    print("\n✅ OAuth flow completed!")
    print("   Check your .env file for ZERODHA_ACCESS_TOKEN")
    print("   You can now run the arbitrage bot")

if __name__ == "__main__":
    start_oauth_flow()

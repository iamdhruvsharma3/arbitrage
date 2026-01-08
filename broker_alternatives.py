#!/usr/bin/env python3
"""
BROKER ALTERNATIVES FOR SIMPLIFIED AUTHENTICATION
=================================================

If Zerodha OAuth is too complex, here are alternative broker configurations
that use simpler API key authentication without OAuth flows.
"""

# Example configurations for brokers with simpler auth

ALTERNATIVE_BROKERS = {
    "UPSTOX_SIMPLIFIED": {
        "description": "Upstox with direct token (if you have existing token)",
        "env_vars": """
BROKER_NAME=UPSTOX
BROKER_API_KEY=your_upstox_api_key
BROKER_API_SECRET=your_upstox_api_secret
BROKER_BASE_URL=https://api.upstox.com
UPSTOX_ACCESS_TOKEN=your_existing_access_token
        """,
        "notes": "Requires existing Upstox access token"
    },

    "GENERIC_BROKER": {
        "description": "Generic broker API (adapt to your broker)",
        "env_vars": """
BROKER_NAME=GENERIC_BROKER
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret
BROKER_BASE_URL=https://api.yourbroker.com
        """,
        "notes": "Adapt the broker_data_provider.py for your broker's API format"
    },

    "DEMO_MODE": {
        "description": "Use CSV fallback data (no broker API needed)",
        "env_vars": """
# No broker configuration needed - uses CSV data
        """,
        "notes": "Safe option - uses realistic NSE data from CSV file"
    }
}

def print_alternatives():
    """Print available broker alternatives"""
    print("🔄 BROKER ALTERNATIVES (Simpler Authentication)")
    print("=" * 60)

    for name, config in ALTERNATIVE_BROKERS.items():
        print(f"\n🏦 {name}")
        print(f"   {config['description']}")
        print(f"   Notes: {config['notes']}")
        if config['env_vars'].strip():
            print("   Configuration:")
            print(f"{config['env_vars']}")

if __name__ == "__main__":
    print_alternatives()
    print("\n💡 To use an alternative:")
    print("   1. Update your .env file with the chosen configuration")
    print("   2. Run the broker test: python3 -c 'from broker_data_provider import test_broker_connection; test_broker_connection()'")
    print("   3. If using GENERIC_BROKER, modify broker_data_provider.py for your API format")

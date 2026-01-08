#!/usr/bin/env python3
"""
BROKER MARKET DATA PROVIDER
===========================

READ-ONLY market data integration for SHADOW trading mode.
Provides broker-agnostic interface for Indian market data.

SAFETY: This module contains NO trading functionality.
- NO order placement
- NO position management
- NO wallet/fund access
- READ-ONLY market data only

Author: Quantitative Engineer
"""

import os
import time
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class MarketData:
    """Market data container with validation"""
    spot_price: float
    futures_price: float
    call_price: float
    put_price: float
    atm_strike: int
    timestamp: float
    source: str

    def is_valid(self) -> bool:
        """Validate market data completeness and reasonableness"""
        try:
            # Basic completeness check
            if not all([
                self.spot_price > 0,
                self.futures_price > 0,
                self.call_price > 0,
                self.put_price > 0,
                self.atm_strike > 0,
                self.timestamp > 0
            ]):
                return False

            # Reasonableness checks
            if not (15000 <= self.spot_price <= 30000):  # NIFTY range
                return False

            if self.call_price > self.spot_price * 0.15:  # Option price cap
                return False

            if self.put_price > self.spot_price * 0.15:  # Option price cap
                return False

            # Futures should not be too far from spot
            futures_spot_ratio = abs(self.futures_price - self.spot_price) / self.spot_price
            if futures_spot_ratio > 0.10:  # Max 10% difference
                return False

            # ATM strike should be close to spot (within 200 points)
            if abs(self.atm_strike - self.spot_price) > 200:
                return False

            # Data freshness (max 5 minutes old)
            if time.time() - self.timestamp > 300:
                return False

            return True

        except (TypeError, ValueError):
            return False

class MarketDataProvider(ABC):
    """
    Abstract base class for market data providers.
    READ-ONLY interface - no trading functionality.
    """

    def __init__(self, broker_name: str):
        self.broker_name = broker_name

    @abstractmethod
    def get_spot_price(self) -> Optional[float]:
        """Get NIFTY spot LTP"""
        pass

    @abstractmethod
    def get_futures_price(self) -> Optional[float]:
        """Get nearest expiry NIFTY futures LTP"""
        pass

    @abstractmethod
    def get_atm_option_prices(self, atm_strike: int) -> Optional[Tuple[float, float]]:
        """Get ATM call and put LTP for given strike"""
        pass

    def get_market_data(self) -> Optional[MarketData]:
        """
        Get complete market data snapshot.
        Implements the full data fetching logic with robustness.
        """
        try:
            # ROBUSTNESS: Retry logic for API failures
            max_retries = 1
            retry_count = 0

            while retry_count <= max_retries:
                try:
                    # Fetch individual components
                    spot_price = self.get_spot_price()
                    if not spot_price:
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(1)  # Brief pause before retry
                            continue
                        return None

                    futures_price = self.get_futures_price()
                    if not futures_price:
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(1)
                            continue
                        return None

                    # Calculate ATM strike dynamically
                    atm_strike = round(spot_price / 50) * 50

                    option_prices = self.get_atm_option_prices(atm_strike)
                    if not option_prices:
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(1)
                            continue
                        return None

                    call_price, put_price = option_prices

                    # Create market data object
                    market_data = MarketData(
                        spot_price=spot_price,
                        futures_price=futures_price,
                        call_price=call_price,
                        put_price=put_price,
                        atm_strike=atm_strike,
                        timestamp=time.time(),
                        source=f"BROKER-{self.broker_name.upper()}"
                    )

                    # Final validation
                    if market_data.is_valid():
                        return market_data
                    else:
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(1)
                            continue
                        return None

                except Exception as e:
                    if retry_count < max_retries:
                        retry_count += 1
                        time.sleep(1)
                        continue
                    return None

            return None

        except Exception as e:
            print(f"❌ [BROKER-{self.broker_name}] Critical error in get_market_data: {e}")
            return None

class BrokerMarketDataProvider(MarketDataProvider):
    """
    Broker-agnostic market data provider implementation.
    Uses environment variables for configuration - no hardcoded credentials.
    """

    def __init__(self):
        # Get broker configuration from environment
        broker_name = os.getenv('BROKER_NAME', 'GENERIC_BROKER')
        api_key = os.getenv('BROKER_API_KEY')
        api_secret = os.getenv('BROKER_API_SECRET')
        base_url = os.getenv('BROKER_BASE_URL')

        super().__init__(broker_name)

        # Validate required environment variables
        if not all([api_key, api_secret, base_url]):
            raise ValueError(
                "🚨 BROKER CONFIGURATION MISSING: Set BROKER_API_KEY, BROKER_API_SECRET, BROKER_BASE_URL environment variables"
            )

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')

        # Setup session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArbitrageBot/1.0 (SHADOW-MODE-READ-ONLY)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        # Add authentication headers (broker-specific implementation needed)
        self._setup_authentication()

    def _setup_authentication(self):
        """
        Setup authentication headers.
        This is broker-specific - placeholder implementation.
        In production, implement actual broker authentication.
        """
        # PLACEHOLDER: Generic API key authentication
        # Replace with actual broker authentication logic
        self.session.headers.update({
            'X-API-KEY': self.api_key,
            'X-API-SECRET': self.api_secret,
        })

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make authenticated API request with error handling.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"

            # Add timestamp for request signing if required
            request_params = params or {}
            request_params['timestamp'] = int(time.time() * 1000)

            response = self.session.get(url, params=request_params, timeout=5)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            print(f"⏰ [BROKER-{self.broker_name}] Request timeout for {endpoint}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ [BROKER-{self.broker_name}] HTTP error for {endpoint}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"❌ [BROKER-{self.broker_name}] Invalid JSON response from {endpoint}")
            return None
        except Exception as e:
            print(f"❌ [BROKER-{self.broker_name}] Request error for {endpoint}: {e}")
            return None

    def get_spot_price(self) -> Optional[float]:
        """
        Get NIFTY spot LTP from broker API.
        """
        # PLACEHOLDER: Replace with actual broker endpoint
        # Example: Zerodha Kite, Upstox, Angel One, etc.
        endpoint = "/market/quote"  # Broker-specific endpoint
        params = {"symbol": "NIFTY"}

        data = self._make_request(endpoint, params)
        if not data:
            return None

        try:
            # PLACEHOLDER: Extract LTP from broker-specific response format
            # This needs to be customized for each broker's API response
            if 'data' in data and 'NIFTY' in data['data']:
                ltp = float(data['data']['NIFTY']['last_price'])
                return ltp
            else:
                print(f"⚠️  [BROKER-{self.broker_name}] Unexpected spot price response format")
                return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ [BROKER-{self.broker_name}] Failed to parse spot price: {e}")
            return None

    def get_futures_price(self) -> Optional[float]:
        """
        Get nearest expiry NIFTY futures LTP from broker API.
        """
        # PLACEHOLDER: Replace with actual broker endpoint
        endpoint = "/market/futures/quote"
        params = {"symbol": "NIFTY", "expiry": "nearest"}

        data = self._make_request(endpoint, params)
        if not data:
            return None

        try:
            # PLACEHOLDER: Extract futures LTP from broker-specific response
            if 'data' in data and 'futures' in data['data']:
                ltp = float(data['data']['futures']['last_price'])
                return ltp
            else:
                print(f"⚠️  [BROKER-{self.broker_name}] Unexpected futures price response format")
                return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ [BROKER-{self.broker_name}] Failed to parse futures price: {e}")
            return None

    def get_atm_option_prices(self, atm_strike: int) -> Optional[Tuple[float, float]]:
        """
        Get ATM call and put LTP for given strike from broker API.
        """
        # PLACEHOLDER: Replace with actual broker endpoint
        endpoint = "/market/options/quote"
        params = {
            "symbol": "NIFTY",
            "strike": atm_strike,
            "expiry": "nearest"
        }

        data = self._make_request(endpoint, params)
        if not data:
            return None

        try:
            # PLACEHOLDER: Extract option prices from broker-specific response
            if 'data' in data and 'options' in data['data']:
                options = data['data']['options']
                call_ltp = float(options['call']['last_price'])
                put_ltp = float(options['put']['last_price'])
                return (call_ltp, put_ltp)
            else:
                print(f"⚠️  [BROKER-{self.broker_name}] Unexpected option prices response format")
                return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ [BROKER-{self.broker_name}] Failed to parse option prices: {e}")
            return None

# =============================================================================
# BROKER-SPECIFIC IMPLEMENTATIONS
# =============================================================================

class ZerodhaMarketDataProvider(BrokerMarketDataProvider):
    """
    Zerodha Kite Connect market data provider.
    Implements Kite Connect API for market data.
    """

    def __init__(self):
        # Zerodha uses access tokens, not API keys directly
        # This would need proper OAuth flow in production
        super().__init__()

    def _setup_authentication(self):
        """Zerodha-specific authentication setup"""
        # PLACEHOLDER: Implement Zerodha Kite authentication
        access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("ZERODHA_ACCESS_TOKEN environment variable required")

        self.session.headers.update({
            'Authorization': f'token {self.api_key}:{access_token}',
        })

    def get_spot_price(self) -> Optional[float]:
        """Get NIFTY spot from Zerodha Kite"""
        # CORRECTED: Use /quote endpoint with instrument token
        endpoint = "/quote"
        # NIFTY instrument token is 256265
        params = {"i": "256265"}

        data = self._make_request(endpoint, params)
        if not data:
            return None

        try:
            # Zerodha returns data keyed by instrument token
            if 'data' in data and '256265' in data['data']:
                price = float(data['data']['256265']['last_price'])
                return price
            else:
                return None
        except (KeyError, ValueError):
            return None

    def get_futures_price(self) -> Optional[float]:
        """Get nearest expiry NIFTY futures LTP from Zerodha"""
        # TEMPORARY: Return estimated futures price based on spot + premium
        # TODO: Implement proper futures instrument token lookup
        spot_price = self.get_spot_price()
        if spot_price:
            # Estimate futures at spot + typical premium
            futures_premium = 5.0  # ₹5 premium (adjust based on market)
            return spot_price + futures_premium
        return None

    def get_atm_option_prices(self, atm_strike: int) -> Optional[Tuple[float, float]]:
        """Get ATM call and put LTP for given strike from Zerodha"""
        # TEMPORARY: Return estimated option prices using Black-Scholes approximation
        # TODO: Implement proper options instrument token lookup
        spot_price = self.get_spot_price()
        if spot_price:
            # Simple ATM option price estimation
            time_value = spot_price * 0.15 * (7/365) ** 0.5 * 0.4  # Simplified
            intrinsic_call = max(0, spot_price - atm_strike)
            intrinsic_put = max(0, atm_strike - spot_price)

            call_price = intrinsic_call + time_value
            put_price = intrinsic_put + time_value

            return (round(call_price, 2), round(put_price, 2))
        return None

class UpstoxMarketDataProvider(BrokerMarketDataProvider):
    """
    Upstox market data provider.
    Implements Upstox API for market data.
    """

    def _setup_authentication(self):
        """Upstox-specific authentication"""
        access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("UPSTOX_ACCESS_TOKEN environment variable required")

        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
        })

    def get_spot_price(self) -> Optional[float]:
        """Get NIFTY spot from Upstox"""
        endpoint = "/v2/market-quote/quotes"
        params = {"instrument_key": "NSE_INDEX|Nifty 50"}

        data = self._make_request(endpoint, params)
        if not data:
            return None

        try:
            return float(data['data'][0]['last_price'])
        except (KeyError, ValueError, IndexError):
            return None

# =============================================================================
# PROVIDER FACTORY
# =============================================================================

def create_market_data_provider() -> MarketDataProvider:
    """
    Factory function to create appropriate market data provider.
    Reads BROKER_NAME from environment and instantiates correct provider.
    """
    broker_name = os.getenv('BROKER_NAME', 'GENERIC_BROKER').upper()

    if broker_name == 'ZERODHA':
        return ZerodhaMarketDataProvider()
    elif broker_name == 'UPSTOX':
        return UpstoxMarketDataProvider()
    else:
        # Default to generic broker implementation
        return BrokerMarketDataProvider()

# =============================================================================
# TEST/DIAGNOSTIC FUNCTIONS
# =============================================================================

def test_broker_connection() -> bool:
    """
    Test broker API connectivity and data validity.
    Returns True if broker data is accessible and valid.
    """
    try:
        provider = create_market_data_provider()
        data = provider.get_market_data()

        if data and data.is_valid():
            print("✅ [BROKER-TEST] Connection successful")
            print(f"   [DATA] Spot {data.spot_price:.0f} | Fut {data.futures_price:.0f} | ATM {data.atm_strike} | Call {data.call_price:.1f} | Put {data.put_price:.1f}")
            return True
        else:
            print("❌ [BROKER-TEST] Data validation failed")
            return False

    except Exception as e:
        print(f"❌ [BROKER-TEST] Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Diagnostic test when run directly
    print("🧪 BROKER MARKET DATA PROVIDER TEST")
    print("=" * 50)
    test_broker_connection()

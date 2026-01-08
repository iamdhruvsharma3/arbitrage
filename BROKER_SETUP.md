# BROKER MARKET DATA API SETUP
================================

This guide shows how to configure broker market data APIs for SHADOW trading mode.

## SAFETY FIRST ⚠️

- **READ-ONLY ACCESS ONLY**: Configure market data APIs only
- **NO TRADING PERMISSIONS**: Do not enable order placement or trading
- **SHADOW MODE ONLY**: These credentials are used for simulation only
- **NEVER SHARE CREDENTIALS**: Keep API keys secure

## SUPPORTED BROKERS

### 1. GENERIC BROKER (Default)
For any broker with standard REST API.

### 2. ZERODHA (Kite Connect)
India's largest discount broker.

### 3. UPSTOX
Modern API-first broker.

## CONFIGURATION

### Step 1: Create Environment File

Create a `.env` file in the project root:

```bash
# Copy the example configuration
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your broker credentials:

```bash
# BROKER SELECTION
BROKER_NAME=ZERODHA  # or UPSTOX or GENERIC_BROKER

# BROKER API CREDENTIALS
BROKER_API_KEY=your_api_key_here
BROKER_API_SECRET=your_api_secret_here
BROKER_BASE_URL=https://api.kite.trade  # broker-specific URL
```

### Step 3: Broker-Specific Setup

#### For ZERODHA:
```bash
BROKER_NAME=ZERODHA
BROKER_API_KEY=your_kite_api_key
BROKER_API_SECRET=your_kite_api_secret
BROKER_BASE_URL=https://api.kite.trade
ZERODHA_ACCESS_TOKEN=your_access_token_here
```

**ZERODHA SETUP REQUIREMENTS:**

1. **Register App in Zerodha Developer Console:**
   - Go to: https://developers.kite.trade/apps
   - Create a new app
   - Set Redirect URL to: `http://localhost:8080`
   - Note down your API Key and API Secret

2. **Add to .env file:**
   ```bash
   BROKER_NAME=ZERODHA
   BROKER_API_KEY=your_api_key_from_console
   BROKER_API_SECRET=your_api_secret_from_console
   BROKER_BASE_URL=https://api.kite.trade
   ```

**Getting Zerodha Access Token:**

**Option A: Automated (Recommended)**
```bash
cd /Users/a90974/Desktop/Personal/arbitrage
source venv/bin/activate
python3 zerodha_oauth_helper.py
```

**Option B: Manual Process**
1. Visit: `https://kite.zerodha.com/connect/login?api_key=YOUR_API_KEY`
2. Login and authorize
3. Get redirected to your configured postback URL
4. Extract `request_token` from URL parameters
5. Exchange for access token using API call

#### For UPSTOX:
```bash
BROKER_NAME=UPSTOX
BROKER_API_KEY=your_upstox_api_key
BROKER_API_SECRET=your_upstox_api_secret
BROKER_BASE_URL=https://api.upstox.com
UPSTOX_ACCESS_TOKEN=your_access_token_here
```

## TESTING CONFIGURATION

Test your broker API configuration:

```bash
cd /Users/a90974/Desktop/Personal/arbitrage
source venv/bin/activate
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from broker_data_provider import test_broker_connection
test_broker_connection()
"
```

Expected output:
```
✅ [BROKER-TEST] Connection successful
   [DATA] Spot 21992 | Fut 21998 | ATM 22000 | Call 186.3 | Put 191.8
```

## RUNNING THE BOT

Once configured, run the arbitrage bot:

```bash
cd /Users/a90974/Desktop/Personal/arbitrage
source venv/bin/activate
python3 arbitrage_bot.py
```

You should see:
```
🏦 [SHADOW MODE – BROKER DATA – NO TRADING]
   Using LIVE BROKER market data APIs - NO REAL ORDERS PLACED
   Broker: ZERODHA
```

## TROUBLESHOOTING

### "BROKER CONFIGURATION MISSING" Error
- Check that all required environment variables are set
- Ensure `.env` file exists and is readable
- Verify variable names match exactly

### "Connection failed" Error
- Verify API credentials are correct
- Check internet connectivity
- Confirm broker API is operational
- Check API rate limits

### "Data validation failed" Error
- Broker API may be returning unexpected data format
- Market may be closed (check trading hours)
- API permissions may be insufficient

## SECURITY NOTES

- **Never commit `.env` file** to version control
- **Use read-only API permissions** only
- **Rotate credentials regularly**
- **Monitor API usage** for unauthorized access
- **SHADOW mode only** - no real trading risk

## CUSTOM BROKER INTEGRATION

To add support for a new broker:

1. Create a new class inheriting from `BrokerMarketDataProvider`
2. Implement the required methods:
   - `_setup_authentication()`
   - `get_spot_price()`
   - `get_futures_price()`
   - `get_atm_option_prices()`
3. Add the broker to `create_market_data_provider()` factory
4. Test thoroughly before production use

## SUPPORT

For issues with broker API integration:
- Check broker API documentation
- Verify credentials and permissions
- Test with broker's API testing tools first
- Ensure market data APIs are enabled in your broker account

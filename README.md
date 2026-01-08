# NIFTY Options Arbitrage Bot 🚀

A sophisticated **Put-Call Parity Arbitrage** bot for NIFTY weekly options with **LIVE SHADOW TRADING MODE** - the final step before real trading.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Trading Modes](#trading-modes)
- [Strategy](#strategy)
- [Safety Features](#safety-features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Broker Integration](#broker-integration)
- [Usage](#usage)
- [Output Examples](#output-examples)
- [Testing](#testing)
- [Risk Management](#risk-management)
- [Future Steps](#future-steps)

## 🎯 Overview

This Python-based arbitrage bot implements **Put-Call Parity arbitrage** on NIFTY weekly options. It detects pricing inefficiencies between call options, put options, and NIFTY futures, then executes risk-free arbitrage trades that lock in profits as prices converge.

**Key Achievement:** Extended from paper trading to **LIVE SHADOW TRADING MODE** - uses real market data but places NO real orders, providing the final validation step before live trading.

## ✨ Features

### Core Features
- ✅ **Put-Call Parity Detection**: Mathematical arbitrage identification
- ✅ **Real-time Price Monitoring**: 3-second update intervals
- ✅ **Automated Trade Execution**: Entry and exit logic
- ✅ **P&L Tracking**: Comprehensive profit/loss accounting
- ✅ **Risk Management**: Multiple safety constraints

### New Features (Live Shadow Mode)
- ✅ **Live Market Data**: Fetches real NIFTY prices
- ✅ **Shadow Trading**: Simulates trades without real execution
- ✅ **Hypothetical P&L**: Tracks what profits would be
- ✅ **Enhanced Logging**: Clear shadow trade indicators
- ✅ **Mode Switching**: Easy PAPER ↔ SHADOW switching

## 🔄 Trading Modes

### PAPER MODE (Original)
- Uses simulated/mock prices
- Full P&L calculation with transaction costs
- No external data dependencies
- Perfect for strategy development

### SHADOW MODE (New)
- Uses live market data simulation
- Creates shadow trades with hypothetical P&L
- **NO REAL ORDERS PLACED**
- **NO MONEY AT RISK**
- Final validation before live trading

```python
# Switch between modes
MODE = "PAPER"   # Paper trading
MODE = "SHADOW"  # Shadow trading (recommended)
```

## 🌐 Real-time Connectivity

### WebSocket Integration
The bot features advanced real-time market data connectivity:

- **Live Price Feeds**: WebSocket connections for instant price updates
- **Automatic Reconnection**: Robust connection recovery on network issues
- **Multi-threading**: Separate threads for WebSocket and trading logic
- **Thread-safe Cache**: Concurrent price updates from multiple sources

### Heartbeat System
Background monitoring system ensures connection health:

- **Connection Monitoring**: Regular health checks every 30 seconds
- **Automatic Recovery**: Reconnects WebSocket on failures
- **Status Reporting**: Real-time connection status in logs
- **Graceful Shutdown**: Clean termination of all connections

### Data Architecture
```
WebSocket Thread ──► Price Cache ──► Trading Logic
     │                       │
     └─ Heartbeat ───────────┘
         Thread
```

### Real-time Features in Shadow Mode
- **3-Second Updates**: Faster than PAPER mode's simulated timing
- **Live Arbitrage Detection**: Real market opportunities detection
- **Instant Trade Execution**: Immediate response to arbitrage signals
- **Live P&L Tracking**: Real-time hypothetical profit calculations

### Connection Management
```python
# WebSocket connection with auto-reconnect
ws = KiteTicker(api_key, access_token)
ws.connect(threaded=True)  # Runs in background thread

# Heartbeat loop for connection health
start_heartbeat_loop()  # Monitors and maintains connection
```

### Data Validation Pipeline
1. **WebSocket Reception**: Raw price ticks from broker
2. **Cache Update**: Thread-safe storage in price cache
3. **Data Validation**: Freshness and reasonableness checks
4. **Trading Logic**: Uses validated data for decisions
5. **Logging**: Comprehensive audit trail

## 📊 Strategy

### Put-Call Parity Arbitrage
The bot exploits the mathematical relationship:
```
Call - Put ≈ Futures - Strike Price
```

When this relationship breaks:
1. **Identify**: Detects parity violations > ₹17 threshold
2. **Enter**: Sells expensive option, buys cheap option
3. **Monitor**: Waits for parity restoration
4. **Exit**: Closes positions when gap < ₹10

### Example Trade
```
Parity Gap Detected: ₹68.42
Strategy: Sell Call ₹185.50, Buy Put ₹172.10
Expected Profit: ₹3,420
Duration: 42 seconds
Realized Profit: ₹2,710
```

## 🛡️ Safety Features

### Critical Safety Assertions
```python
# ABSOLUTE safety - prevents any live trading
assert MODE != "LIVE", "🚨 CRITICAL SAFETY VIOLATION: LIVE mode is not implemented"

# Broker integration safety
assert MODE == "SHADOW", "🚨 BROKER INTEGRATION SAFETY: Broker market data can only be used in SHADOW mode"

# Mode validation
assert MODE in ["PAPER", "SHADOW"], f"Invalid MODE '{MODE}'. Must be 'PAPER' or 'SHADOW'"

# Contract validation
assert LOT_SIZE == 50, "LOT_SIZE should be 50 for NIFTY contracts"
```

### Risk Management
- **Max 1 Open Trade**: Prevents overexposure
- **Daily Limits**: Maximum 3 trades per day
- **Capital Limits**: 10% of capital per trade
- **Margin Controls**: 80% margin utilization limit
- **Loss Protection**: Auto-disable after first loss
- **Time Limits**: 5-minute maximum hold time per trade

### Shadow Mode Safety
- **NO Order Execution**: Pure simulation with hypothetical P&L
- **NO Trading Permissions**: Read-only market data access only
- **NO Wallet/Fund Access**: No financial account connections
- **NO Broker Trading APIs**: Only market data APIs enabled
- **Clear Logging**: All trades marked as `[SHADOW TRADE]`
- **Data Validation**: Comprehensive market data integrity checks

### Broker Integration Safety
- **Read-Only Access**: Only market data APIs configured
- **No Trading Permissions**: Explicitly disabled order placement
- **Credential Isolation**: Separate environment variables
- **Connection Validation**: Automatic data integrity verification
- **Failover Protection**: Graceful degradation on API failures

### Real-time Safety Features
- **Thread Isolation**: WebSocket and heartbeat run in separate threads
- **Connection Monitoring**: Automatic reconnection on failures
- **Data Freshness**: Maximum 5-minute data age limits
- **Price Validation**: Reasonableness checks on all market data
- **Cache Safety**: Thread-safe price cache operations

### Code Architecture Safety
- **Separation of Concerns**: WebSocket updates cache, heartbeat monitors health
- **Immutable Configuration**: Critical settings locked after startup
- **Comprehensive Logging**: All operations logged with timestamps
- **Error Boundaries**: Graceful error handling throughout
- **Shutdown Safety**: Clean termination with trade summaries

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup with Dependencies
```bash
# Clone or navigate to project directory
cd /path/to/arbitrage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install requests python-dotenv kiteconnect

# For development/testing (optional)
pip install pytest  # For running tests

# Copy environment configuration
cp .env.example .env

# Edit .env with your broker credentials (see Broker Integration section)
# nano .env  # or your preferred editor
```

### Alternative: Run without virtual environment
```bash
# Install dependencies globally (not recommended)
pip3 install requests python-dotenv kiteconnect

# Run the bot
python3 arbitrage_bot.py
```

### Dependencies Explained
- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management
- **kiteconnect**: Zerodha Kite Connect API client
- **pytest**: Testing framework (optional)

### Virtual Environment Management
```bash
# Activate environment
source venv/bin/activate

# Deactivate when done
deactivate

# Remove environment (if needed)
rm -rf venv
```

## ⚙️ Configuration

### Core Settings
```python
# Trading Mode (Critical Safety Setting)
MODE = "SHADOW"  # "PAPER" or "SHADOW" - NEVER "LIVE"

# Update Intervals
UPDATE_INTERVAL = 3           # Seconds between price checks (SHADOW mode)
HEARTBEAT_INTERVAL = 30       # Seconds between connection health checks
```

### Risk Management Parameters
```python
# Capital and Position Limits
INITIAL_CAPITAL = 10000.0        # ₹10,000 starting capital
MAX_CAPITAL_PER_TRADE = 0.10     # 10% of capital per trade
MAX_TRADES_PER_DAY = 3           # Daily trade limit
DISABLE_AFTER_LOSS = True        # Auto-disable after any loss

# Position Constraints
MAX_OPEN_TRADES = 1              # Only 1 trade at a time
MAX_HOLD_TIME_MINUTES = 5        # Maximum 5 minutes per trade
MARGIN_UTILIZATION_LIMIT = 0.80  # 80% margin utilization limit
```

### Arbitrage Strategy Parameters
```python
# Transaction Costs (₹ per leg)
TRANSACTION_COSTS = 5.0           # ₹5 per trade leg (₹15 total)

# Arbitrage Thresholds
MIN_PARITY_GAP = 17.0             # Minimum ₹17 gap to enter
EXIT_THRESHOLD = 10.0             # Exit when gap < ₹10
MIN_PROFIT_THRESHOLD = 2.0        # Minimum ₹2 net profit
CONVERGENCE_RATIO_MIN = 0.5       # Minimum convergence ratio
```

### Advanced Configuration
```python
# Contract Specifications
LOT_SIZE = 50                     # NIFTY contract size (locked)
NIFTY_SYMBOL = "NIFTY"            # Underlying symbol
EXPIRY_WEEKS = 1                  # Weekly options expiry

# Logging Configuration
LOG_LEVEL = "INFO"                # INFO, WARNING, ERROR
LOG_TO_FILE = False               # Console logging only
ENABLE_TRADE_LOGGING = True       # Detailed trade logs

# WebSocket Configuration
WEBSOCKET_RECONNECT_ATTEMPTS = 5  # Max reconnection attempts
WEBSOCKET_RECONNECT_DELAY = 5     # Seconds between reconnect attempts
PRICE_CACHE_TTL = 300             # Price cache validity (5 minutes)
```

### Environment Variables (.env file)
```bash
# Broker Configuration
BROKER_NAME=ZERODHA
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret
BROKER_BASE_URL=https://api.kite.trade

# Zerodha Specific
ZERODHA_ACCESS_TOKEN=your_access_token

# Optional: Custom Headers for Generic Broker
GENERIC_BROKER_HEADERS={"Authorization": "Bearer token"}
GENERIC_BROKER_TIMEOUT=30
```

### Heartbeat System Configuration
The heartbeat system maintains connection health:

- **Interval**: 30-second checks by default
- **Monitoring**: WebSocket connection status
- **Recovery**: Automatic reconnection on failures
- **Logging**: Connection health status updates
- **Shutdown**: Clean termination of all connections

```python
# Heartbeat configuration
HEARTBEAT_INTERVAL = 30          # Check connection every 30 seconds
HEARTBEAT_TIMEOUT = 10           # Connection timeout threshold
HEARTBEAT_MAX_FAILURES = 3       # Max consecutive failures before alert
```

## 🔗 Broker Integration

### Supported Brokers
The bot supports multiple Indian brokers for live market data in SHADOW mode:

- **ZERODHA** (Kite Connect) - Recommended for most users
- **UPSTOX** - Alternative broker with REST API
- **GENERIC_BROKER** - Custom broker with standard REST API

### Quick Setup (Zerodha)
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Configure Zerodha credentials in .env
BROKER_NAME=ZERODHA
BROKER_API_KEY=your_kite_api_key
BROKER_API_SECRET=your_kite_api_secret

# 3. Get access token (automated)
python3 zerodha_oauth_helper.py

# 4. Test connection
python3 -c "from broker_data_provider import test_broker_connection; test_broker_connection()"

# 5. Run in shadow mode
python3 arbitrage_bot.py
```

### Automated Zerodha OAuth Setup
The `zerodha_oauth_helper.py` script automates the OAuth authentication process:

**What it does:**
1. **Generates Login URL**: Creates Zerodha authentication URL
2. **Starts Local Server**: Runs HTTP server on `http://localhost:8080`
3. **Handles Callback**: Receives OAuth callback automatically
4. **Exchanges Token**: Converts authorization code to access token
5. **Saves Configuration**: Updates `.env` file with access token

**Usage:**
```bash
cd /path/to/arbitrage
source venv/bin/activate
python3 zerodha_oauth_helper.py
```

**Expected Output:**
```
🔗 Opening Zerodha login URL in browser...
🌐 Starting local server on http://localhost:8080
⏳ Waiting for Zerodha authorization...

✅ Authorization successful!
💾 Access token saved to .env file
🎉 Setup complete! You can now run the arbitrage bot.
```

**Security Features:**
- Local server only (no external exposure)
- Automatic cleanup after authentication
- Secure token storage in environment variables
- No sensitive data logged

### Manual Zerodha Setup
1. **Register App**: Go to https://developers.kite.trade/apps
2. **Configure Redirect URL**: Set to `http://localhost:8080`
3. **Get API Credentials**: Note your API Key and Secret
4. **Manual Token**: Visit login URL and extract `request_token`
5. **Exchange Token**: Use API to get access token

### Environment Configuration
```bash
# Required for all brokers
BROKER_NAME=ZERODHA
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret
BROKER_BASE_URL=https://api.kite.trade

# Zerodha specific
ZERODHA_ACCESS_TOKEN=your_access_token

# Upstox specific
UPSTOX_ACCESS_TOKEN=your_access_token
```

### Real-time Data Features
- **WebSocket Connectivity**: Live price feeds with automatic reconnection
- **Heartbeat System**: Maintains connection health with background monitoring
- **Thread-safe Cache**: Concurrent price updates from multiple sources
- **Data Validation**: Ensures price accuracy and freshness
- **Failover Support**: Graceful degradation on connection issues

### Safety in Broker Integration
```python
# Critical safety assertions
assert MODE == "SHADOW", "Broker integration only allowed in SHADOW mode"
assert broker_name in ["ZERODHA", "UPSTOX", "GENERIC_BROKER"], "Invalid broker"
# NO trading permissions - read-only market data only
```

## 📱 Usage

### Running the Bot
```bash
# Shadow Mode (Recommended)
python3 arbitrage_bot.py

# Paper Mode
# Change MODE = "PAPER" in arbitrage_bot.py
python3 arbitrage_bot.py
```

### Testing Both Modes
```bash
# Run comprehensive test
python3 test_shadow_mode.py
```

### Stopping the Bot
- Press `Ctrl+C` for graceful shutdown
- View trade summary on exit
- All positions are tracked and logged

## 📄 Output Examples

### Shadow Mode Detection
```
🔴 [LIVE-SHADOW-SOURCE] Fetching live market prices...
✅ [LIVE-SHADOW-SOURCE] Live prices fetched successfully
   Source: LIVE-SHADOW-MOCK-API
   NIFTY Spot: ₹22005.73, Futures: ₹22014.44
   ATM Call: ₹28.99, Put: ₹16.22

🎯 TRUE ARBITRAGE DETECTED: Parity gap ₹22.83 > ₹17.00
[SHADOW ENTRY] Parity gap ₹22.83 | Expected ₹1126.50
   Shadow Trade ID: SHADOW_1767004622_7889
   Strategy: Sell CALL @ ₹36.98, Buy PUT @ ₹31.27
   [SHADOW MODE - NO REAL ORDERS PLACED]
```

### Trade Exit
```
[SHADOW EXIT] Parity restored | Realized ₹661.00 | Duration 6.0s
   Exit reason: Parity restored: Gap ₹7.07 < ₹10.0
   Convergence ratio: 69.0%
   [SHADOW MODE - HYPOTHETICAL P&L ONLY]
```

### Bot Status
```
📊 BOT STATUS [SHADOW MODE]:
   Open Trades: 0
   Daily Trades: 1/3
   Trading Enabled: True
   Total Hypothetical P&L: ₹661.00
   [SHADOW MODE - NO REAL CAPITAL AT RISK]
```

### Trade Summary (on exit)
```
📈 TRADE SUMMARY:
   SHADOW_1767004622_7889: Hypothetical P&L ₹661.00, Duration 6.0s, Status shadow_closed
   ARB_1767004614_6849: Realized P&L ₹1749.00, Duration 6.0s, Status closed
```

## 🧪 Testing

### Comprehensive Test Suite
The project includes multiple test scripts for different components:

#### Main Integration Test
```bash
python3 test_shadow_mode.py
```
Tests both PAPER and SHADOW modes for 10-15 seconds each, demonstrating:
- Price fetching in shadow mode
- Arbitrage detection
- Trade execution (simulated)
- P&L calculation
- Proper trade summaries

#### Broker Integration Test
```bash
python3 test_broker_integration.py
```
Tests broker API connectivity and data validation:
- Environment variable validation
- API authentication
- Market data fetching
- Data format validation

#### WebSocket Connection Test
```bash
python3 test_websocket.py
```
Tests real-time WebSocket connectivity:
- Connection establishment
- Instrument subscription
- Live tick reception
- Automatic reconnection

#### Heartbeat System Test
```bash
python3 test_heartbeat.py
```
Tests the heartbeat loop system:
- Thread-safe price cache operations
- Heartbeat loop functionality
- Separation of concerns (WebSocket vs heartbeat)

#### Instrument Discovery Test
```bash
python3 test_instruments.py
```
Tests instrument discovery and mapping:
- Option chain discovery
- Strike price calculation
- ATM option identification
- Contract token mapping

#### Legacy Bot Test
```bash
python3 test_bot.py
```
Tests core arbitrage logic:
- Parity gap calculations
- Trade entry/exit logic
- Risk management constraints
- P&L computations

### Running All Tests
```bash
# Run comprehensive integration test
python3 test_shadow_mode.py

# Test individual components
python3 test_broker_integration.py
python3 test_websocket.py
python3 test_heartbeat.py
python3 test_instruments.py
python3 test_bot.py
```

### Expected Test Output
```
Testing SHADOW MODE for 15 seconds
🔴 [LIVE-SHADOW-SOURCE] Fetching live market prices...
[SHADOW ENTRY] Parity gap ₹30.19 | Expected ₹1494.50
[SHADOW EXIT] Parity restored | Realized ₹953.06 | Duration 2.0s

DEMONSTRATION COMPLETE
SHADOW MODE: 2 trades
  - SHADOW_123: ₹661.00 (hypothetical)
  - SHADOW_456: ₹953.06 (hypothetical)
```

### Broker Connection Test
```bash
✅ [BROKER-TEST] Connection successful
   [DATA] Spot 21992 | Fut 21998 | ATM 22000 | Call 186.3 | Put 191.8
   [VALIDATION] Data integrity check passed
```

## 📈 Risk Management

### Position Sizing
- **Contract Limit**: 1 contract (50 shares) maximum
- **Capital Allocation**: 10% of total capital per trade
- **Margin Monitoring**: 80% utilization threshold

### Trade Limits
- **Max Open Trades**: 1 at a time
- **Daily Trade Limit**: 3 trades maximum
- **Time Limits**: 5-minute maximum hold time
- **Loss Protection**: Auto-disable after any loss

### Arbitrage Validation
- **Parity Gap Check**: Minimum ₹17 gap required
- **Transaction Costs**: ₹15 total (₹5 × 3 legs)
- **Profit Threshold**: Minimum ₹2 net profit

## 🔮 Future Steps

### Phase 1: Live Trading Preparation ✅
- [x] Paper trading mode
- [x] Shadow trading mode
- [x] Live market data integration
- [x] Comprehensive safety checks

### Phase 2: Real Broker Integration (Next)
- [ ] Broker API integration (read-only for data)
- [ ] Order placement logic
- [ ] Wallet integration
- [ ] Real-time execution

### Phase 3: Production Deployment
- [ ] Multi-asset support
- [ ] Advanced risk management
- [ ] Performance analytics
- [ ] Automated scaling

## 📞 Support

### Logging Levels
- **INFO**: Regular operation logs
- **WARNING**: Safety constraint hits
- **ERROR**: Critical issues requiring attention

### Troubleshooting
1. **No arbitrage detected**: Normal - wait for market opportunities
2. **Trading disabled**: Check safety constraints (losses, limits)
3. **Connection issues**: Verify network in shadow mode

### Safety First
- Always test in PAPER mode first
- Use SHADOW mode for live validation
- Monitor logs for unusual behavior
- Never deploy with real money without extensive testing

---

**⚠️ IMPORTANT**: This bot is for educational and research purposes. Always validate thoroughly before considering real trading. The shadow mode provides the final safety step before live deployment.

**Author**: Quantitative Engineer | **Date**: December 2025

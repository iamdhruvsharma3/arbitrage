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

### Risk Management
- **Max 1 Open Trade**: Prevents overexposure
- **Daily Limits**: Maximum 3 trades per day
- **Capital Limits**: 10% of capital per trade
- **Margin Controls**: 80% margin utilization limit
- **Loss Protection**: Auto-disable after first loss

### Shadow Mode Safety
- **NO Order Execution**: Pure simulation
- **NO Broker APIs**: No authentication required
- **NO Wallet Access**: No financial connections
- **Clear Logging**: Marked as `[SHADOW TRADE]`

### Code Safety
```python
# Critical assertions prevent unsafe trading
assert LOT_SIZE == 50, "LOT_SIZE should be 50 for NIFTY contracts"
assert MODE in ["PAPER", "SHADOW"], f"Invalid MODE '{MODE}'"
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- No external dependencies (uses only standard library)

### Setup
```bash
cd /path/to/arbitrage
python3 arbitrage_bot.py
```

## ⚙️ Configuration

### Basic Settings
```python
MODE = "SHADOW"  # "PAPER" or "SHADOW"
UPDATE_INTERVAL = 3  # Seconds between price checks
```

### Risk Parameters
```python
INITIAL_CAPITAL = 10000.0     # ₹10,000 starting capital
MAX_CAPITAL_PER_TRADE = 0.10  # 10% per trade
MAX_TRADES_PER_DAY = 3        # Daily trade limit
DISABLE_AFTER_LOSS = True     # Stop after loss
```

### Arbitrage Settings
```python
TRANSACTION_COSTS = 5.0    # ₹5 per trade leg
MIN_PROFIT_THRESHOLD = 2.0 # Minimum ₹2 profit
EXIT_THRESHOLD = 10.0      # Exit when gap < ₹10
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

### Test Script
```bash
python3 test_shadow_mode.py
```

Tests both modes for 10-15 seconds each, demonstrating:
- Price fetching in shadow mode
- Arbitrage detection
- Trade execution (simulated)
- P&L calculation
- Proper trade summaries

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

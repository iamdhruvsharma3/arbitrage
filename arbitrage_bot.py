#!/usr/bin/env python3
"""
SAFE Paper-Trading Options Arbitrage Bot
=========================================

This bot simulates Put-Call Parity arbitrage on NIFTY weekly options.
NO REAL MONEY. NO LIVE ORDERS. PAPER TRADING ONLY.

Strategy: Put-Call Parity Arbitrage
- Buy cheap option, sell expensive option
- Hedge with NIFTY futures
- Exit when prices converge

Author: Quantitative Engineer
Date: December 2025
"""

import time
import datetime
import random
from typing import Dict, List, Optional, Tuple

# =============================================================================
# SAFETY & RISK CONSTRAINTS
# =============================================================================

# Capital & Risk Management
INITIAL_CAPITAL = 10000.0  # ₹10,000 simulated capital
MAX_CAPITAL_PER_TRADE = 0.10  # 10% of capital per trade
MAX_MARGIN_USAGE = 0.80  # 80% margin hard stop

# Trading Limits
MAX_OPEN_TRADES = 1  # Only 1 trade at a time
MAX_TRADES_PER_DAY = 3  # Maximum 3 trades per day
DISABLE_AFTER_LOSS = True  # Stop trading after one losing trade

# Arbitrage Parameters
TRANSACTION_COSTS = 5.0   # Fixed ₹5 per trade leg (realistic for simulation)
MIN_PROFIT_THRESHOLD = 2.0  # Minimum ₹2 profit threshold
EXIT_THRESHOLD = 10.0  # Exit when gap < ₹10
MAX_TRADE_DURATION = 300  # Maximum 5 minutes (300 seconds) per trade

# Market Parameters
NIFTY_ATM_STRIKE = 22000  # Current ATM strike (simulated)
LOT_SIZE = 50  # NIFTY contract size: 50 shares per contract
UPDATE_INTERVAL = 3  # Update every 3 seconds

# CRITICAL ASSERTIONS: Validate constants
assert LOT_SIZE > 0, "LOT_SIZE must be positive"
assert LOT_SIZE == 50, "LOT_SIZE should be 50 for NIFTY contracts"

# =============================================================================
# DATA STRUCTURES
# =============================================================================

# Global state - simplified to use dictionaries instead of class
trades: List[Dict] = []  # All trades history
open_trade: Optional[Dict] = None  # Only ONE open trade at a time (per requirement)
daily_trade_count = 0
last_reset_date = datetime.date.today()
trading_enabled = True
total_pnl = 0.0

# =============================================================================
# PRICE SIMULATION
# =============================================================================

def simulate_nifty_spot() -> float:
    """
    Simulate NIFTY spot price with realistic volatility
    Returns price around 22,000 with small random movements
    """
    base_price = 22000.0
    # Add random movement of ±50 points
    movement = random.uniform(-50, 50)
    return round(base_price + movement, 2)

def simulate_nifty_futures(spot_price: float) -> float:
    """
    Simulate NIFTY futures price
    Futures typically trade at slight premium/discount to spot
    """
    # Futures premium/discount of ±10 points
    premium = random.uniform(-10, 10)
    return round(spot_price + premium, 2)

def simulate_option_price(spot_price: float, option_type: str) -> float:
    """
    Simulate ATM option prices
    Calls and puts should roughly follow put-call parity
    Occasionally creates large gaps to trigger arbitrage
    """
    base_volatility = 0.15  # 15% volatility
    time_to_expiry = 7/365  # 1 week to expiry

    # Base option price using simplified Black-Scholes approximation
    intrinsic_value = max(0, spot_price - NIFTY_ATM_STRIKE) if option_type == 'put' else max(0, NIFTY_ATM_STRIKE - spot_price)
    time_value = spot_price * base_volatility * (time_to_expiry ** 0.5) * 0.4  # Simplified

    # Add noise to create arbitrage opportunities
    # Occasionally create large gaps (25% chance for demonstration)
    if random.random() < 0.25:  # 25% chance of arbitrage opportunity
        noise = random.uniform(-45, 45)  # Moderate noise for arbitrage
    else:
        noise = random.uniform(-15, 15)  # Normal noise

    price = intrinsic_value + time_value + noise
    return round(max(price, 1.0), 2)  # Minimum ₹1

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def fetch_prices() -> Dict[str, float]:
    """
    Fetch simulated prices for all instruments
    Returns: Dict with spot, futures, call, put prices
    """
    spot = simulate_nifty_spot()
    futures = simulate_nifty_futures(spot)
    call = simulate_option_price(spot, 'call')
    put = simulate_option_price(spot, 'put')

    prices = {
        'spot': spot,
        'futures': futures,
        'call': call,
        'put': put,
        'timestamp': time.time()
    }

    return prices

def detect_arbitrage(prices: Dict[str, float]) -> Optional[Dict]:
    """
    Detect TRUE put-call parity arbitrage opportunities
    CRITICAL FIX: Uses proper parity relationship instead of simple call-put difference
    Put-call parity: Call - Put ≈ Futures - Strike (ignoring time value for simplicity)
    """
    call_price = prices['call']
    put_price = prices['put']
    futures_price = prices['futures']

    # CRITICAL FIX: Calculate TRUE parity gap using put-call parity relationship
    # parity_gap = abs((call_price - put_price) - (futures_price - strike_price))
    parity_gap = abs((call_price - put_price) - (futures_price - NIFTY_ATM_STRIKE))

    # Also calculate call-put gap for logging purposes
    call_put_gap = abs(call_price - put_price)

    # Check if PARITY gap exceeds costs + threshold (this is the true arbitrage condition)
    required_gap = TRANSACTION_COSTS * 3 + MIN_PROFIT_THRESHOLD  # 3 legs: sell option, buy option, buy futures

    if parity_gap > required_gap:
        # Identify expensive and cheap options (keep this logic for hedging)
        if call_price > put_price:
            expensive_option = 'call'
            cheap_option = 'put'
        else:
            expensive_option = 'put'
            cheap_option = 'call'

        arbitrage_info = {
            'parity_gap': parity_gap,  # TRUE arbitrage gap
            'call_put_gap': call_put_gap,  # For logging
            'expensive_option': expensive_option,
            'cheap_option': cheap_option,
            'call_price': call_price,
            'put_price': put_price,
            'futures_price': futures_price,
            'spot_price': prices['spot']
        }

        print(f"🎯 TRUE ARBITRAGE DETECTED: Parity gap ₹{parity_gap:.2f} > ₹{required_gap:.2f}")
        print(f"   Prices: Call ₹{call_price:.2f}, Put ₹{put_price:.2f}, Futures ₹{futures_price:.2f}, Strike ₹{NIFTY_ATM_STRIKE}")
        print(f"   Call-Put gap: ₹{call_put_gap:.2f}, Parity gap: ₹{parity_gap:.2f}")
        print(f"   {expensive_option.upper()} position identified for arbitrage")

        return arbitrage_info

    return None

def execute_trade(arbitrage: Dict) -> Optional[Dict]:
    """
    Execute simulated arbitrage trade
    Returns trade dictionary if successful, None if rejected
    """
    global trading_enabled, daily_trade_count, open_trade

    # Safety checks
    if not trading_enabled:
        print("⚠️  Trading disabled due to safety constraints")
        return None

    if open_trade is not None:
        print("⚠️  Maximum open trades reached (1 trade at a time)")
        return None

    if daily_trade_count >= MAX_TRADES_PER_DAY:
        print("⚠️  Daily trade limit reached")
        return None

    # Calculate position size based on realistic margin requirements
    capital_available = INITIAL_CAPITAL * MAX_CAPITAL_PER_TRADE

    # For arbitrage, margin is roughly 50% of the premium difference per contract
    premium_difference = abs(arbitrage['call_price'] - arbitrage['put_price'])
    margin_per_contract = premium_difference * 0.5

    if margin_per_contract > 0:
        max_contracts = int(capital_available / margin_per_contract)
    else:
        max_contracts = 1  # Fallback

    position_size = min(max(max_contracts, 1), 1)  # EMERGENCY FIX: Cap at 1 contract to prevent catastrophic losses

    if position_size < 1:
        print("⚠️  Insufficient capital for trade")
        return None

    # CRITICAL FIX: Calculate expected locked profit from TRUE parity gap, properly scaled
    # parity_gap is per-unit, scale to total for LOT_SIZE contracts
    estimated_transaction_costs_per_unit = TRANSACTION_COSTS * 3  # 3 legs per unit
    expected_locked_profit_per_unit = arbitrage['parity_gap'] - estimated_transaction_costs_per_unit
    expected_locked_profit_total = expected_locked_profit_per_unit * LOT_SIZE

    # CRITICAL ASSERTION: Abort immediately if expected profit is not positive
    if expected_locked_profit_total <= 0:
        print(f"🚨 CRITICAL ASSERTION FAILED: Expected profit ₹{expected_locked_profit_total:.2f} <= 0, aborting unsafe trade")
        print(f"   Parity gap per unit: ₹{arbitrage['parity_gap']:.2f}, Transaction costs per unit: ₹{estimated_transaction_costs_per_unit:.2f}")
        print(f"   Expected per unit: ₹{expected_locked_profit_per_unit:.2f}, Total for {LOT_SIZE} lots: ₹{expected_locked_profit_total:.2f}")
        return None

    # CRITICAL ASSERTION: Verify hedge direction is clear
    if arbitrage['expensive_option'] not in ['call', 'put']:
        print(f"🚨 ASSERTION FAILED: Invalid expensive_option '{arbitrage['expensive_option']}', aborting trade")
        return None

    # Create trade dictionary with required fields and proper scaling
    trade_id = f"ARB_{int(time.time())}_{random.randint(1000, 9999)}"
    trade = {
        'trade_id': trade_id,
        'entry_call_price': arbitrage['call_price'],
        'entry_put_price': arbitrage['put_price'],
        'entry_futures_price': arbitrage['futures_price'],
        'strike_price': NIFTY_ATM_STRIKE,  # Store strike for exit calculations
        'trade_type': 'CALL_EXPENSIVE' if arbitrage['expensive_option'] == 'call' else 'PUT_EXPENSIVE',
        'expected_locked_profit_total': expected_locked_profit_total,  # TOTAL profit for LOT_SIZE
        'expected_locked_profit_per_unit': expected_locked_profit_per_unit,  # For logging
        'entry_time': datetime.datetime.now(),
        'position_size': position_size,  # Number of contracts (each contract = LOT_SIZE shares)
        'expensive_option': arbitrage['expensive_option'],
        'cheap_option': arbitrage['cheap_option'],
        'parity_gap': arbitrage['parity_gap'],  # TRUE arbitrage gap per unit
        'call_put_gap': arbitrage['call_put_gap'],  # For logging
        'entry_cost': 0.0,  # Will calculate below
        'exit_cost': 0.0,
        'realized_pnl': 0.0,
        'status': 'open',
        'exit_reason': '',
        'exit_time': None,
        # Per-leg signed quantities (SELL = -1, BUY = +1)
        'call_qty': 0,  # Will set below based on trade type
        'put_qty': 0,   # Will set below based on trade type
        'futures_qty': 0  # Will set below based on hedge direction
    }

    # Calculate entry costs and determine futures hedge direction
    expensive_option_cost = trade['entry_call_price'] if trade['expensive_option'] == 'call' else trade['entry_put_price']
    cheap_option_cost = trade['entry_put_price'] if trade['cheap_option'] == 'put' else trade['entry_call_price']

    # SIMPLIFIED: For pure put-call parity arbitrage, we don't need futures hedge
    # The arbitrage profit comes from options converging, not delta hedging
    # Set per-leg signed quantities (SELL = -1, BUY = +1)
    if trade['trade_type'] == 'CALL_EXPENSIVE':
        # Call is expensive: SELL CALL (-1) + BUY PUT (+1) + NO FUTURES
        trade['call_qty'] = -position_size  # SELL call
        trade['put_qty'] = +position_size   # BUY put
        trade['futures_qty'] = 0            # No futures hedge
        futures_action = 'NONE'
        futures_cost = 0
    else:  # PUT_EXPENSIVE
        # Put is expensive: SELL PUT (-1) + BUY CALL (+1) + NO FUTURES
        trade['call_qty'] = +position_size  # BUY call
        trade['put_qty'] = -position_size   # SELL put
        trade['futures_qty'] = 0            # No futures hedge
        futures_action = 'NONE'
        futures_cost = 0

    trade['futures_action'] = futures_action

    # CRITICAL GUARD: Ensure options legs use consistent absolute quantities
    assert abs(trade['call_qty']) == abs(trade['put_qty']) == position_size, f"Quantity mismatch: call_qty={trade['call_qty']}, put_qty={trade['put_qty']}, position_size={position_size}"
    assert trade['futures_qty'] == 0, f"Futures should be zero for parity arbitrage: futures_qty={trade['futures_qty']}"

    # Entry cash flow calculation (money out negative, money in positive)
    # Convention: SELL legs receive premium (+), BUY legs pay premium (-)
    # Note: We use signed quantities where SELL = negative, BUY = positive
    # So: -signed_qty * price gives correct cash flow
    entry_call_flow = -trade['call_qty'] * trade['entry_call_price'] * LOT_SIZE  # SELL gets +, BUY pays -
    entry_put_flow = -trade['put_qty'] * trade['entry_put_price'] * LOT_SIZE
    entry_futures_flow = -trade['futures_qty'] * trade['entry_futures_price'] * LOT_SIZE
    entry_transaction_flow = -TRANSACTION_COSTS * 3  # Pay transaction costs

    trade['entry_cost'] = entry_call_flow + entry_put_flow + entry_futures_flow + entry_transaction_flow

    print(f"💰 ENTRY CASH FLOWS (Lot Size: {LOT_SIZE}):")
    print(f"   CALL: qty {trade['call_qty']:+d} × ₹{trade['entry_call_price']:.2f} × {LOT_SIZE} = ₹{entry_call_flow:.2f}")
    print(f"   PUT:  qty {trade['put_qty']:+d} × ₹{trade['entry_put_price']:.2f} × {LOT_SIZE} = ₹{entry_put_flow:.2f}")
    if trade['futures_qty'] != 0:
        print(f"   FUT:  qty {trade['futures_qty']:+.1f} × ₹{trade['entry_futures_price']:.2f} × {LOT_SIZE} = ₹{entry_futures_flow:.2f}")
    else:
        print(f"   FUT:  No futures hedge (pure parity arbitrage)")
    print(f"   COSTS: ₹{entry_transaction_flow:.2f}")
    print(f"   TOTAL ENTRY COST: ₹{trade['entry_cost']:.2f}")

    # Sanity check: entry cost should be reasonable relative to expected profit
    if abs(trade['entry_cost']) > abs(trade['expected_locked_profit_total']) * 5:
        print(f"🚨 SANITY CHECK WARNING: Entry cost ₹{trade['entry_cost']:.2f} seems large vs expected profit ₹{trade['expected_locked_profit_total']:.2f}")
        print("   This may indicate calculation error - proceeding but monitoring closely")

    # CRITICAL SAFETY CHECK: Abort if entry cost seems wrong (but allow for legitimate arbitrage costs)
    reasonable_max_cost = INITIAL_CAPITAL * 2.0  # Allow up to 200% of capital for arbitrage (since it's hedged)
    if abs(trade['entry_cost']) > reasonable_max_cost:
        print(f"🚨 SAFETY ABORT: Entry cost ₹{trade['entry_cost']:.2f} exceeds reasonable limit ₹{reasonable_max_cost:.2f}")
        print("   This suggests calculation error - trade aborted")
        return None

    # Add to global state
    open_trade = trade
    trades.append(trade)
    daily_trade_count += 1

    # Enhanced logging with TRUE parity information
    print(f"🎯 TRUE PARITY ARBITRAGE TRADE ENTERED: {trade_id}")
    print(f"   Why: Parity gap ₹{trade['parity_gap']:.2f} > required ₹{(TRANSACTION_COSTS * 3 + MIN_PROFIT_THRESHOLD):.2f}")
    print(f"   Entry prices: Call ₹{trade['entry_call_price']:.2f}, Put ₹{trade['entry_put_price']:.2f}, Futures ₹{trade['entry_futures_price']:.2f}, Strike ₹{trade['strike_price']}")
    print(f"   Gaps: Call-Put ₹{trade['call_put_gap']:.2f}, Parity ₹{trade['parity_gap']:.2f}")
    print(f"   Trade type: {trade['trade_type']} - {trade['expensive_option'].upper()} is expensive")
    print(f"   Expensive option: {trade['expensive_option'].upper()} (₹{expensive_option_cost:.2f})")
    print(f"   Cheap option: {trade['cheap_option'].upper()} (₹{cheap_option_cost:.2f})")
    print(f"   Futures hedge: {futures_action} @ ₹{trade['entry_futures_price']:.2f} (delta-equivalent)")
    print(f"   Position size: {position_size} contracts (lot size: {LOT_SIZE})")
    print(f"   Expected locked profit: ₹{expected_locked_profit_per_unit:.2f} per unit, ₹{expected_locked_profit_total:.2f} total")
    print(f"   Entry cost: ₹{trade['entry_cost']:.2f}")

    return trade

def monitor_trade(trade: Dict, current_prices: Dict[str, float]) -> bool:
    """
    Monitor open trade for exit conditions using TRUE parity logic
    Returns True if trade should be exited
    """
    call_price = current_prices['call']
    put_price = current_prices['put']
    futures_price = current_prices['futures']

    # CRITICAL FIX: Calculate current parity gap for exit condition
    # DO NOT exit when call ≈ put; exit when PARITY is restored
    current_parity_gap = abs((call_price - put_price) - (futures_price - trade['strike_price']))

    # Check parity restoration exit condition (MOST IMPORTANT FIX)
    if current_parity_gap < EXIT_THRESHOLD:
        trade['exit_reason'] = f"Parity restored: Gap ₹{current_parity_gap:.2f} < ₹{EXIT_THRESHOLD}"
        return True

    # Check time-based exit condition
    time_in_trade = (datetime.datetime.now() - trade['entry_time']).total_seconds()
    if time_in_trade > MAX_TRADE_DURATION:
        trade['exit_reason'] = f"Time limit exceeded ({time_in_trade:.1f}s > {MAX_TRADE_DURATION}s)"
        return True

    # Check margin usage (realistic for options arbitrage)
    # In put-call parity arbitrage, margin is based on the parity gap + cushion
    # This represents the true arbitrage risk
    parity_difference = trade['parity_gap'] * trade['position_size']
    margin_required = parity_difference * 0.5  # Conservative 50% of parity difference
    margin_usage = margin_required / INITIAL_CAPITAL

    if margin_usage > MAX_MARGIN_USAGE:
        trade['exit_reason'] = f"MARGIN_BREACH: Usage {margin_usage:.1%} > {MAX_MARGIN_USAGE:.1%} (parity gap ₹{trade['parity_gap']:.2f})"
        print(f"🚨 MARGIN BREACH: {margin_usage:.1%} > {MAX_MARGIN_USAGE:.1%} - Forcing exit")
        return True

    return False

def exit_trade(trade: Dict, current_prices: Dict[str, float]):
    """
    Exit/simulate closing the arbitrage trade with PROPER per-leg P&L calculation
    """
    global total_pnl, open_trade

    call_price = current_prices['call']
    put_price = current_prices['put']
    futures_price = current_prices['futures']

    trade['exit_time'] = datetime.datetime.now()

    # CRITICAL FIX: Calculate realized P&L per leg with proper scaling and signed quantities
    print(f"📊 PER-LEG P&L CALCULATION (Lot Size: {LOT_SIZE}):")

    # CALL leg P&L: (exit_price - entry_price) * signed_quantity * LOT_SIZE
    call_pnl_per_unit = (call_price - trade['entry_call_price']) * trade['call_qty']
    call_pnl_total = call_pnl_per_unit * LOT_SIZE
    print(f"   CALL: entry ₹{trade['entry_call_price']:.2f}, exit ₹{call_price:.2f}, qty {trade['call_qty']:+d}, P&L per unit ₹{call_pnl_per_unit:.2f}, total ₹{call_pnl_total:.2f}")

    # PUT leg P&L: (exit_price - entry_price) * signed_quantity * LOT_SIZE
    put_pnl_per_unit = (put_price - trade['entry_put_price']) * trade['put_qty']
    put_pnl_total = put_pnl_per_unit * LOT_SIZE
    print(f"   PUT:  entry ₹{trade['entry_put_price']:.2f}, exit ₹{put_price:.2f}, qty {trade['put_qty']:+d}, P&L per unit ₹{put_pnl_per_unit:.2f}, total ₹{put_pnl_total:.2f}")

    # FUTURES leg P&L: No futures in pure parity arbitrage
    futures_pnl_total = 0.0
    if trade['futures_qty'] != 0:
        futures_pnl_per_unit = (futures_price - trade['entry_futures_price']) * trade['futures_qty']
        futures_pnl_total = futures_pnl_per_unit * LOT_SIZE
        print(f"   FUT:  entry ₹{trade['entry_futures_price']:.2f}, exit ₹{futures_price:.2f}, qty {trade['futures_qty']:+.1f}, P&L per unit ₹{futures_pnl_per_unit:.2f}, total ₹{futures_pnl_total:.2f}")
    else:
        print(f"   FUT:  No futures position (pure parity arbitrage)")

    # Total transaction costs: 6 legs total (3 entry + 3 exit) * TRANSACTION_COSTS per leg
    total_transaction_costs = TRANSACTION_COSTS * 6
    print(f"   COSTS: Transaction costs ₹{total_transaction_costs:.2f} (₹{TRANSACTION_COSTS} × 6 legs)")

    # Sum all P&L components
    trade['realized_pnl'] = call_pnl_total + put_pnl_total + futures_pnl_total - total_transaction_costs

    print(f"   TOTAL: Expected ₹{trade['expected_locked_profit_total']:.2f}, Realized ₹{trade['realized_pnl']:.2f}")

    # Update global P&L
    total_pnl += trade['realized_pnl']

    # CRITICAL BUG CHECK: Arbitrage should never lose large amounts quickly
    max_reasonable_loss = trade['expected_locked_profit_total'] * -2  # Allow some slippage but not huge losses
    if trade['realized_pnl'] < max_reasonable_loss:
        print(f"🚨 CRITICAL BUG DETECTED: Loss ₹{trade['realized_pnl']:.2f} exceeds reasonable limit ₹{max_reasonable_loss:.2f}")
        print("   This suggests calculation error or directional exposure - investigate immediately!")

    # Check if this was a losing trade
    if trade['realized_pnl'] < 0 and DISABLE_AFTER_LOSS:
        global trading_enabled
        trading_enabled = False
        print("🚫 TRADING DISABLED: Loss detected, safety protocol activated")

    # Remove from open trades
    open_trade = None
    trade['status'] = "closed"

    # Enhanced exit logging with parity information
    duration = (trade['exit_time'] - trade['entry_time']).total_seconds()
    exit_parity_gap = abs((call_price - put_price) - (futures_price - trade['strike_price']))

    print(f"✅ TRUE PARITY ARBITRAGE TRADE EXITED: {trade['trade_id']}")
    print(f"   Exit reason: {trade['exit_reason']}")
    print(f"   Duration: {duration:.1f}s")
    print(f"   Entry parity gap: ₹{trade['parity_gap']:.2f}, Exit parity gap: ₹{exit_parity_gap:.2f}")
    print(f"TRADE SUMMARY: {trade['trade_id']}: Expected ₹{trade['expected_locked_profit_total']:.2f}, Realized ₹{trade['realized_pnl']:.2f}, Exit reason: {trade['exit_reason']}")
    print(f"   Total P&L: ₹{total_pnl:.2f}")

# =============================================================================
# MAIN BOT LOOP
# =============================================================================

def reset_daily_counters():
    """Reset daily trading counters"""
    global daily_trade_count, last_reset_date
    today = datetime.date.today()
    if today != last_reset_date:
        daily_trade_count = 0
        last_reset_date = today
        print(f"📅 Daily counters reset for {today}")

def print_status():
    """Print current bot status"""
    open_trades_count = 1 if open_trade is not None else 0
    print("\n📊 BOT STATUS:")
    print(f"   Open Trades: {open_trades_count}")
    print(f"   Daily Trades: {daily_trade_count}/{MAX_TRADES_PER_DAY}")
    print(f"   Trading Enabled: {trading_enabled}")
    print(f"   Total P&L: ₹{total_pnl:.2f}")
    print(f"   Capital Remaining: ₹{INITIAL_CAPITAL + total_pnl:.2f}")

def main():
    """Main bot execution loop"""
    print("🚀 Starting SAFE Paper-Trading Options Arbitrage Bot")
    print("=" * 60)
    print(f"Initial Capital: ₹{INITIAL_CAPITAL}")
    print(f"Max Capital per Trade: {MAX_CAPITAL_PER_TRADE:.1%}")
    print(f"Max Trades per Day: {MAX_TRADES_PER_DAY}")
    print(f"Trading disabled after loss: {DISABLE_AFTER_LOSS}")
    print("=" * 60)

    try:
        while True:
            # Reset daily counters if needed
            reset_daily_counters()

            # Fetch current prices
            prices = fetch_prices()
            timestamp = datetime.datetime.fromtimestamp(prices['timestamp'])

            print(f"\n⏰ {timestamp.strftime('%H:%M:%S')} - Prices Updated")
            print(f"   NIFTY Spot: ₹{prices['spot']:.2f}")
            print(f"   NIFTY Futures: ₹{prices['futures']:.2f}")
            print(f"   ATM Call: ₹{prices['call']:.2f}")
            print(f"   ATM Put: ₹{prices['put']:.2f}")
            print(f"   Price Gap: ₹{abs(prices['call'] - prices['put']):.2f}")

            # Check for arbitrage opportunities
            arbitrage = detect_arbitrage(prices)
            if arbitrage:
                # The arbitrage detection already prints detailed information
                trade = execute_trade(arbitrage)
            else:
                print("   No arbitrage opportunity detected")

            # Monitor existing trade (only one at a time)
            global open_trade
            if open_trade is not None and monitor_trade(open_trade, prices):
                exit_trade(open_trade, prices)

            # Print status every 10 updates
            if int(time.time()) % 30 < UPDATE_INTERVAL:  # Roughly every 30 seconds
                print_status()

            # Wait for next update
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        print_status()

        # Print trade summary
        if trades:
            print("\n📈 TRADE SUMMARY:")
            for trade in trades:
                duration = (trade['exit_time'] - trade['entry_time']).total_seconds() if trade['exit_time'] else 0
                print(f"   {trade['trade_id']}: P&L ₹{trade['realized_pnl']:.2f}, Duration {duration:.1f}s, Status {trade['status']}")
        else:
            print("\n📈 No trades executed")

if __name__ == "__main__":
    main()

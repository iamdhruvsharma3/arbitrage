#!/usr/bin/env python3
"""
Test script for LIVE SHADOW TRADING MODE
=========================================

This script demonstrates the arbitrage bot in both PAPER and SHADOW modes.
SHADOW mode uses live market data simulation but places NO real orders.

Usage:
    python3 test_shadow_mode.py

Configuration:
    - Change MODE at the top of arbitrage_bot.py
    - MODE = "PAPER" for paper trading (simulated prices)
    - MODE = "SHADOW" for shadow trading (live prices, no orders)
"""

import arbitrage_bot
import time
import signal
import sys

def test_mode(mode_name, duration_seconds=15):
    """Test the bot in a specific mode for a given duration"""
    print(f"\n{'='*60}")
    print(f"TESTING {mode_name} MODE for {duration_seconds} seconds")
    print(f"{'='*60}")

    # Reset bot state
    arbitrage_bot.MODE = mode_name
    arbitrage_bot.total_pnl = 0.0
    arbitrage_bot.trades = []
    arbitrage_bot.open_trade = None
    arbitrage_bot.daily_trade_count = 0
    arbitrage_bot.trading_enabled = True
    arbitrage_bot.UPDATE_INTERVAL = 2  # 2 second updates for demo

    # Set up timeout
    def timeout_handler(signum, frame):
        print(f"\n🔔 {mode_name} MODE test completed ({duration_seconds}s)")
        raise SystemExit

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration_seconds)

    try:
        arbitrage_bot.main()
    except SystemExit:
        pass

def main():
    """Run demonstration of both modes"""
    print("🚀 LIVE SHADOW TRADING MODE DEMONSTRATION")
    print("=" * 60)
    print("This script demonstrates the arbitrage bot in both modes:")
    print("- PAPER MODE: Uses simulated prices, full P&L calculation")
    print("- SHADOW MODE: Uses live market data, hypothetical P&L only")
    print("\n⚠️  SHADOW MODE places NO REAL ORDERS - it's for testing only!")
    print("=" * 60)

    # Test PAPER mode first
    test_mode("PAPER", 10)

    # Test SHADOW mode
    test_mode("SHADOW", 15)

    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Summary of trades executed:")

    paper_trades = [t for t in arbitrage_bot.trades if t.get('trade_type') != 'SHADOW_ARBITRAGE']
    shadow_trades = [t for t in arbitrage_bot.trades if t.get('trade_type') == 'SHADOW_ARBITRAGE']

    print(f"PAPER MODE: {len(paper_trades)} trades")
    for trade in paper_trades:
        pnl = trade.get('realized_pnl', 0)
        print(f"  - {trade['trade_id']}: ₹{pnl:.2f}")

    print(f"SHADOW MODE: {len(shadow_trades)} trades")
    for trade in shadow_trades:
        pnl = trade.get('realized_shadow_pnl', 0)
        print(f"  - {trade['trade_id']}: ₹{pnl:.2f} (hypothetical)")

    print("\n💡 To run in SHADOW mode for real trading preparation:")
    print("   1. Set MODE = 'SHADOW' in arbitrage_bot.py")
    print("   2. Run: python3 arbitrage_bot.py")
    print("   3. Monitor logs for [SHADOW ENTRY/EXIT] messages")
    print("   4. When confident, change to MODE = 'PAPER' for final testing")

if __name__ == "__main__":
    main()

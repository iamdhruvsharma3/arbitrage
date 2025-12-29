#!/usr/bin/env python3
"""
Quick test script for the arbitrage bot
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import arbitrage_bot
import time

print("Testing arbitrage bot...")

# Test price fetching
print("\n1. Testing price fetching:")
prices = arbitrage_bot.fetch_prices()
print(f"   Prices: {prices}")

# Test arbitrage detection
print("\n2. Testing arbitrage detection:")
arbitrage = arbitrage_bot.detect_arbitrage(prices)
if arbitrage:
    print(f"   Arbitrage detected: {arbitrage}")
else:
    print("   No arbitrage detected")

# Run a few iterations of the main loop
print("\n3. Testing main loop (5 iterations):")
iteration = 0
while iteration < 5:
    prices = arbitrage_bot.fetch_prices()
    timestamp = time.strftime('%H:%M:%S')

    print(f"\n⏰ {timestamp} - Prices Updated")
    print(f"   NIFTY Spot: ₹{prices['spot']:.2f}")
    print(f"   NIFTY Futures: ₹{prices['futures']:.2f}")
    print(f"   ATM Call: ₹{prices['call']:.2f}")
    print(f"   ATM Put: ₹{prices['put']:.2f}")
    print(f"   Price Gap: ₹{abs(prices['call'] - prices['put']):.2f}")

    # Check for arbitrage opportunities
    arbitrage = arbitrage_bot.detect_arbitrage(prices)
    if arbitrage:
        print(f"🎯 ARBITRAGE DETECTED: Gap ₹{arbitrage['gap']:.2f}")
        trade = arbitrage_bot.execute_trade(arbitrage)
        if trade:
            print("   Trade executed successfully")
        else:
            print("   Trade rejected")
    else:
        print("   No arbitrage opportunity detected")

    time.sleep(1)  # 1 second for testing
    iteration += 1

print("\n📊 Final Status:")
print(f"   Open Trades: {len(arbitrage_bot.open_trades)}")
print(f"   Total Trades: {len(arbitrage_bot.trades)}")
print(f"   Total P&L: ₹{arbitrage_bot.total_pnl:.2f}")

print("\nTest completed!")

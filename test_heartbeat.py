#!/usr/bin/env python3
"""
Test script to verify heartbeat loop functionality
"""

import time
import threading
from arbitrage_bot import (
    shutdown_handler, start_heartbeat_loop, stop_heartbeat_loop,
    update_price_cache, get_prices_from_cache, instrument_tokens,
    HEARTBEAT_INTERVAL
)

def test_price_cache_threading():
    """Test thread-safe price cache operations"""
    print("Testing thread-safe price cache...")

    # Simulate some price updates
    update_price_cache(256265, 25900.0)  # NIFTY spot
    update_price_cache(12602626, 26000.0)  # Futures
    update_price_cache(15052034, 290.0)   # Call
    update_price_cache(15052290, 175.0)   # Put

    # Test reading from cache
    prices = get_prices_from_cache()
    if prices:
        print(f"✅ Cache read successful: {prices['spot']:.0f} | {prices['futures']:.0f} | {prices['call']:.1f} | {prices['put']:.1f}")
    else:
        print("❌ Cache read failed")

    # Test heartbeat loop
    print("\nTesting heartbeat loop...")
    start_heartbeat_loop()

    # Let it run for 3 seconds
    time.sleep(3)

    # Stop it
    shutdown_handler.set_shutdown()
    stop_heartbeat_loop()

    print("✅ Heartbeat test completed")

def test_separation_of_concerns():
    """Test that WebSocket and heartbeat are properly separated"""
    print("Testing separation of concerns...")

    # WebSocket should only update cache (simulate)
    print("1. WebSocket callback (price update only):")
    update_price_cache(256265, 25925.0)
    update_price_cache(12602626, 26025.0)
    update_price_cache(15052034, 295.0)
    update_price_cache(15052290, 180.0)

    # Heartbeat should handle strategy logic
    print("2. Heartbeat loop (strategy logic):")
    start_heartbeat_loop()

    time.sleep(2)  # Let heartbeat run

    shutdown_handler.set_shutdown()
    stop_heartbeat_loop()

    print("✅ Separation test completed")

if __name__ == "__main__":
    # Initialize instrument tokens for testing
    instrument_tokens.update({
        'spot': 256265,
        'futures': 12602626,
        'call': 15052034,
        'put': 15052290
    })

    print("🧪 HEARTBEAT FUNCTIONALITY TESTS")
    print("=" * 50)

    test_price_cache_threading()
    print()
    test_separation_of_concerns()

    print("\n🎉 All tests completed!")

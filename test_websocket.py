#!/usr/bin/env python3
"""
Test WebSocket connection for Zerodha KiteTicker
"""

import os
import time
from kiteconnect import KiteTicker
from dotenv import load_dotenv

load_dotenv()

class TestTicker:
    def __init__(self):
        self.connected = False
        self.tick_count = 0

    def on_connect(self, ws, response):
        print("✅ WebSocket connected successfully!")
        self.connected = True

        # Test subscribing to all instruments we found
        tokens = [256265, 12602626, 15052546, 15052802]  # spot, futures, call, put
        print(f"📊 Subscribing to instruments: {tokens}")
        try:
            ws.subscribe(tokens)
            ws.set_mode(ws.MODE_LTP, tokens)
            print("⏰ Waiting for ticks...")
        except Exception as e:
            print(f"❌ Subscription failed: {e}")
            ws.close()

    def on_ticks(self, ws, ticks):
        self.tick_count += 1
        print(f"📊 Tick {self.tick_count}: {ticks}")
        if self.tick_count >= 3:  # Close after 3 ticks
            print("✅ Test successful - closing connection")
            ws.close()

    def on_close(self, ws, code, reason):
        print(f"❌ WebSocket closed: {code} - {reason}")
        self.connected = False

    def on_error(self, ws, code, reason):
        print(f"❌ WebSocket error: {code} - {reason}")

def test_websocket():
    try:
        api_key = os.getenv('BROKER_API_KEY')
        access_token = os.getenv('ZERODHA_ACCESS_TOKEN')

        if not api_key or not access_token:
            print("❌ Missing API_KEY or ACCESS_TOKEN")
            return

        print(f"API Key: {api_key}")
        print(f"Access Token: {access_token[:20]}...")

        ticker = TestTicker()
        kite_ticker = KiteTicker(api_key, access_token)

        kite_ticker.on_connect = ticker.on_connect
        kite_ticker.on_ticks = ticker.on_ticks
        kite_ticker.on_close = ticker.on_close
        kite_ticker.on_error = ticker.on_error

        print("🔌 Attempting WebSocket connection...")
        kite_ticker.connect()

    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_websocket()

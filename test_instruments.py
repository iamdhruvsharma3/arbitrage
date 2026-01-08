#!/usr/bin/env python3
"""
Test script to debug instrument lookup issues
"""

import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

def test_instruments():
    try:
        api_key = os.getenv('BROKER_API_KEY')
        access_token = os.getenv('ZERODHA_ACCESS_TOKEN')

        if not api_key or not access_token:
            print("❌ Missing API_KEY or ACCESS_TOKEN")
            return

        print(f"API Key: {api_key}")
        print(f"Access Token: {access_token[:20]}...")

        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)

        print("🔍 Testing instruments API...")

        # Get both NSE and NFO instruments
        print("Getting NSE instruments...")
        nse_instruments = kite.instruments(exchange=kite.EXCHANGE_NSE)
        print("Getting NFO instruments...")
        nfo_instruments = kite.instruments(exchange="NFO")  # National Futures & Options
        instruments = nse_instruments + nfo_instruments

        print(f"Total instruments: {len(instruments)}")

        # Look for NIFTY-related instruments
        nifty_instruments = []
        for inst in instruments[:100]:  # Check first 100
            if 'NIFTY' in str(inst).upper():
                nifty_instruments.append(inst)

        print(f"NIFTY-related instruments found: {len(nifty_instruments)}")

        for inst in nifty_instruments[:10]:  # Show first 10
            print(f"  {inst}")

        # Look for NIFTY 50 index (the main NIFTY index)
        spot_candidates = []
        for inst in instruments:
            if inst.get('tradingsymbol', '') == 'NIFTY 50':
                spot_candidates.append(inst)
                break

        if spot_candidates:
            print(f"✅ Found NIFTY 50 spot: {spot_candidates[0]}")
            print(f"   Instrument token: {spot_candidates[0]['instrument_token']}")
        else:
            print("❌ NIFTY 50 spot not found")

        # Look for NIFTY futures
        print("\n🔍 Looking for NIFTY futures...")
        futures_candidates = []
        for inst in nfo_instruments:  # Only look in NFO instruments
            if (inst.get('name', '') == 'NIFTY' and
                inst.get('instrument_type') == 'FUT'):
                futures_candidates.append(inst)

        if futures_candidates:
            print(f"Found {len(futures_candidates)} NIFTY futures")
            # Sort by expiry and show nearest
            futures_candidates.sort(key=lambda x: x.get('expiry', '9999-12-31'))
            nearest = futures_candidates[0]
            print(f"Nearest expiry: {nearest.get('tradingsymbol')} (token: {nearest.get('instrument_token')}, expiry: {nearest.get('expiry')})")
        else:
            print("❌ No NIFTY futures found")

        # Look for NIFTY options - find all available expiries and strikes
        print("\n🔍 Looking for NIFTY options...")

        # Get all NIFTY option expiries
        option_expiries = set()
        option_strikes = set()

        for inst in nfo_instruments:
            if inst.get('name', '') == 'NIFTY' and inst.get('instrument_type') in ['CE', 'PE']:
                if inst.get('expiry'):
                    option_expiries.add(inst.get('expiry'))
                if inst.get('strike'):
                    option_strikes.add(inst.get('strike'))

        print(f"Available option expiries: {sorted(option_expiries)}")
        print(f"Strike range: {min(option_strikes) if option_strikes else 'None'} - {max(option_strikes) if option_strikes else 'None'}")

        # Get actual current NIFTY price to calculate ATM
        try:
            spot_quote = kite.quote(instrument_token=256265)
            if spot_quote and '256265' in spot_quote:
                current_price = float(spot_quote['256265']['last_price'])
                print(f"Current NIFTY 50 price: ₹{current_price:.2f}")
                atm_strike = round(current_price / 50) * 50
                print(f"Calculated ATM strike: ₹{atm_strike}")
            else:
                atm_strike = 22100  # Fallback
                print("Could not get current price, using fallback ATM strike: 22100")
        except Exception as e:
            atm_strike = 22100  # Fallback
            print(f"Error getting current price: {e}, using fallback ATM strike: 22100")

        print(f"Looking for ATM options with strike: {atm_strike}")

        call_candidates = []
        put_candidates = []

        for inst in nfo_instruments:
            if (inst.get('name', '') == 'NIFTY' and
                inst.get('strike') == atm_strike):

                if inst.get('instrument_type') == 'CE':
                    call_candidates.append(inst)
                elif inst.get('instrument_type') == 'PE':
                    put_candidates.append(inst)

        print(f"ATM Call options (strike {atm_strike}): {len(call_candidates)}")
        print(f"ATM Put options (strike {atm_strike}): {len(put_candidates)}")

        if call_candidates:
            call_candidates.sort(key=lambda x: x.get('expiry', '9999-12-31'))
            nearest_call = call_candidates[0]
            print(f"Nearest ATM Call: {nearest_call.get('tradingsymbol')} (token: {nearest_call.get('instrument_token')}, expiry: {nearest_call.get('expiry')})")

        if put_candidates:
            put_candidates.sort(key=lambda x: x.get('expiry', '9999-12-31'))
            nearest_put = put_candidates[0]
            print(f"Nearest ATM Put: {nearest_put.get('tradingsymbol')} (token: {nearest_put.get('instrument_token')}, expiry: {nearest_put.get('expiry')})")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instruments()

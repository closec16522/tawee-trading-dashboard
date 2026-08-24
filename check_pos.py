import MetaTrader5 as mt5
if not mt5.initialize():
    print("MT5 Init Failed")
else:
    pos = mt5.positions_get()
    if pos is None:
        print("No positions or error")
    else:
        print(f"Total positions: {len(pos)}")
        for p in pos:
            print(f"{p.ticket}: {p.symbol} {p.type} {p.volume} @ {p.price_open}")
    mt5.shutdown()

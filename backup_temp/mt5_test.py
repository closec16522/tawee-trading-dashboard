import MetaTrader5 as mt5
path = r"C:\Program Files\VT Markets (Pty) MT5 Terminal\terminal64.exe"
print("Init with path:", mt5.initialize(path=path))
if not mt5.initialize(path=path):
    print("Error:", mt5.last_error())
mt5.shutdown()

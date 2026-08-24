import re

file_path = "mt5_backend/agent_orchestrator.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_logic = """        else:
            result = mt5.order_send(request)
            if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result = mt5.order_send(request)"""

new_logic = """        else:
            result = mt5.order_send(request)
            if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result = mt5.order_send(request)
                if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    result = mt5.order_send(request)"""

code = code.replace(old_logic, new_logic)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched type_filling logic in agent_orchestrator.py")

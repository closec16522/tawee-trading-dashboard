import re

path = 'mt5_backend/mt5_gateway.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''class TradingSettingsUpdate(BaseModel):
    allowed_grades: list
    gemini_api_key: str = ""'''

replacement1 = '''class TradingSettingsUpdate(BaseModel):
    allowed_grades: list
    gemini_api_key: str = ""
    co_pilot_mode: bool = False'''

target2 = '''    trading_config = {
        "allowed_grades": settings.allowed_grades,
        "gemini_api_key": settings.gemini_api_key,
        "telegram_token": settings.telegram_token,
        "telegram_chat_id": settings.telegram_chat_id,
        "telegram_chat_id_longterm": settings.telegram_chat_id_longterm
    }'''

replacement2 = '''    trading_config = {
        "allowed_grades": settings.allowed_grades,
        "gemini_api_key": settings.gemini_api_key,
        "telegram_token": settings.telegram_token,
        "telegram_chat_id": settings.telegram_chat_id,
        "telegram_chat_id_longterm": settings.telegram_chat_id_longterm,
        "co_pilot_mode": settings.co_pilot_mode
    }'''

content = content.replace(target1, replacement1)
content = content.replace(target2, replacement2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Gateway Copilot settings patched!")
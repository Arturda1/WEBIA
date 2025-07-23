import asyncio
import json
import os
from ozon_integration.telegram_bot import send_confirmation

PENDING_PATH = os.path.join(os.path.dirname(__file__), "ozon_integration", "pending_ops.json")

def is_confirmed(message_id):
    with open(PENDING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(message_id, {}).get("confirmed") == "yes"

def change_price_if_confirmed():
    msg_id = "ozon_price_001"
    text = "Изменить цену товара X до 999₽?"

    asyncio.run(send_confirmation(msg_id, text))

    # тут может быть пауза, проверка через кнопку или другой поток
    import time
    for _ in range(30):
        time.sleep(1)
        if is_confirmed(msg_id):
            print("✅ Цена подтверждена, отправляем в Ozon API")
            return
    print("⛔ Не подтверждено")

import os
import pandas as pd
from datetime import datetime

log_path = os.path.join("data", "operations_log.xlsx")


def register_operation_and_update_stock(form_data):
    """
    Регистрирует операцию и обновляет лог
    """
    row = {
        "Дата": datetime.today().strftime("%Y-%m-%d"),
        "Сотрудник": form_data.get("employee", ""),
        "Операция": form_data.get("operation", ""),
        "Объект": form_data.get("item", ""),
        "Кол-во": int(form_data.get("quantity", 0))
    }

    if not row["Сотрудник"] or not row["Операция"] or not row["Объект"]:
        raise ValueError("Не заполнены все обязательные поля")

    # Чтение существующего лога
    if os.path.exists(log_path):
        try:
            df = pd.read_excel(log_path)
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения operations_log.xlsx: {str(e)}")
    else:
        df = pd.DataFrame(columns=row.keys())

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Сохранение
    try:
        df.to_excel(log_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка сохранения operations_log.xlsx: {str(e)}")

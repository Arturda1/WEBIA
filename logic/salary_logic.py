import pandas as pd
import os
from datetime import datetime
from logic.material_usage import use_materials_for_product
from logic.products_logic import add_product_stock

RATES_FILE = "data/operation_rates.xlsx"
LOG_FILE = "logs/operations_log.xlsx"

def load_rates():
    if not os.path.exists(RATES_FILE):
        print("❌ Файл operation_rates.xlsx не найден.")
        return pd.DataFrame(columns=["Название", "Категория", "Ставка (₽)"])
    return pd.read_excel(RATES_FILE)

def log_operation(date, employee, operation, product, qty, rate, total):
    columns = ["Дата", "Сотрудник", "Операция", "Изделие", "Кол-во", "Ставка", "Сумма"]
    new_row = pd.DataFrame([[date, employee, operation, product, qty, rate, total]], columns=columns)
    os.makedirs("logs", exist_ok=True)

    if os.path.exists(LOG_FILE):
        log_df = pd.read_excel(LOG_FILE)
        log_df = pd.concat([log_df, new_row], ignore_index=True)
    else:
        log_df = new_row

    log_df.to_excel(LOG_FILE, index=False)

def register_operation(employee, operation, qty):
    if qty <= 0:
        print("⚠️ Кол-во должно быть больше 0.")
        return

    rates = load_rates()
    rate_row = rates[rates["Название"] == operation]

    if rate_row.empty:
        print(f"❌ Не найдена ставка для операции '{operation}'")
        return

    rate = rate_row.iloc[0]["Ставка (₽)"]
    total = round(rate * qty, 2)
    date = datetime.now()  # ← сохраняем как datetime, не строку

    product = operation

    try:
        use_materials_for_product(product, qty)
        add_product_stock(product, qty)
    except ValueError as e:
        print(f"⚠️ {e}")
        return
    except Exception as e:
        print(f"💥 Внутренняя ошибка: {e}")
        return

    log_operation(date, employee, operation, product, qty, rate, total)
    print(f"✅ {employee} → {operation} × {qty} → {total} ₽ записано в лог.")


def operation_input_menu():
    print("\\n📋 Ввод выполненных операций")

    employee = input("Сотрудник: ").strip()
    if not employee:
        print("❌ Сотрудник не указан.")
        return

    rates = load_rates()
    if rates.empty:
        print("❌ Список операций пуст.")
        return

    operations = rates["Название"].tolist()

    while True:
        print("\\n🔁 Выберите операцию (или '0' — выйти в меню):")
        for idx, op in enumerate(operations, 1):
            print(f"  {idx}. {op}")

        choice = input("Номер операции: ").strip()
        if choice == "0":
            print("↩️ Возврат в главное меню.")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(operations)):
            print(f"❗ Введите число от 1 до {len(operations)}.")
            continue

        operation = operations[int(choice) - 1]

        qty_input = input("Кол-во выполнено (или 0 — отменить): ").strip()
        if qty_input == "0":
            print("⏩ Операция пропущена.")
            continue
        try:
            qty = int(qty_input)
        except ValueError:
            print("❌ Некорректное число.")
            continue

        register_operation(employee, operation, qty)


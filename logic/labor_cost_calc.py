from logic.material_cost_calc import trace_all_stages
import pandas as pd
from collections import defaultdict

PRODUCT_RECIPES_FILE = "data/product_recipes.xlsx"
OPERATION_RATES_FILE = "data/operation_rates.xlsx"


def calculate_labor_cost():
    try:
        product_df = pd.read_excel(PRODUCT_RECIPES_FILE)
        rates_df = pd.read_excel(OPERATION_RATES_FILE).drop_duplicates(subset=["Название"])
    except Exception as e:
        print(f"❌ Ошибка загрузки файлов: {e}")
        return

    products = sorted(product_df["Название"].unique().tolist())

    print("\n📦 Выберите изделие:")
    for i, name in enumerate(products, 1):
        print(f"{i}. {name}")
    try:
        choice = int(input("Введите номер: ")) - 1
        if choice < 0 or choice >= len(products):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор.")
        return

    selected = products[choice]
    stages = trace_all_stages(selected, product_df)

    print(f"\n🧾 Стоимость работ для: {selected}")
    print(f"{'Операция':40} {'Кол-во':>8} {'Ставка':>10} {'Сумма':>10}")
    print("-" * 70)

    total = 0
    for stage, qty in stages.items():
        row = rates_df[rates_df["Название"] == stage]
        if row.empty:
            continue
        rate = float(row.iloc[0]["Ставка (₽)"])
        cost = round(rate * qty, 2)
        total += cost
        print(f"{stage:40} {qty:8.2f} {rate:10.2f} {cost:10.2f}")

    print("-" * 70)
    print(f"{'ИТОГО:':>60} {total:10.2f} ₽")

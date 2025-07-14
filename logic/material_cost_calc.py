import pandas as pd
from collections import defaultdict

PRODUCT_RECIPES_FILE = "data/product_recipes.xlsx"
SEMI_RECIPES_FILE = "data/semi_products_recipes.xlsx"
MATERIALS_FILE = "data/materials.xlsx"

def load_all():
    return (
        pd.read_excel(PRODUCT_RECIPES_FILE),
        pd.read_excel(SEMI_RECIPES_FILE),
        pd.read_excel(MATERIALS_FILE),
    )

def get_price(materials_df, name):
    row = materials_df[materials_df["Название"].str.strip() == name.strip()]
    if row.empty:
        return 0
    return float(row.iloc[0].get("Средняя цена (₽/ед.)", 0) or 0)

def trace_all_stages(product_name, recipes_df, visited=None, multiplier=1):
    if visited is None:
        visited = defaultdict(float)

    visited[product_name] += multiplier

    sub_recipes = recipes_df[recipes_df["Название"].str.strip() == product_name.strip()]
    if sub_recipes.empty:
        return visited

    for _, row in sub_recipes.iterrows():
        component = str(row["Из чего состоит"]).strip()
        qty = float(row["Кол-во"])
        trace_all_stages(component, recipes_df, visited, multiplier * qty)

    return visited

def collect_materials_for_stages(stages: dict, semi_df: pd.DataFrame):
    total_materials = defaultdict(float)
    for stage, stage_qty in stages.items():
        stage_rows = semi_df[semi_df["Название"].str.strip() == stage.strip()]
        for _, row in stage_rows.iterrows():
            material = str(row["Материал"]).strip()
            qty = float(row["Кол-во"]) * stage_qty
            total_materials[material] += qty
    return total_materials

def calculate_cost():
    import pandas as pd

    # Загружаем данные
    product_df, semi_df, materials_df = load_all()
    products = sorted(set(product_df["Название"].tolist()))

    # Выбор изделия
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

    selected_product = products[choice]

    # Строим дерево стадий и собираем нужные материалы
    stages = trace_all_stages(selected_product, product_df)
    materials_used = collect_materials_for_stages(stages, semi_df)

    # Сортируем materials_df по столбцу "Порядок" (гарантированный порядок из Excel)
    materials_df = materials_df.sort_values("Порядок", ignore_index=True)

    # Вывод таблицы
    print(f"\n🧾 Себестоимость изделия: {selected_product}")
    print(f"{'Материал':40} {'Кол-во':>10} {'Цена':>10} {'Сумма':>10}")
    print("-" * 70)

    total = 0
    for _, row in materials_df.iterrows():
        name = str(row["Название"]).strip()
        if name not in materials_used:
            continue

        qty = round(materials_used[name], 4)
        price = round(get_price(materials_df, name), 2)
        cost = round(qty * price, 2)
        total += cost
        print(f"{name:40} {qty:10.4f} {price:10.2f} {cost:10.2f}")

    print("-" * 70)
    print(f"{'ИТОГО:':>62} {total:10.2f} ₽")

import pandas as pd
import os

PRODUCTS_FILE = "data/products_list.xlsx"
RECIPES_FILE = "data/product_recipes.xlsx"


def load_products():
    return pd.read_excel(PRODUCTS_FILE)


def save_products(df):
    df.to_excel(PRODUCTS_FILE, index=False)


def load_recipes():
    return pd.read_excel(RECIPES_FILE)


def update_stage():
    df_products = load_products()
    df_recipes = load_recipes()

    # Получим список всех изделий, которые встречаются в "Название"
    stage_names = df_products[df_products["Категория"] == "Полуфабрикат"]["Название"].tolist()

    print("\nВыберите полуфабрикат для обновления стадии:")
    for i, name in enumerate(stage_names, 1):
        print(f"{i}. {name}")

    try:
        index = int(input("Введите номер: ")) - 1
        if index < 0 or index >= len(stage_names):
            raise ValueError
    except ValueError:
        print("Неверный выбор.")
        return

    target = stage_names[index]

    # Определяем из чего он состоит (берем первый компонент как "источник")
    recipe = df_recipes[df_recipes["Название"] == target]
    if recipe.empty:
        print("⛔ Не найдена информация о рецепте для этого полуфабриката.")
        return

    source = recipe.iloc[0]["Из чего состоит"]

    try:
        qty = int(input(f"Сколько штук перевести из '{source}' в '{target}': "))
    except ValueError:
        print("Неверное количество.")
        return

    if source not in df_products["Название"].values:
        print(f"⛔ '{source}' не найден на складе.")
        return

    source_index = df_products[df_products["Название"] == source].index[0]
    available = df_products.at[source_index, "Остаток"]

    if available < qty:
        print(f"⛔ Недостаточно остатков. Доступно: {available}")
        return

    df_products.at[source_index, "Остаток"] -= qty

    if target in df_products["Название"].values:
        target_index = df_products[df_products["Название"] == target].index[0]
        df_products.at[target_index, "Остаток"] += qty
    else:
        new_row = {
            "Категория": "Полуфабрикат",
            "Название": target,
            "Ед. изм.": "шт",
            "Остаток": qty
        }
        df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)

    save_products(df_products)
    print(f"✅ Переведено {qty} шт из '{source}' в '{target}' успешно сохранено.")
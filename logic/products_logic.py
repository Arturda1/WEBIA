import pandas as pd
import os
from logic.material_usage import use_materials_for_product

PRODUCTS_FILE = "data/products_list.xlsx"
RECIPES_FILE = "data/product_recipes.xlsx"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        print("\n❗️Файл products_list.xlsx не найден!")
        return pd.DataFrame(columns=["Категория", "Название", "Ед. изм.", "Остаток"])
    return pd.read_excel(PRODUCTS_FILE)

def save_products(df):
    df.to_excel(PRODUCTS_FILE, index=False)

def load_recipes():
    return pd.read_excel(RECIPES_FILE)

def produce():
    df_products = load_products()
    df_recipes = load_recipes()

    while True:
        print("\nЧто вы хотите произвести:")
        print("1. Готовое изделие")
        print("2. Полуфабрикат")
        print("м. Вернуться в меню")
        type_choice = input("Введите номер: ").strip()

        if type_choice == "м":
            return
        elif type_choice == "1":
            products = df_products[df_products["Категория"] == "Готовая продукция"]["Название"].tolist()
            category = "Готовая продукция"
        elif type_choice == "2":
            products = df_products[df_products["Категория"] == "Полуфабрикат"]["Название"].tolist()
            category = "Полуфабрикат"
        else:
            print("Неверный выбор. Попробуйте снова.")
            continue

        while True:
            print("\nВыберите изделие для производства:")
            for i, name in enumerate(products, 1):
                print(f"{i}. {name}")
            print("м. Вернуться назад")
            choice = input("Введите номер: ").strip()

            if choice == "м":
                break

            if not choice.isdigit() or not (1 <= int(choice) <= len(products)):
                print("Некорректный ввод. Попробуйте снова.")
                continue

            product_name = products[int(choice) - 1]
            break

        if choice == "м":
            continue

        qty_input = input(f"Сколько штук '{product_name}' произвести: ").strip()
        if qty_input.lower() == "м":
            continue
        if not qty_input.isdigit():
            print("Некорректный ввод количества.")
            continue
        qty = int(qty_input)

        recipe = df_recipes[df_recipes["Название"] == product_name]

        if recipe.empty:
            # Нет рецепта — обычная заливка, списываем материалы
            if product_name in df_products["Название"].values:
                idx = df_products[df_products["Название"] == product_name].index[0]
                df_products.at[idx, "Остаток"] += qty
            else:
                new_row = {
                    "Категория": category,
                    "Название": product_name,
                    "Ед. изм.": "шт",
                    "Остаток": qty
                }
                df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)

            use_materials_for_product(product_name, qty)
            save_products(df_products)
            print(f"\n✅ Успешно произведено {qty} шт '{product_name}'. Остатки обновлены.")
            return

        # Проверка: стадийный переход (один компонент из рецепта)
        if len(recipe) == 1:
            source = recipe.iloc[0]["Из чего состоит"]
            used_qty = int(recipe.iloc[0]["Кол-во"]) * qty

            if source not in df_products["Название"].values:
                print(f"\n❗️Компонент '{source}' не найден.")
                return

            source_idx = df_products[df_products["Название"] == source].index[0]
            if df_products.at[source_idx, "Остаток"] < used_qty:
                print(f"\n❗️Недостаточно остатков: '{source}' — нужно {used_qty}, доступно {df_products.at[source_idx, 'Остаток']}")
                return

            # списываем исходную стадию
            df_products.at[source_idx, "Остаток"] -= used_qty
            print(f"✅ Переведено {used_qty} шт из '{source}' в '{product_name}'")
        else:
            # сложное изделие — списываем полуфабрикаты
            df_used = []
            for _, row in recipe.iterrows():
                used_name = row["Из чего состоит"]
                used_qty = int(row["Кол-во"]) * qty

                if used_name in df_products["Название"].values:
                    idx = df_products[df_products["Название"] == used_name].index[0]
                    if df_products.at[idx, "Остаток"] < used_qty:
                        print(f"\n❗️Недостаточно остатков: '{used_name}' — нужно {used_qty}, доступно {df_products.at[idx, 'Остаток']}")
                        return
                    df_products.at[idx, "Остаток"] -= used_qty
                    df_used.append((used_name, used_qty))
                else:
                    print(f"\n❗️Компонент '{used_name}' не найден.")
                    return

        # увеличиваем остаток целевого изделия
        if product_name in df_products["Название"].values:
            idx = df_products[df_products["Название"] == product_name].index[0]
            df_products.at[idx, "Остаток"] += qty
        else:
            new_row = {
                "Категория": category,
                "Название": product_name,
                "Ед. изм.": "шт",
                "Остаток": qty
            }
            df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)

        save_products(df_products)
        print(f"\n✅ Успешно произведено {qty} шт '{product_name}'. Остатки обновлены.")
        return

def show_products_stock():
    df = load_products()
    while True:
        print("\nЧто хотите посмотреть:")
        print("1. Готовая продукция")
        print("2. Полуфабрикаты")
        print("м. Вернуться в меню")
        choice = input("Введите номер: ").strip()

        if choice == "м":
            return
        elif choice == "1":
            category = "Готовая продукция"
        elif choice == "2":
            category = "Полуфабрикат"
        else:
            print("Неверный выбор.")
            continue

        selected = df[df["Категория"] == category]
        if selected.empty:
            print("\n📭 Нет записей в этой категории.")
        else:
            print(f"\n📦 Остатки ({category}):")
            for i, row in selected.iterrows():
                print(f"– {row['Название']}: {row['Остаток']} {row['Ед. изм.']}")
        return

def add_product_stock(product_name: str, qty: int):
    df_products = load_products()

    if product_name in df_products["Название"].values:
        idx = df_products[df_products["Название"] == product_name].index[0]
        df_products.at[idx, "Остаток"] += qty
    else:
        new_row = {
            "Категория": "Готовая продукция",
            "Название": product_name,
            "Ед. изм.": "шт",
            "Остаток": qty
        }
        df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)

    save_products(df_products)

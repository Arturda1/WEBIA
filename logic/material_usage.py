import pandas as pd
import os

MATERIALS_FILE = "data/materials.xlsx"
PRODUCT_RECIPES_FILE = "data/product_recipes.xlsx"
SEMI_RECIPES_FILE = "data/semi_products_recipes.xlsx"


def load_materials():
    if not os.path.exists(MATERIALS_FILE):
        print("\n❌ Файл materials.xlsx не найден!")
        return pd.DataFrame(columns=["Название", "Ед. изм.", "Остаток"])
    return pd.read_excel(MATERIALS_FILE)


def save_materials(df):
    df.to_excel(MATERIALS_FILE, index=False)


def load_all_recipes():
    return pd.read_excel(PRODUCT_RECIPES_FILE), pd.read_excel(SEMI_RECIPES_FILE)


def get_flat_materials(product_name: str, qty: int, product_recipes: pd.DataFrame, semi_recipes: pd.DataFrame, visited=None):
    if visited is None:
        visited = set()

    if product_name in visited:
        return {}
    visited.add(product_name)

    result = {}
    recipe_rows = product_recipes[product_recipes["Название"] == product_name]

    if recipe_rows.empty:
        semi_rows = semi_recipes[semi_recipes["Название"] == product_name]
        if semi_rows.empty:
            result[product_name] = result.get(product_name, 0) + qty
            return result
        for _, row in semi_rows.iterrows():
            material = row["Материал"]
            material_qty = row["Кол-во"] * qty
            result[material] = result.get(material, 0) + material_qty
        return result

    for _, row in recipe_rows.iterrows():
        component = row["Из чего состоит"]
        component_qty = row["Кол-во"] * qty
        sub_result = get_flat_materials(component, component_qty, product_recipes, semi_recipes, visited)
        for mat, q in sub_result.items():
            result[mat] = result.get(mat, 0) + q

    return result


def use_materials_for_product(product_name: str, qty: int):
    df_materials = load_materials()
    product_recipes, semi_recipes = load_all_recipes()

    total_materials = get_flat_materials(product_name, qty, product_recipes, semi_recipes)

    for material, total_needed in total_materials.items():
        if material not in df_materials["Название"].values:
            print(f"\n❌ Материал '{material}' не найден на складе!")
            return

        idx = df_materials[df_materials["Название"] == material].index[0]
        current_stock = df_materials.at[idx, "Остаток"]

        if current_stock < total_needed:
            print(f"\n❌ Недостаточно '{material}': нужно {total_needed}, доступно {current_stock}")
            return

    for material, total_needed in total_materials.items():
        idx = df_materials[df_materials["Название"] == material].index[0]
        df_materials.at[idx, "Остаток"] = round(df_materials.at[idx, "Остаток"] - total_needed, 4)
        print(f"✅ Списано {total_needed} {df_materials.at[idx, 'Ед. изм.']} '{material}'")

    save_materials(df_materials)
    print("\n📦 Остатки материалов обновлены.")

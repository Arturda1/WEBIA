import os
import pandas as pd

materials_path = os.path.join("data", "materials.xlsx")


def calculate_material_cost(recipe_rows: list) -> float:
    """
    Считает суммарную стоимость материалов по рецепту (list of dict)
    """
    if not os.path.exists(materials_path):
        return 0.0
    try:
        df = pd.read_excel(materials_path)
    except:
        return 0.0

    cost = 0.0
    for row in recipe_rows:
        name = row.get("Материал")
        qty = row.get("Кол-во")
        if pd.isna(name) or pd.isna(qty):
            continue

        match = df[df["Материал"] == name]
        if match.empty:
            continue

        price = match["Средняя цена"].values[0]
        try:
            cost += float(price) * float(qty)
        except:
            continue

    return round(cost, 2)

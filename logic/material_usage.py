import os
import pandas as pd

semi_recipes_path = os.path.join("data", "semi_products_recipes.xlsx")


def calculate_materials_for_semi_product(name: str, count: int):
    if not os.path.exists(semi_recipes_path):
        return []
    try:
        df = pd.read_excel(semi_recipes_path)
    except:
        return []

    df = df[df["Название"] == name]
    if df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        material = row.get("Материал", "")
        qty = row.get("Кол-во", 0)
        unit = row.get("Ед. изм.", "")
        if pd.notna(material) and pd.notna(qty):
            try:
                results.append({
                    "Материал": material,
                    "Кол-во": float(qty) * count,
                    "Ед. изм.": unit
                })
            except:
                continue
    return results

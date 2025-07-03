import os
import pandas as pd

products_path = os.path.join("data", "products_list.xlsx")
recipes_path = os.path.join("data", "product_recipes.xlsx")
semi_recipes_path = os.path.join("data", "semi_products_recipes.xlsx")


def get_available_products():
    if not os.path.exists(products_path):
        return []
    try:
        df = pd.read_excel(products_path)
        return df["Наименование"].dropna().unique().tolist()
    except:
        return []


def get_materials_for_product(product_name: str):
    if not os.path.exists(recipes_path):
        return []
    try:
        df = pd.read_excel(recipes_path)
        return df[df["Изделие"] == product_name].to_dict(orient="records")
    except:
        return []


def get_materials_for_semi_product(name: str):
    if not os.path.exists(semi_recipes_path):
        return []
    try:
        df = pd.read_excel(semi_recipes_path)
        return df[df["Название"] == name].to_dict(orient="records")
    except:
        return []

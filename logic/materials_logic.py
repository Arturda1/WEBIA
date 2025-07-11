import os
import pandas as pd
from datetime import datetime

materials_path = os.path.join("data", "materials.xlsx")
purchases_path = os.path.join("data", "purchases.xlsx")


def add_purchase(form_data):
    """
    Добавляет новую поставку в purchases.xlsx
    """
    if not os.path.exists(purchases_path):
        df = pd.DataFrame(columns=form_data.keys())
    else:
        try:
            df = pd.read_excel(purchases_path)
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения purchases.xlsx: {str(e)}")

    row = {key: form_data.get(key)[0] if isinstance(form_data.get(key), list) else form_data.get(key) for key in form_data}
    row["Дата"] = datetime.today().strftime("%Y-%m-%d")

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    try:
        df.to_excel(purchases_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка сохранения purchases.xlsx: {str(e)}")


def update_average_prices():
    """
    Обновляет среднюю цену в materials.xlsx на основе последних 3 поставок из purchases.xlsx
    """
    if not os.path.exists(purchases_path) or not os.path.exists(materials_path):
        return

    try:
        purchases = pd.read_excel(purchases_path)
        materials = pd.read_excel(materials_path)
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения Excel-файлов: {str(e)}")

    if purchases.empty or materials.empty:
        return

    purchases["Цена (за упаковку)"] = pd.to_numeric(purchases["Цена (за упаковку)"], errors="coerce")
    purchases = purchases.dropna(subset=["Цена (за упаковку)"])

    avg_prices = (
        purchases.groupby("Материал")
        .apply(lambda x: x.sort_values("Дата", ascending=False).head(3)["Цена (за упаковку)"].mean())
        .reset_index()
        .rename(columns={0: "Средняя цена"})
    )

    materials = materials.merge(avg_prices, on="Материал", how="left")
    materials["Средняя цена"] = materials["Средняя цена_y"].combine_first(materials.get("Средняя цена_x"))
    materials = materials.drop(columns=[col for col in materials.columns if col.endswith("_x") or col.endswith("_y")])

    try:
        materials.to_excel(materials_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка сохранения materials.xlsx: {str(e)}")


def load_materials():
    """
    Загружает список материалов из materials.xlsx
    """
    if not os.path.exists(materials_path):
        return []

    try:
        df = pd.read_excel(materials_path)
        return df["Материал"].dropna().unique().tolist()
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки материалов: {str(e)}")

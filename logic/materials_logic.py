import os
import pandas as pd
from datetime import datetime

PRODUCT_RECIPES_FILE = "data/product_recipes.xlsx"
SEMI_RECIPES_FILE = "data/semi_products_recipes.xlsx"
MATERIALS_FILE = "data/materials.xlsx"
SNAPSHOT_FOLDER = "db/snapshots"



def load_materials():
    if not os.path.exists(MATERIALS_FILE):
        print("\n❗️Файл materials.xlsx не найден!")
        return pd.DataFrame(columns=["Название", "Ед. изм.", "Остаток"])
    return pd.read_excel(MATERIALS_FILE)

def save_materials(df):
    df.to_excel(MATERIALS_FILE, index=False)

def show_stock(df):
    print("\n📦 Остатки материалов:\n")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['Название']} ({row['Ед. изм.']}): {row['Остаток']}")

def save_snapshot(df):
    if not os.path.exists(SNAPSHOT_FOLDER):
        os.makedirs(SNAPSHOT_FOLDER)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SNAPSHOT_FOLDER, f"materials_snapshot_{now}.xlsx")
    df.to_excel(path, index=False)
    print(f"\n✅ Снапшот сохранён: {path}")

def add_material(df):
    diffs = []

    print("\nВведите изменения остатков (например: +10, -5), оставьте пустым, чтобы пропустить.")

    for i, row in df.iterrows():
        val = input(f"{i+1}. {row['Название']} ({row['Ед. изм.']}): ").strip()
        if val == "":
            diffs.append(0)
            continue
        try:
            diffs.append(float(val))
        except:
            diffs.append(0)

    while True:
        print("\n——— ИТОГ ———")
        for i, row in df.iterrows():
            delta = diffs[i]
            final = row["Остаток"] + delta
            print(f"{i+1}. {row['Название']}: {final} ({'+' if delta >= 0 else ''}{delta})")

        cmd = input("\n[1] Подтвердить изменения\n[2] Исправить значение\n[0] Выйти в меню\nВыберите команду: ").strip()

        if cmd == "1":
            for i in range(len(df)):
                df.at[i, "Остаток"] += diffs[i]
            save_materials(df)
            print("✅ Изменения сохранены в файл.")
            break
        elif cmd == "2":
            idx = int(input("Введите номер для исправления: ")) - 1
            val = input("Новое значение: ")
            try:
                diffs[idx] = float(val)
            except:
                print("Неверный ввод.")
        elif cmd == "0":
            print("↩️ Возврат в главное меню.")
            return
        
def get_price_from_materials_file(material_name):
    df = load_materials()
    row = df[df["Название"].str.strip() == material_name.strip()]
    if row.empty or pd.isna(row.iloc[0].get("Средняя цена (₽/ед.)", None)):
        return 0
    return float(row.iloc[0]["Средняя цена (₽/ед.)"])

def update_average_prices():
    purchases_path = "data/purchases.xlsx"

    try:
        materials_df = load_materials()
        purchases_df = pd.read_excel(purchases_path)
    except Exception as e:
        print(f"❌ Ошибка загрузки файлов: {e}")
        return

    purchases_df["Материал"] = purchases_df["Материал"].str.strip()
    materials_df["Название"] = materials_df["Название"].str.strip()

    avg_prices = []
    for material in materials_df["Название"]:
        filtered = purchases_df[purchases_df["Материал"] == material]
        if filtered.empty:
            avg_prices.append(None)
            continue

        recent = filtered.sort_values("Дата", ascending=False).head(3)
        prices_per_unit = recent["Цена (за упаковку)"] / recent["Кол-во в упаковке"]
        avg_price = round(prices_per_unit.mean(), 2)
        avg_prices.append(avg_price)

    materials_df["Средняя цена (₽/ед.)"] = avg_prices
    save_materials(materials_df)
    print("✅ Средние цены обновлены в materials.xlsx")


from logic.materials_logic import load_materials, add_material, show_stock, save_snapshot
from logic.products_logic import show_products_stock
from logic.material_cost_calc import calculate_cost
from logic.salary_logic import operation_input_menu
from logic.labor_cost_calc import calculate_labor_cost


def main_menu():
    while True:
        print("""
📋 Главное меню:
1. Изменить остатки материалов
2. Посмотреть остатки материалов
3. Сохранить снапшот остатков
4. Посмотреть остатки готовых изделий/полуфабрикатов
5. Обновить средние цены из purchases
6. Посчитать себестоимость изделия
7. Зарегистрировать операцию (для зарплаты)
8. Посчитать стоимость работ для изделия
0. Выход
""")

        choice = input("Выберите пункт меню: ").strip()
        if choice == "1":
            df = load_materials()
            add_material(df)
        elif choice == "2":
            df = load_materials()
            show_stock(df)
        elif choice == "3":
            df = load_materials()
            save_snapshot(df)
        elif choice == "4":
            show_products_stock()
        elif choice == "5":
            from logic.materials_logic import update_average_prices
            update_average_prices()
        elif choice == "6":
            calculate_cost()
        elif choice == "7":
            operation_input_menu()
        elif choice == "8":
            calculate_labor_cost()
        elif choice == "0":
            print("👋 Выход.")
            break
        else:
            print("❌ Неверный ввод. Повторите.")
        

if __name__ == "__main__":
    pass  # отключено при деплое на Railway

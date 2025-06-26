import tkinter as tk
from tkinter import messagebox
from logic.materials_logic import load_materials, add_material, show_stock, save_snapshot
from logic.products_logic import produce, show_products_stock
from logic.stages_logic import update_stage
from logic.material_cost_calc import calculate_cost
from logic.salary_logic import operation_input_menu

root = tk.Tk()
root.title("Система управления производством")
root.geometry("600x500")
root.configure(bg="#f7f7f7")

# Цвета и иконки для кнопок
buttons = [
    ("📥 Изменить остатки", add_material, "#d1e7dd"),
    ("📦 Остатки материалов", show_stock, "#e2e3e5"),
    ("🗂 Сохранить снапшот", save_snapshot, "#dee2e6"),
    ("🏷 Остатки изделий", show_products_stock, "#f8d7da"),
    ("🏭 Производство", produce, "#dbe5f1"),
    ("🔄 Обновить стадию", update_stage, "#fef3cd"),
    ("💰 Себестоимость", calculate_cost, "#ffe5b4"),
    ("👷 Зарплата/операции", operation_input_menu, "#f0d1d1")
]

# Визуальные настройки
frame = tk.Frame(root, bg="#f7f7f7")
frame.pack(pady=20)

for i in range(0, len(buttons), 2):
    row = tk.Frame(frame, bg="#f7f7f7")
    row.pack(pady=10)
    for j in range(2):
        if i + j >= len(buttons):
            break
        text, command, color = buttons[i + j]
        def wrap(cmd=command):
            try:
                if cmd.__code__.co_argcount > 0:
                    df = load_materials()
                    cmd(df)
                else:
                    cmd()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        btn = tk.Button(row, text=text, width=20, height=4, bg=color, command=wrap, relief="groove")
        btn.pack(side="left", padx=10)

# Кнопка выхода
exit_btn = tk.Button(root, text="❌ Выйти", width=20, height=2, bg="#cccccc", command=root.quit)
exit_btn.pack(pady=20)

root.mainloop()

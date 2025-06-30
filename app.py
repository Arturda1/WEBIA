import os
from dotenv import load_dotenv
load_dotenv()

import zipfile
import io
from flask import send_file


from flask import Flask, render_template, request, redirect, session, url_for
import os
import pandas as pd

app = Flask(__name__, template_folder="templates")
app.secret_key = "очень_секретная_строка"


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    import json
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(BASE_DIR, "data", "users.json")

    if request.method == "POST":
        login_input = request.form["username"]
        password_input = request.form["password"]

        try:
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            return "Ошибка загрузки users.json: " + str(e)

        for u in users:
            if u["login"] == login_input and u["password"] == password_input:
                session["user"] = login_input
                session["employee"] = u["name"]
                return redirect(url_for("dashboard"))

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


# --- Login page ---
@app.route("/", methods=["GET", "POST"])
def login():
    import json
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(BASE_DIR, "data", "users.json")

    print("Зашли на /")

    if request.method == "POST":
        login_input = request.form["username"]
        password_input = request.form["password"]

        try:
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            return f"<p>❌ Ошибка загрузки users.json: {e}</p>"

        for u in users:
            if u["login"] == login_input and u["password"] == password_input:
                session["user"] = login_input
                session["employee"] = u["name"]
                return redirect(url_for("dashboard"))

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")






# --- Dashboard ---
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/view-stock", methods=["GET", "POST"])
def view_stock():
    if "user" not in session:
        return redirect(url_for("login"))

    from logic.materials_logic import load_materials, save_materials
    import pandas as pd

    df = load_materials()

    if request.method == "POST":
        diffs = []
        for i in range(len(df)):
            val = request.form.get(f"m_{i}", "").strip()
            try:
                diffs.append(float(val))
            except:
                diffs.append(0)

        for i in range(len(df)):
            df.at[i, "Остаток"] += diffs[i]

        save_materials(df)
        return "<p>✅ Остатки обновлены.</p><a href='/view-stock'>↩ Вернуться</a> | <a href='/dashboard'>🏠 В меню</a>"

    html = "<h2>📦 Остатки материалов + Изменения</h2>"
    html += "<form method='post'><table border='1' cellpadding='5'>"
    html += "<tr><th>№</th><th>Название</th><th>Ед.</th><th>Текущий остаток</th><th>Изменение</th></tr>"

    for i, row in df.iterrows():
        html += f"<tr><td>{i+1}</td><td>{row['Название']}</td><td>{row['Ед. изм.']}</td>"
        html += f"<td>{row['Остаток']}</td><td><input type='text' name='m_{i}'></td></tr>"

    html += "</table><br><button type='submit'>💾 Сохранить изменения</button></form>"
    html += "<br><a href='/dashboard'>⬅ Назад</a>"
    return html


@app.route("/produce", methods=["GET", "POST"])
def produce_route():
    if "user" not in session:
        return redirect(url_for("login"))

    from logic.products_logic import produce
    import pandas as pd

    if request.method == "POST":
        product_name = request.form.get("product")
        qty = int(request.form.get("qty", 1))
        try:
            produce(product_name, qty)
            return f"<p>✅ Произведено {qty} × {product_name}</p><a href='/dashboard'>⬅ Назад</a>"
        except Exception as e:
            return f"<p>❌ Ошибка: {e}</p><a href='/dashboard'>⬅ Назад</a>"

    # Загрузка списка изделий из Excel
    df = pd.read_excel("data/product_recipes.xlsx")
    product_names = df["Название"].unique().tolist()

    options_html = "".join([f"<option value='{name}'>{name}</option>" for name in product_names])

    return f'''
        <h2>🏭 Производство</h2>
        <form method="post">
            <label>Выберите изделие:</label><br>
            <select name="product">{options_html}</select><br><br>
            <label>Количество:</label><br>
            <input name="qty" type="number" value="1"><br><br>
            <button type="submit">Произвести</button>
        </form>
        <a href="/dashboard">⬅ Назад</a>
    '''


# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/view-products")
def view_products():
    if "user" not in session:
        return redirect(url_for("login"))

    from logic.products_logic import load_products

    df = load_products()

    html = "<h2>📦 Остатки продукции:</h2><ul>"

    for category in ["Готовая продукция", "Полуфабрикат"]:
        html += f"<h3>{category}</h3><ul>"
        sub = df[df["Категория"] == category]
        for _, row in sub.iterrows():
            html += f"<li>{row['Название']} — {row['Остаток']} {row['Ед. изм.']}</li>"
        html += "</ul>"

    html += "<a href='/dashboard'>⬅ Назад</a>"
    return html

@app.route("/register-operation", methods=["GET", "POST"])
def register_operation_web():
    if "user" not in session:
        return redirect(url_for("login"))

    from logic.salary_logic import register_operation, load_rates
    import json

    # 🟢 Обработка POST (регистрация операции)
    if request.method == "POST":
        employee = request.form.get("employee")
        operation = request.form.get("operation")
        qty = int(request.form.get("qty", 1))

        print(f"📥 POST-получено: {employee}, {operation}, {qty}")  # debug
        register_operation(employee, operation, qty)

        return redirect(url_for("dashboard"))

    # 🔵 Отображение формы
    rates_df = load_rates()

    # Структурируем операции: Категория → Подкатегория → [Операции]
    structured = {}
    for _, row in rates_df.iterrows():
        cat = row.get("Категория", "Без категории")
        sub = row.get("Подкатегория", "Без подкатегории")
        name = row["Название"]
        structured.setdefault(cat, {}).setdefault(sub, []).append(name)

    data_json = json.dumps(structured, ensure_ascii=False)

    return f"""
    <h2>🧾 Регистрация операции</h2>
    <form method="post">
        <label>Сотрудник:</label><br>
        <input type="hidden" name="employee" value="{session['employee']}">
        <p><b>Сотрудник:</b> {session['employee']}</p><br>


        <label>Категория:</label><br>
        <select id="category" onchange="updateSubcategories()" required></select><br><br>

        <label>Подкатегория:</label><br>
        <select id="subcategory" onchange="updateOperations()" required></select><br><br>

        <label>Операция:</label><br>
        <select name="operation" id="operation" required></select><br><br>

        <label>Количество:</label><br>
        <input name="qty" type="number" value="1" required><br><br>

        <button type="submit">Зарегистрировать</button>
    </form>

    <a href="/dashboard">⬅ Назад</a>

    <script>
    const data = {data_json};

    function updateSubcategories() {{
        const cat = document.getElementById("category").value;
        const subs = Object.keys(data[cat] || {{}});

        const subSelect = document.getElementById("subcategory");
        subSelect.innerHTML = subs.map(s => `<option value="${{s}}">${{s}}</option>`).join('');
        updateOperations();
    }}

    function updateOperations() {{
        const cat = document.getElementById("category").value;
        const sub = document.getElementById("subcategory").value;
        const ops = (data[cat] && data[cat][sub]) || [];

        const opSelect = document.getElementById("operation");
        opSelect.innerHTML = ops.map(o => `<option value="${{o}}">${{o}}</option>`).join('');
    }}

    window.onload = () => {{
        const catSelect = document.getElementById("category");
        catSelect.innerHTML = Object.keys(data).map(c => `<option value="${{c}}">${{c}}</option>`).join('');
        updateSubcategories();
    }};
    </script>
    """



@app.route("/operations-log")
def operations_log():
    if "user" not in session:
        return redirect(url_for("login"))

    if session.get("employee") != "админ":
        return "<p>⛔ Доступ только для администратора.</p><a href='/dashboard'>⬅ Назад</a>"


    import pandas as pd
    path = "logs/operations_log.xlsx"

    if not os.path.exists(path):
        return "<p>📭 Лог операций пока пуст.</p><a href='/dashboard'>⬅ Назад</a>"

    # --- Чтение и фильтрация по дате ---
    start = request.args.get("start")
    end = request.args.get("end")
    df = pd.read_excel(path)
    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")

    if start and end:
        try:
            start_date = pd.to_datetime(start)
            end_date = pd.to_datetime(end)
            df = df[(df["Дата"] >= start_date) & (df["Дата"] <= end_date)]
        except:
            return "<p>❌ Ошибка в дате фильтра.</p><a href='/operations-log'>⬅ Назад</a>"

    # --- Формирование HTML ---
    html = '''
    <h2>🧾 Журнал операций</h2>
    <form method="get">
      <label>Фильтр по дате:</label><br>
      с <input type="date" name="start" required> по <input type="date" name="end" required>
      <button type="submit">Применить</button>
    </form><br>
    <table border='1' cellpadding='5'><tr>
    '''
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr>"

    for _, row in df.iterrows():
        html += "<tr>" + "".join([f"<td>{row[col]}</td>" for col in df.columns]) + "</tr>"

    html += "</table><br>"

    # --- Кнопка скачивания и очистка ---
    html += '''
    <a href="/download-operations-log">📥 Скачать лог (Excel)</a><br><br>
    <form action="/clear-operations-log" method="post" onsubmit="return confirm('Очистить журнал?')">
      <label>Пароль для очистки:</label><br>
      <input type="password" name="password" required><br><br>
      <button type="submit">🗑 Очистить журнал операций</button>
    </form>
    <br><a href='/dashboard'>⬅ Назад</a>
    '''

    return html


@app.route("/clear-operations-log", methods=["POST"])
def clear_operations_log():
    if "user" not in session:
        return redirect(url_for("login"))

    password = request.form.get("password")
    if password != "1488":
        return "<p>❌ Неверный пароль. Очистка отменена.</p><a href='/operations-log'>↩ Назад</a>"

    import pandas as pd
    path = "logs/operations_log.xlsx"
    columns = ["Дата", "Сотрудник", "Операция", "Изделие", "Кол-во", "Ставка", "Сумма"]
    df = pd.DataFrame(columns=columns)
    df.to_excel(path, index=False)

    return "<p>🗑 Журнал очищен.</p><a href='/operations-log'>↩ Назад</a>"


@app.route("/salary-report", methods=["GET", "POST"])
def salary_report():
    if "user" not in session:
        return redirect(url_for("login"))

    import pandas as pd
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    path = "logs/operations_log.xlsx"
    current_employee = session.get("employee", "").strip()

    if not os.path.exists(path):
        return "<p>📭 Лог операций отсутствует.</p><a href='/dashboard'>⬅ Назад</a>"

    df = pd.read_excel(path)
    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")

    if request.method == "POST":
        employee = request.form.get("employee").strip()
        period_str = request.form.get("period", "")
        if not employee or "," not in period_str:
            return "<p>❌ Заполните все поля.</p><a href='/salary-report'>⬅ Назад</a>"

        start_str, end_str = period_str.split(",")
        start_date = pd.to_datetime(start_str)
        end_date = pd.to_datetime(end_str)

        filtered = df[(df["Сотрудник"] == employee) & (df["Дата"] >= start_date) & (df["Дата"] <= end_date)]

        if filtered.empty:
            return "<p>📭 Нет данных за указанный период.</p><a href='/salary-report'>⬅ Назад</a>"

        total = round(filtered["Сумма"].sum(), 2)

        html = f"<h2>💰 Зарплата: {employee}</h2>"
        html += f"<p>Период: {start_str} — {end_str}</p>"
        html += "<table border='1' cellpadding='5'><tr>"
        for col in filtered.columns:
            html += f"<th>{col}</th>"
        html += "</tr>"
        for _, row in filtered.iterrows():
            html += "<tr>" + "".join([f"<td>{row[col]}</td>" for col in filtered.columns]) + "</tr>"
        html += f"</table><br><h3>Итого: {total} ₽</h3>"
        html += "<a href='/salary-report'>↩ Назад</a> | <a href='/dashboard'>🏠 В меню</a>"
        return html

    # --- Формирование списка сотрудников ---
    if current_employee == "админ":
        employees = df["Сотрудник"].dropna().unique().tolist()
        employee_select = "<label>Сотрудник:</label><br><select name='employee'>" + "".join(
            [f"<option value='{name}'>{name}</option>" for name in employees]
        ) + "</select><br><br>"
    else:
        employee_select = f"<input type='hidden' name='employee' value='{current_employee}'>"
        employee_select += f"<p><b>Сотрудник:</b> {current_employee}</p><br>"

    # --- Периоды ---
    periods = []
    min_date = df["Дата"].min().replace(day=1)
    max_date = df["Дата"].max()

    cur = min_date
    while cur <= max_date:
        mid = cur.replace(day=15)
        last = (cur + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
        periods.append((cur, mid))
        periods.append((mid + timedelta(days=1), last))
        cur += relativedelta(months=1)

    period_options = ""
    for start, end in periods:
        label = f"{start.strftime('%d.%m')} – {end.strftime('%d.%m.%Y')}"
        value = f"{start.date()},{end.date()}"
        period_options += f"<option value='{value}'>{label}</option>"

    return f'''
        <h2>🧮 Расчёт зарплаты</h2>
        <form method="post">
            {employee_select}
            <label>Период:</label><br>
            <select name="period">{period_options}</select><br><br>
            <button type="submit">Рассчитать</button>
        </form>
        <a href="/dashboard">⬅ Назад</a>
    '''



@app.route("/download-operations-log")
def download_operations_log():
    if "user" not in session:
        return redirect(url_for("login"))

    path = "logs/operations_log.xlsx"
    if not os.path.exists(path):
        return "<p>❌ Файл operations_log.xlsx не найден.</p><a href='/dashboard'>⬅ Назад</a>"

    from flask import send_file
    return send_file(path, as_attachment=True)

@app.route("/calculate-cost", methods=["GET", "POST"])
def calculate_cost_web():
    from logic.material_cost_calc import (
        load_all,
        trace_all_stages,
        collect_materials_for_stages,
        get_price,
    )

    product_df, semi_df, materials_df = load_all()

    # Определение только финальных изделий
    all_names = set(product_df["Название"].str.strip())
    used_as_component = set(product_df["Из чего состоит"].str.strip())
    used_in_semi = set(semi_df["Название"].str.strip())
    final_products = sorted(all_names - used_as_component - used_in_semi)

    if request.method == "POST":
        selected = request.form.get("product")
        if not selected:
            return "<p>❌ Не выбрано изделие.</p><a href='/calculate-cost'>↩ Назад</a>"

        stages = trace_all_stages(selected, product_df)
        materials = collect_materials_for_stages(stages, semi_df)

        html = f"<h2>🧾 Себестоимость: {selected}</h2>"
        html += "<table border='1' cellpadding='5'><tr><th>Материал</th><th>Кол-во</th><th>Цена</th><th>Сумма</th></tr>"
        total = 0
        for name in sorted(materials):
            qty = round(materials[name], 4)
            price = round(get_price(materials_df, name), 2)
            cost = round(qty * price, 2)
            total += cost
            html += f"<tr><td>{name}</td><td>{qty}</td><td>{price} ₽</td><td>{cost} ₽</td></tr>"
        html += f"<tr><td colspan='3' align='right'><b>ИТОГО</b></td><td><b>{round(total, 2)} ₽</b></td></tr>"
        html += "</table><br><a href='/dashboard'>⬅ В меню</a>"
        return html

    options_html = "".join([f"<option value='{name}'>{name}</option>" for name in final_products])
    return f'''
        <h2>📦 Расчёт себестоимости (только готовые изделия)</h2>
        <form method="post">
            <label>Выберите изделие:</label><br>
            <select name="product">{options_html}</select><br><br>
            <button type="submit">📊 Посчитать</button>
        </form>
        <a href="/dashboard">⬅ Назад</a>
    '''

@app.route("/labor-cost", methods=["GET", "POST"])
def labor_cost_web():
    if "user" not in session:
        return redirect(url_for("login"))

    if session.get("employee") != "админ":
        return "<p>⛔ Доступ только для администратора.</p><a href='/dashboard'>⬅ Назад</a>"

    from logic.material_cost_calc import trace_all_stages
    import pandas as pd

    product_df = pd.read_excel("data/product_recipes.xlsx")
    rates_df = pd.read_excel("data/operation_rates.xlsx").drop_duplicates(subset=["Название"])

    all_names = set(product_df["Название"].str.strip())
    used_as_component = set(product_df["Из чего состоит"].str.strip())
    final_products = sorted(all_names - used_as_component)

    if request.method == "POST":
        selected = request.form.get("product")
        if not selected:
            return "<p>❌ Не выбрано изделие.</p><a href='/labor-cost'>↩ Назад</a>"

        stages = trace_all_stages(selected, product_df)

        html = f"<h2>💼 Стоимость работ: {selected}</h2>"
        html += "<table border='1' cellpadding='5'><tr><th>Операция</th><th>Кол-во</th><th>Ставка</th><th>Сумма</th></tr>"
        total = 0

        for stage, qty in stages.items():
            row = rates_df[rates_df["Название"] == stage]
            if row.empty:
                continue
            rate = float(row.iloc[0]["Ставка (₽)"])
            cost = round(rate * qty, 2)
            total += cost
            html += f"<tr><td>{stage}</td><td>{qty:.2f}</td><td>{rate:.2f} ₽</td><td>{cost:.2f} ₽</td></tr>"

        html += f"<tr><td colspan='3' align='right'><b>ИТОГО</b></td><td><b>{round(total, 2)} ₽</b></td></tr>"
        html += "</table><br><a href='/dashboard'>⬅ Назад</a>"
        return html

    options_html = "".join([f"<option value='{name}'>{name}</option>" for name in final_products])
    return f'''
        <h2>📊 Себестоимость по работам (только готовые изделия)</h2>
        <form method="post">
            <label>Выберите изделие:</label><br>
            <select name="product">{options_html}</select><br><br>
            <button type="submit">Посчитать</button>
        </form>
        <a href="/dashboard'>⬅ Назад</a>
    '''


@app.route("/add-purchase", methods=["GET", "POST"])
def add_purchase():
    if "user" not in session:
        return redirect(url_for("login"))

    path = "data/purchases.xlsx"
    if os.path.exists(path):
        df = pd.read_excel(path)
    else:
        df = pd.DataFrame(columns=[
            "Дата", "Доставка ID", "Контрагент", "Материал", "Ед. изм.",
            "Кол-во упаковок", "Кол-во в упаковке", "Цена (за упаковку)",
            "Стоимость (общая)", "Стоимость доставки", "Комментарий",
            "Источник оплаты", "Категория расходов", "Вид расходов"
        ])

    contractors = sorted(df["Контрагент"].dropna().unique().tolist())
    materials = sorted(df["Материал"].dropna().unique().tolist())

    # значения по выбранному контрагенту
    selected_contractor = ""
    payment_sources = []
    expense_categories = []
    expense_types = []

    if request.method == "POST":
        mode = request.form.get("mode", "")
        selected_contractor = request.form.get("contractor") or ""
        new_contractor = request.form.get("new_contractor", "").strip()
        selected_contractor = new_contractor or selected_contractor

        if mode != "save":
            filtered_df = df[df["Контрагент"] == selected_contractor]
            materials = sorted(filtered_df["Материал"].dropna().unique().tolist())
            payment_sources = sorted(filtered_df["Источник оплаты"].dropna().unique().tolist())
            expense_categories = sorted(filtered_df["Категория расходов"].dropna().unique().tolist())
            expense_types = sorted(filtered_df["Вид расходов"].dropna().unique().tolist())

            return render_template("add_purchase.html",
                contractors=contractors,
                materials=materials,
                selected_contractor=selected_contractor,
                payment_sources=payment_sources,
                expense_categories=expense_categories,
                expense_types=expense_types
            )

        try:
            from datetime import datetime
            date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
            contractor = new_contractor or request.form.get("contractor")
            delivery_cost = float(request.form.get("delivery") or 0)

            payment_source = request.form.get("payment_source", "").strip()
            expense_category = request.form.get("expense_category", "").strip()
            expense_type = request.form.get("expense_type", "").strip()

            # Генерация нового Доставка ID
            existing_ids = df["Доставка ID"].dropna().astype(str).tolist()
            last_number = max([int(x[1:]) for x in existing_ids if x.startswith("D") and x[1:].isdigit()] + [0])
            delivery_id = f"D{last_number+1:04d}"

            rows = []
            index = 0
            while True:
                if f"material_{index}" not in request.form and f"new_material_{index}" not in request.form:
                    break

                material = request.form.get(f"new_material_{index}") or request.form.get(f"material_{index}")
                unit = request.form.get(f"unit_{index}", "шт")
                qty_packs = float(request.form.get(f"qty_packs_{index}") or 0)
                units_per_pack = float(request.form.get(f"units_per_pack_{index}") or 1)
                price_per_pack = float(request.form.get(f"price_per_pack_{index}") or 0)
                total_cost = float(request.form.get(f"total_cost_{index}") or 0)
                comment = request.form.get(f"comment_{index}", "")

                row = {
                    "Дата": date,
                    "Доставка ID": delivery_id,
                    "Контрагент": contractor,
                    "Материал": material,
                    "Ед. изм.": unit,
                    "Кол-во упаковок": qty_packs,
                    "Кол-во в упаковке": units_per_pack,
                    "Цена (за упаковку)": price_per_pack,
                    "Стоимость (общая)": total_cost,
                    "Стоимость доставки": "",
                    "Комментарий": comment,
                    "Источник оплаты": payment_source,
                    "Категория расходов": expense_category,
                    "Вид расходов": expense_type
                }
                rows.append(row)
                index += 1

            if delivery_cost and len(rows) > 0:
                rows[0]["Стоимость доставки"] = delivery_cost

            df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
            df.to_excel(path, index=False)

            return "<p style='color:green'>✅ Поставка добавлена.</p><a href='/add-purchase'>Добавить ещё</a> | <a href='/dashboard'>🏠 В меню</a>"

        except Exception as e:
            return f"<p>❌ Ошибка: {e}</p><a href='/add-purchase'>↩ Назад</a>"

    return render_template("add_purchase.html",
        contractors=contractors,
        materials=materials,
        selected_contractor=selected_contractor,
        payment_sources=[],
        expense_categories=[],
        expense_types=[]
    )

import os

import zipfile
from flask import send_file

@app.route("/download-all")
def download_all():
    zip_path = "data/all_data.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir("data"):
            full_path = os.path.join("data", file)
            if os.path.isfile(full_path):
                zipf.write(full_path, arcname=file)
    return send_file(zip_path, as_attachment=True)



# nothing else here — gunicorn handles app startup


from flask import send_from_directory, render_template_string

@app.route("/files")
def list_files():
    files = os.listdir("data")
    return render_template_string('''
        <h2>📁 Файлы в папке /data</h2>
        <ul>
        {% for f in files %}
            <li><a href="/download/{{ f }}">{{ f }}</a></li>
        {% endfor %}
        </ul>
        <br><a href='/dashboard'>⬅ Назад</a>
    ''', files=files)

@app.route("/download-all")
def download_all_files():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename in os.listdir("data"):
            file_path = os.path.join("data", filename)
            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=filename)
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        download_name='all_data.zip',
        as_attachment=True
    )


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory("data", filename, as_attachment=True)


@app.route("/debug-users")
def debug_users():
    import os, json
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.json")
    if not os.path.exists(users_path):
        return "<p>❌ Файл не найден</p>"
    with open(users_path, "r", encoding="utf-8") as f:
        return f"<pre>{json.dumps(json.load(f), ensure_ascii=False, indent=2)}</pre>"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


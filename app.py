import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

import zipfile
import io
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, session, url_for, send_file, flash
from logic.salary_logic import get_salary_table
from logic.stages_logic import register_operation_and_update_stock
from logic.materials_logic import update_average_prices

IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT") == "production"

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_local")
app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    users_path = os.path.join(BASE_DIR, "data", "users.json")
    if request.method == "POST":
        login_input = request.form.get("username")
        password_input = request.form.get("password")
        try:
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            return f"<b>Ошибка загрузки users.json:</b> {str(e)}"

        for u in users:
            if u["login"] == login_input and u["password"] == password_input:
                session["user"] = login_input
                session["employee"] = u["name"]
                return redirect(url_for("dashboard"))

        return "<b>Неверный логин или пароль</b>"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session.get("employee"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/add-purchase", methods=["GET", "POST"])
def add_purchase():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            from logic.materials_logic import add_purchase
            form_data = request.form.to_dict(flat=False)
            add_purchase(form_data)
            update_average_prices()
            flash("Поставка успешно добавлена", "success")
        except Exception as e:
            flash(f"Ошибка при сохранении: {str(e)}", "danger")
    return render_template("add_purchase.html")

@app.route("/get-salary", methods=["GET"])
def get_salary():
    if "user" not in session:
        return redirect(url_for("login"))
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return "Укажите период"
    try:
        df = get_salary_table(start, end)
        table_html = df.to_html(index=False)
        return render_template("salary_result.html", table_html=table_html, start=start, end=end)
    except Exception as e:
        return f"Ошибка: {str(e)}"

@app.route("/register-operation", methods=["POST"])
def register_operation():
    if "user" not in session:
        return redirect(url_for("login"))
    try:
        form_data = request.form
        register_operation_and_update_stock(form_data)
        flash("Операция зарегистрирована", "success")
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "danger")
    return redirect(url_for("dashboard"))

@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        return f"Файл {filename} не найден"
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=not IS_PRODUCTION, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
